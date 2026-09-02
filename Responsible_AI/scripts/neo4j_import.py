from neo4j import GraphDatabase
import json
import os

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "password123"
DATABASE = "neo4j"

JSON_FOLDER = "json_data"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def load_resume(data):
    resume_id = data.get("resume_id")

    with driver.session(database=DATABASE) as session:

        session.run(
            """
            MERGE (r:Resume {resume_id: $resume_id})
            SET r.summary = $summary
            """,
            resume_id=resume_id,
            summary=data.get("summary", "")
        )

        personal = data.get("personal_information", {})
        name = personal.get("name")

        if name:
            session.run(
                """
                MATCH (r:Resume {resume_id: $resume_id})
                MERGE (p:Person {name: $name})
                SET p.email = $email,
                    p.phone = $phone,
                    p.location = $location,
                    p.linkedin = $linkedin
                MERGE (p)-[:HAS_RESUME]->(r)
                """,
                resume_id=resume_id,
                name=name,
                email=personal.get("email"),
                phone=personal.get("phone"),
                location=personal.get("location"),
                linkedin=personal.get("linkedin")
            )

        for edu in data.get("education", []):
            session.run(
                """
                MATCH (r:Resume {resume_id: $resume_id})
                MERGE (e:Education {
                    degree: $degree,
                    institution: $institution,
                    field: $field,
                    year: $year
                })
                MERGE (r)-[:HAS_EDUCATION]->(e)
                """,
                resume_id=resume_id,
                degree=edu.get("degree") or "",
                institution=edu.get("institution") or "",
                field=edu.get("field") or "",
                year=str(edu.get("year") or "")
            )

        for skill in data.get("skills", []):
            if isinstance(skill, dict):
                name = skill.get("name") or ""
                category = skill.get("category") or ""
            else:
                name = str(skill)
                category = ""

            if name:
                session.run(
                    """
                    MATCH (r:Resume {resume_id: $resume_id})
                    MERGE (s:Skill {name: $name})
                    SET s.category = $category
                    MERGE (r)-[:HAS_SKILL]->(s)
                    """,
                    resume_id=resume_id,
                    name=name,
                    category=category
                )

        for exp in data.get("experience", []):
            company = exp.get("company") or ""

            if company:
                session.run(
                    """
                    MATCH (r:Resume {resume_id: $resume_id})
                    MERGE (c:Company {name: $company})
                    MERGE (r)-[w:WORKED_AT]->(c)
                    SET w.role = $role,
                        w.start_date = $start_date,
                        w.end_date = $end_date,
                        w.responsibilities = $responsibilities
                    """,
                    resume_id=resume_id,
                    company=company,
                    role=exp.get("role") or "",
                    start_date=exp.get("start_date") or "",
                    end_date=exp.get("end_date") or "",
                    responsibilities=exp.get("responsibilities", [])
                )

        for project in data.get("projects", []):
            name = project.get("name") or ""

            if name:
                session.run(
                    """
                    MATCH (r:Resume {resume_id: $resume_id})
                    MERGE (p:Project {name: $name})
                    SET p.description = $description,
                        p.technologies = $technologies
                    MERGE (r)-[:HAS_PROJECT]->(p)
                    """,
                    resume_id=resume_id,
                    name=name,
                    description=project.get("description") or "",
                    technologies=project.get("technologies", [])
                )

        for cert in data.get("certifications", []):
            if cert:
                session.run(
                    """
                    MATCH (r:Resume {resume_id: $resume_id})
                    MERGE (c:Certification {name: $name})
                    MERGE (r)-[:HAS_CERTIFICATION]->(c)
                    """,
                    resume_id=resume_id,
                    name=str(cert)
                )

        for achievement in data.get("achievements", []):
            if achievement:
                session.run(
                    """
                    MATCH (r:Resume {resume_id: $resume_id})
                    MERGE (a:Achievement {description: $description})
                    MERGE (r)-[:HAS_ACHIEVEMENT]->(a)
                    """,
                    resume_id=resume_id,
                    description=str(achievement)
                )

def main():
    with driver.session(database=DATABASE) as session:
        session.run(
            """
            CREATE CONSTRAINT resume_id_unique IF NOT EXISTS
            FOR (r:Resume)
            REQUIRE r.resume_id IS UNIQUE
            """
        )

    files = [
        f for f in os.listdir(JSON_FOLDER)
        if f.endswith(".json")
    ]

    print(f"Found {len(files)} JSON files")

    for filename in sorted(files):
        path = os.path.join(JSON_FOLDER, filename)

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        load_resume(data)
        print(f"Loaded {data.get('resume_id')}")

    print("All resumes loaded")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.close()