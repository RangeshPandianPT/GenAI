import faiss
import PyPDF2
import numpy as np
import pickle
import os
import requests
from config import get_api_config, validate_config, get_embedding_dimension

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


def pdf_to_vectors(pdf_path):
    # Read PDF
    print(f"📄 Reading PDF: {pdf_path}")
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        total_pages = len(pdf_reader.pages)

        # Extract text from each page separately
        page_texts = []
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            page_texts.append({
                'text': page_text,
                'page_number': page_num + 1
            })

        # Combine all text for chunking
        text = ''.join([p['text'] for p in page_texts])

    print(f"📊 Total pages: {total_pages}")
    print(f"📊 Total text length: {len(text):,} characters")
    print(f"📊 Average characters per page: {len(text) // total_pages:,}")

    # Create chunks with page tracking
    chunks = []
    chunk_metadata = []

    for i in range(0, len(text), 400):
        chunk_text = text[i:i + 500]
        chunks.append(chunk_text)

        # Estimate which page this chunk belongs to
        estimated_page = min((i // (len(text) // total_pages)) + 1, total_pages)
        chunk_metadata.append({
            'start_pos': i,
            'estimated_page': estimated_page
        })

    print(f"✂️  Created {len(chunks)} chunks")

    # Get embeddings using configured API
    print(f"🔄 Getting embeddings using {config['api_type'].upper()} API...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"Processing {i + 1}/{len(chunks)}")
        embedding = get_embedding(chunk, config)
        embeddings.append(embedding)

    # Create FAISS index
    print("🗂️  Creating FAISS index...")
    embeddings = np.array(embeddings)
    embedding_dim = config["embedding_dim"]
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings.astype('float32'))

    # Save to files
    print("💾 Saving to files...")
    faiss.write_index(index, "vectors.index")
    with open("chunks.pkl", "wb") as f:
        pickle.dump({
            'chunks': chunks,
            'metadata': chunk_metadata,
            'total_pages': total_pages
        }, f)

    print("✅ Vector database created successfully!")
    print(f"📁 Files saved: vectors.index, chunks.pkl")
    print(f"📊 Vector shape: {embeddings.shape}")
    print(f"🔢 Sample vector (first 5 dims): {embeddings[0][:5]}")

    return embeddings, chunks


# Usage
if __name__ == "__main__":
    # Convert PDF to vectors (run this once)
    pdf_file = r"d:\GenAI\Rag Model\RangeshPandian_Resume.pdf.pdf"  # Change to your PDF file
    embeddings, chunks = pdf_to_vectors(pdf_file)

    print("\n🎉 Setup complete! Now you can run 'ask_questions.py' to chat with your PDF!")