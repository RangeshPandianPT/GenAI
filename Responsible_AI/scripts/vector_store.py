import chromadb
import json
import os

JSON_FOLDER = "json_data"
VECTOR_DB_FOLDER = "vector_db"

client = chromadb.PersistentClient(
    path=VECTOR_DB_FOLDER
)

collection = client.get_or_create_collection(
    name="resume_collection"
)

for filename in sorted(os.listdir(JSON_FOLDER)):

    if not filename.endswith(".json"):
        continue

    path = os.path.join(JSON_FOLDER, filename)

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    resume_id = str(data["resume_id"])
    summary = data.get("summary", "")

    skills = data.get("skills", [])
    projects = data.get("projects", [])
    experience = data.get("experience", [])

    text = f"""
Resume ID: {resume_id}

Summary:
{summary}

Skills:
{skills}

Projects:
{projects}

Experience:
{experience}
"""

    collection.upsert(
        ids=[resume_id],
        documents=[text],
        metadatas=[
            {
                "resume_id": resume_id,
                "source": filename
            }
        ]
    )

    print(f"Stored: {resume_id}")

print("Vector database created successfully")
print(f"Total documents: {collection.count()}")