import faiss
import openai
import numpy as np
import pickle
import os

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')  # Use environment variable


def ask_question(question):
    # Check if vector files exist
    if not os.path.exists("vectors.index") or not os.path.exists("chunks.pkl"):
        print("❌ Error: Vector database not found!")
        print("🔧 Please run 'pdf_to_vectors.py' first to create the database.")
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
        response = openai.Embedding.create(input=question, model="text-embedding-ada-002")
        query_vector = np.array(response['data'][0]['embedding']).reshape(1, -1)

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

        # Get answer from GPT with page context
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"You are answering questions about a {total_pages}-page document. When providing answers, mention page numbers when relevant."
            }, {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}\n\nAnswer based on the context:"
            }]
        )
        return response.choices[0].message.content

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