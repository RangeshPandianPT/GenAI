import chromadb
from neo4j import GraphDatabase
import requests
import json

# =========================
# CONFIGURATION
# =========================

VECTOR_DB = "vector_db"
COLLECTION_NAME = "resume_collection"

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "Resume@123"
NEO4J_DATABASE = "resumedb"

OLLAMA_URL = "http://localhost:11434/api/generate"
QWEN_MODEL = "qwen2.5:7b"


# =========================
# VECTOR DATABASE
# =========================

chroma_client = chromadb.PersistentClient(
    path=VECTOR_DB
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# =========================
# NEO4J
# =========================

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# =========================
# GET NEO4J DATA
# =========================

def get_resume_from_neo4j(resume_id):

    query = """
    MATCH (r:Resume {resume_id: $resume_id})
    OPTIONAL MATCH (r)-[rel]->(n)
    RETURN properties(r) AS resume,
           collect({
               relationship: type(rel),
               node: properties(n)
           }) AS connections
    """

    with driver.session(database=NEO4J_DATABASE) as session:

        result = session.run(
            query,
            resume_id=str(resume_id)
        ).single()

        if not result:
            return None

        return {
            "resume": result["resume"],
            "connections": result["connections"]
        }


# =========================
# ASK QWEN
# =========================

def ask_qwen(question, context):

    prompt = f"""
You are a resume search assistant.

Answer the user's question using the resume information below.

USER QUESTION:
{question}

RESUME INFORMATION:
{context}

Instructions:
- Identify the relevant candidates.
- Mention their resume ID.
- Use the skills, education, projects and experience available.
- Do not invent information.
- Give a concise answer.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": QWEN_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


# =========================
# KNOWLEDGE BASE SEARCH
# =========================

def search_knowledge_base(question, top_k=3):

    print("\nSearching Vector Database...")

    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )

    resume_ids = results["ids"][0]
    documents = results["documents"][0]

    print("Relevant resumes:", resume_ids)

    context = []

    for i, resume_id in enumerate(resume_ids):

        neo4j_data = get_resume_from_neo4j(resume_id)

        context.append({
            "resume_id": resume_id,
            "vector_information": documents[i],
            "graph_information": neo4j_data
        })

    print("Retrieved data from Neo4j.")

    context_text = json.dumps(
        context,
        indent=2,
        default=str
    )

    answer = ask_qwen(
        question,
        context_text
    )

    return answer


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("Resume Knowledge Base")
    print("=====================")

    while True:

        question = input(
            "\nAsk a question (type 'exit' to quit): "
        )

        if question.lower() == "exit":
            break

        try:

            answer = search_knowledge_base(question)

            print("\nAnswer:")
            print(answer)

        except Exception as e:

            print("\nError:")
            print(e)

    driver.close()