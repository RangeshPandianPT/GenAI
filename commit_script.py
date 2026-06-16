import os
import subprocess

repo_dir = r"d:\Projects\GenAI"
os.chdir(repo_dir)

target_file = r"Rag Model\backend.py"

# Get original content from git
result = subprocess.run(['git', 'show', 'HEAD:Rag Model/backend.py'], capture_output=True, text=True, encoding='utf-8')
content = result.stdout.replace('\r\n', '\n')

# Step 1: Update check_status
target1 = """                "success": True,
                "database_exists": True,
                "total_chunks": len(data['chunks']),
                "total_pages": data['total_pages']"""
repl1 = """                "success": True,
                "database_exists": True,
                "total_chunks": len(data['chunks']),
                "total_pages": data.get('total_pages', 0),
                "files": data.get('files', [])"""
content = content.replace(target1, repl1)

with open(target_file, "w", encoding="utf-8", newline='\n') as f:
    f.write(content)
os.system('git add "Rag Model/backend.py"')
os.system('git commit -m "feat(rag): update check_status to include files and robust total_pages"')

# Step 2: Chunking division by zero protection
target2 = """        # Create chunks
        chunks = []
        chunk_metadata = []
        
        for i in range(0, len(text), 400):
            chunk_text = text[i:i + 500]
            chunks.append(chunk_text)
            
            estimated_page = min((i // (len(text) // total_pages)) + 1, total_pages)
            chunk_metadata.append({
                'start_pos': i,
                'estimated_page': estimated_page
            })"""
repl2 = """        # Create chunks
        new_chunks = []
        new_chunk_metadata = []
        
        # Prevent division by zero
        text_len = len(text)
        chars_per_page = max(text_len // max(total_pages, 1), 1)
        
        for i in range(0, text_len, 400):
            chunk_text = text[i:i + 500]
            new_chunks.append(chunk_text)
            
            estimated_page = min((i // chars_per_page) + 1, total_pages)
            new_chunk_metadata.append({
                'start_pos': i,
                'estimated_page': estimated_page,
                'filename': filename
            })"""
content = content.replace(target2, repl2)

target2_b = """        # Get embeddings
        embeddings = []
        for chunk in chunks:"""
repl2_b = """        # Get embeddings
        embeddings = []
        for chunk in new_chunks:"""
content = content.replace(target2_b, repl2_b)

target2_c = """        return jsonify({
            "success": True,
            "message": "PDF processed successfully",
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "filename": filename
        })"""
repl2_c = """        return jsonify({
            "success": True,
            "message": "PDF processed successfully",
            "total_pages": total_pages,
            "total_chunks": len(new_chunks),
            "filename": filename
        })"""
content = content.replace(target2_c, repl2_c)

with open(target_file, "w", encoding="utf-8", newline='\n') as f:
    f.write(content)
os.system('git add "Rag Model/backend.py"')
os.system('git commit -m "fix(rag): prevent division by zero and track filename in chunks"')

# Step 3: FAISS Appending
target3 = """        # Create FAISS index
        embeddings = np.array(embeddings)
        embedding_dim = config["embedding_dim"]
        index = faiss.IndexFlatIP(embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # Save to files
        faiss.write_index(index, "vectors.index")
        with open("chunks.pkl", "wb") as f:
            pickle.dump({
                'chunks': chunks,
                'metadata': chunk_metadata,
                'total_pages': total_pages
            }, f)"""
repl3 = """        embeddings = np.array(embeddings)
        
        # Check if database exists to append
        if os.path.exists("vectors.index") and os.path.exists("chunks.pkl"):
            index = faiss.read_index("vectors.index")
            with open("chunks.pkl", "rb") as f:
                existing_data = pickle.load(f)
            
            chunks = existing_data['chunks'] + new_chunks
            chunk_metadata = existing_data['metadata'] + new_chunk_metadata
            total_pages_all = existing_data.get('total_pages', 0) + total_pages
            files = existing_data.get('files', [])
            if filename not in files:
                files.append(filename)
        else:
            embedding_dim = config["embedding_dim"]
            index = faiss.IndexFlatIP(embedding_dim)
            chunks = new_chunks
            chunk_metadata = new_chunk_metadata
            total_pages_all = total_pages
            files = [filename]
            
        index.add(embeddings.astype('float32'))
        
        # Save to files
        faiss.write_index(index, "vectors.index")
        with open("chunks.pkl", "wb") as f:
            pickle.dump({
                'chunks': chunks,
                'metadata': chunk_metadata,
                'total_pages': total_pages_all,
                'files': files
            }, f)"""
content = content.replace(target3, repl3)

with open(target_file, "w", encoding="utf-8", newline='\n') as f:
    f.write(content)
os.system('git add "Rag Model/backend.py"')
os.system('git commit -m "feat(rag): support appending multiple PDFs to vector index"')

# Step 4: Ask Question Context Attribution
target4 = """        for score, idx in zip(scores[0], indices[0]):
            chunk_text = chunks[idx]
            page_num = metadata[idx]['estimated_page']
            context_parts.append(f"[Page {page_num}]: {chunk_text}")
            relevant_chunks.append({
                "text": chunk_text[:200] + "...",
                "page": page_num,
                "score": float(score)
            })"""
repl4 = """        for score, idx in zip(scores[0], indices[0]):
            chunk_text = chunks[idx]
            page_num = metadata[idx].get('estimated_page', 1)
            doc_name = metadata[idx].get('filename', 'Unknown Document')
            context_parts.append(f"[File: {doc_name}, Page: {page_num}]: {chunk_text}")
            relevant_chunks.append({
                "text": chunk_text[:200] + "...",
                "page": page_num,
                "document": doc_name,
                "score": float(score)
            })"""
content = content.replace(target4, repl4)

with open(target_file, "w", encoding="utf-8", newline='\n') as f:
    f.write(content)
os.system('git add "Rag Model/backend.py"')
os.system('git commit -m "feat(rag): add document attribution to search context"')

# Step 5: Documents Endpoint
target5 = """@app.route('/api/clear', methods=['POST'])"""
repl5 = """@app.route('/api/documents', methods=['GET'])
def list_documents():
    \"\"\"List all uploaded documents in the vector database\"\"\"
    if os.path.exists("chunks.pkl"):
        try:
            with open("chunks.pkl", "rb") as f:
                data = pickle.load(f)
            return jsonify({
                "success": True,
                "files": data.get('files', [])
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    return jsonify({"success": True, "files": []})


@app.route('/api/clear', methods=['POST'])"""
content = content.replace(target5, repl5)

with open(target_file, "w", encoding="utf-8", newline='\n') as f:
    f.write(content)
os.system('git add "Rag Model/backend.py"')
os.system('git commit -m "feat(rag): add /api/documents endpoint to list files"')

# Push to github
print("Pushing to github...")
os.system('git push origin main')
