import faiss
import numpy as np
import pickle
import os
import requests
from config import get_api_config, validate_config

# Validate and get configuration
validate_config()
config = get_api_config()


def get_embedding(text, config):
    """Get embedding for text using the configured API"""
    if config["api_type"] == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=config["api_key"])
        response = client.embeddings.create(input=text, model=config["embedding_model"])
        return response.data[0].embedding
    
    elif config["api_type"] == "ollama":
        # Ollama API call
        response = requests.post(
            f"{config['base_url']}/api/embeddings",
            json={"model": config["embedding_model"], "prompt": text}
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"Unknown API type: {config['api_type']}")


def get_chat_response(messages, config):
    """Get chat response using the configured API"""
    if config["api_type"] == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=config["api_key"])
        response = client.chat.completions.create(
            model=config["chat_model"],
            messages=messages
        )
        return response.choices[0].message.content
    
    elif config["api_type"] == "ollama":
        # Ollama API call
        # Convert messages to prompt format for Ollama
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
        
        response = requests.post(
            f"{config['base_url']}/api/generate",
            json={
                "model": config["chat_model"],
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"Unknown API type: {config['api_type']}")


def ask_question(question):
    # Check if vector files exist
    if not os.path.exists("vectors.index") or not os.path.exists("chunks.pkl"):
        print("❌ Error: Vector database not found!")
        print("🔧 Please run 'pdf_vector.py' first to create the database.")
        return None

    try:
        # Load saved data
        index = faiss.read_index("vectors.index")
        with open("chunks.pkl", "rb") as f:
            data = pickle.load(f)

        chunks = data['chunks']
        metadata = data['metadata']
        total_pages = data['total_pages']

        # Get question embedding
        query_embedding = get_embedding(question, config)
        query_vector = np.array(query_embedding).reshape(1, -1)

        # Search similar chunks
        scores, indices = index.search(query_vector.astype('float32'), 3)

        # Show similarity scores and page info for debugging
        print(f"🔍 Found {len(indices[0])} relevant chunks:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            page_num = metadata[idx]['estimated_page']
            print(f"   Chunk {i + 1}: Score {score:.3f} (≈Page {page_num})")

        # Build context with page information
        context_parts = []
        for idx in indices[0]:
            chunk_text = chunks[idx]
            page_num = metadata[idx]['estimated_page']
            context_parts.append(f"[Page {page_num}]: {chunk_text}")

        context = '\n\n'.join(context_parts)

        # Get answer using configured API
        messages = [
            {
                "role": "system",
                "content": f"You are answering questions about a {total_pages}-page document. When providing answers, mention page numbers when relevant."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}\n\nAnswer based on the context:"
            }
        ]
        
        answer = get_chat_response(messages, config)
        return answer

    except Exception as e:
        print(f"❌ Error processing question: {str(e)}")
        return None


def main():
    # Check if database exists
    if not os.path.exists("vectors.index") or not os.path.exists("chunks.pkl"):
        print("❌ Vector database not found!")
        print("🔧 Please run 'pdf_to_vectors.py' first to create the database.")
        print("📋 Steps:")
        print("   1. Run: python pdf_to_vectors.py")
        print("   2. Then run: python ask_questions.py")
        return

    # Load database info
    try:
        index = faiss.read_index("vectors.index")
        with open("chunks.pkl", "rb") as f:
            data = pickle.load(f)

        chunks = data['chunks']
        total_pages = data['total_pages']

        print(f"✅ Database loaded: {len(chunks)} chunks from {total_pages} pages")
    except Exception as e:
        print(f"❌ Error loading database: {str(e)}")
        return

    # Interactive question loop
    print("\n" + "=" * 60)
    print("🤖 RAG System Ready! Ask me questions about your PDF")
    print("💡 Type 'bye', 'quit', 'exit', or 'q' to exit")
    print("🔢 Type 'info' to see database statistics")
    print("=" * 60)

    while True:
        question = input("\n❓ Your question: ").strip()

        # Check for exit commands
        if question.lower() in ['bye', 'quit', 'exit', 'q']:
            print("👋 Goodbye! Thanks for using the RAG system!")
            break

        # Show database info
        if question.lower() == 'info':
            print(f"📊 Database Info:")
            print(f"   • Total pages: {total_pages}")
            print(f"   • Total chunks: {len(chunks)}")
            print(f"   • Vector dimensions: 1536")
            print(f"   • Average chunks per page: {len(chunks) / total_pages:.1f}")
            print(f"   • Sample chunk: {chunks[0][:100]}...")
            continue

        # Skip empty questions
        if not question:
            print("⚠️  Please enter a question!")
            continue

        print("🔍 Searching and generating answer...")
        answer = ask_question(question)

        if answer:
            print(f"🤖 Answer: {answer}")
        else:
            print("❌ Sorry, I couldn't generate an answer. Please try a different question.")


if __name__ == "__main__":
    main()