import os
import re
import mysql.connector
from neo4j import GraphDatabase


MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Rangesh@07",
    "database": "employee_kg"
}

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password123"

RESUME_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "resumes"
)


def parse_resume(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    def extract(pattern):
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )

        if match:
            return match.group(1).strip()

        return ""

    employee_id = extract(
        r"Employee\s*ID\s*:\s*(.+)"
    )

    name = extract(
        r"Name\s*:\s*(.+)"
    )

    summary = extract(
        r"Professional\s*Summary\s*:\s*(.*?)(?=\n\s*Skills\s*:)"
    )

    skills = extract(
        r"Skills\s*:\s*(.*?)(?=\n\s*Projects\s*:)"
    )

    projects = extract(
        r"Projects\s*:\s*(.*?)(?=\n\s*Strengths\s*:)"
    )

    strengths = extract(
        r"Strengths\s*:\s*(.*?)(?=\n\s*Areas\s+for\s+Improvement\s*:)"
    )

    improvement = extract(
        r"Areas\s+for\s+Improvement\s*:\s*(.*?)(?=\n\s*Certifications\s*:)"
    )

    certifications = extract(
        r"Certifications\s*:\s*(.*?)(?=\n\s*Manager\s+Feedback\s*:)"
    )

    feedback = extract(
        r"Manager\s+Feedback\s*:\s*(.*?)(?=\n\s*Career\s+Goal\s*:)"
    )

    career_goal = extract(
        r"Career\s+Goal\s*:\s*(.*)"
    )

    return {
        "employee_id": employee_id,
        "name": name,
        "summary": summary,
        "skills": skills,
        "projects": projects,
        "strengths": strengths,
        "improvement": improvement,
        "certifications": certifications,
        "feedback": feedback,
        "career_goal": career_goal
    }


# =========================================================
# CONNECT TO MYSQL
# =========================================================

def get_mysql_data():

    print("\nConnecting to MySQL...")

    connection = mysql.connector.connect(**MYSQL_CONFIG)

    cursor = connection.cursor(dictionary=True)

    # -----------------------------------------------------
    # EMPLOYEES
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            employee_id,
            company_id,
            department_id,
            salary,
            designation,
            joining_date
        FROM Employee
    """)

    employees = cursor.fetchall()

    # -----------------------------------------------------
    # COMPANIES
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            company_id,
            company_name,
            address,
            city,
            state,
            country,
            industry,
            revenue_crore
        FROM Company
    """)

    companies = cursor.fetchall()

    # -----------------------------------------------------
    # DEPARTMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            department_id,
            department_name
        FROM Department
    """)

    departments = cursor.fetchall()

    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            performance_id,
            employee_id,
            review_year,
            technical_score,
            communication_score,
            leadership_score,
            teamwork_score,
            productivity_score,
            quality_score,
            overall_score
        FROM Performance
    """)

    performances = cursor.fetchall()

    cursor.close()
    connection.close()

    print(f"Employees loaded: {len(employees)}")
    print(f"Companies loaded: {len(companies)}")
    print(f"Departments loaded: {len(departments)}")
    print(f"Performance records loaded: {len(performances)}")

    return employees, companies, departments, performances


# =========================================================
# CREATE NEO4J GRAPH
# =========================================================

def create_graph(
    employees,
    companies,
    departments,
    performances,
    resumes
):

    print("\nConnecting to Neo4j...")

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )

    try:

        with driver.session() as session:

            # -------------------------------------------------
            # CLEAR OLD GRAPH
            # -------------------------------------------------

            print("Clearing existing graph...")

            session.run("""
                MATCH (n)
                DETACH DELETE n
            """)

            # -------------------------------------------------
            # CREATE COMPANY NODES
            # -------------------------------------------------

            print("Creating company nodes...")

            for company in companies:

                session.run("""
                    CREATE (c:Company {
                        company_id: $company_id,
                        name: $company_name,
                        address: $address,
                        city: $city,
                        state: $state,
                        country: $country,
                        industry: $industry,
                        revenue_crore: $revenue
                    })
                """,
                    company_id=company["company_id"],
                    company_name=company["company_name"],
                    address=company["address"],
                    city=company["city"],
                    state=company["state"],
                    country=company["country"],
                    industry=company["industry"],
                    revenue=float(company["revenue_crore"])
                )

            # -------------------------------------------------
            # CREATE DEPARTMENT NODES
            # -------------------------------------------------

            print("Creating department nodes...")

            for department in departments:

                session.run("""
                    CREATE (d:Department {
                        department_id: $department_id,
                        name: $department_name
                    })
                """,
                    department_id=department["department_id"],
                    department_name=department["department_name"]
                )

            # -------------------------------------------------
            # CREATE EMPLOYEE NODES
            # -------------------------------------------------

            print("Creating employee nodes...")

            for employee in employees:

                session.run("""
                    CREATE (e:Employee {
                        employee_id: $employee_id,
                        salary: $salary,
                        designation: $designation,
                        joining_date: $joining_date
                    })
                """,
                    employee_id=employee["employee_id"],
                    salary=float(employee["salary"]),
                    designation=employee["designation"],
                    joining_date=str(employee["joining_date"])
                )

            # -------------------------------------------------
            # EMPLOYEE → COMPANY
            # -------------------------------------------------

            print("Connecting employees to companies...")

            for employee in employees:

                session.run("""
                    MATCH (e:Employee {
                        employee_id: $employee_id
                    })

                    MATCH (c:Company {
                        company_id: $company_id
                    })

                    MERGE (e)-[:WORKS_AT]->(c)
                """,
                    employee_id=employee["employee_id"],
                    company_id=employee["company_id"]
                )

            # -------------------------------------------------
            # EMPLOYEE → DEPARTMENT
            # -------------------------------------------------

            print("Connecting employees to departments...")

            for employee in employees:

                session.run("""
                    MATCH (e:Employee {
                        employee_id: $employee_id
                    })

                    MATCH (d:Department {
                        department_id: $department_id
                    })

                    MERGE (e)-[:BELONGS_TO]->(d)
                """,
                    employee_id=employee["employee_id"],
                    department_id=employee["department_id"]
                )

            # -------------------------------------------------
            # PERFORMANCE NODES
            # -------------------------------------------------

            print("Creating performance nodes...")

            for performance in performances:

                session.run("""
                    MATCH (e:Employee {
                        employee_id: $employee_id
                    })

                    CREATE (p:Performance {
                        performance_id: $performance_id,
                        review_year: $review_year,
                        technical_score: $technical_score,
                        communication_score: $communication_score,
                        leadership_score: $leadership_score,
                        teamwork_score: $teamwork_score,
                        productivity_score: $productivity_score,
                        quality_score: $quality_score,
                        overall_score: $overall_score
                    })

                    CREATE (e)-[:HAS_PERFORMANCE]->(p)
                """,
                    performance_id=performance["performance_id"],
                    employee_id=performance["employee_id"],
                    review_year=int(performance["review_year"]),
                    technical_score=float(performance["technical_score"]),
                    communication_score=float(performance["communication_score"]),
                    leadership_score=float(performance["leadership_score"]),
                    teamwork_score=float(performance["teamwork_score"]),
                    productivity_score=float(performance["productivity_score"]),
                    quality_score=float(performance["quality_score"]),
                    overall_score=float(performance["overall_score"])
                )

            # -------------------------------------------------
            # UNSTRUCTURED DATA
            # -------------------------------------------------

            print("Creating unstructured-data nodes...")

            for resume in resumes:

                employee_id = resume["employee_id"]

                # Skip invalid resume files
                if not employee_id:
                    print(
                        "WARNING: Skipping resume with missing employee ID"
                    )
                    continue

                # -------------------------------------------------
                # PERSON NODE
                # -------------------------------------------------

                session.run("""
                    MATCH (e:Employee {
                        employee_id: $employee_id
                    })

                    CREATE (p:Person {
                        name: $name,
                        summary: $summary,
                        strengths: $strengths,
                        improvement: $improvement,
                        career_goal: $career_goal
                    })

                    CREATE (e)-[:IDENTIFIED_AS]->(p)
                """,
                    employee_id=employee_id,
                    name=resume["name"],
                    summary=resume["summary"],
                    strengths=resume["strengths"],
                    improvement=resume["improvement"],
                    career_goal=resume["career_goal"]
                )

                # -------------------------------------------------
                # RESUME NODE
                # -------------------------------------------------

                session.run("""
                    MATCH (e:Employee {
                        employee_id: $employee_id
                    })

                    CREATE (r:Resume {
                        employee_id: $employee_id
                    })

                    CREATE (e)-[:HAS_RESUME]->(r)
                """,
                    employee_id=employee_id
                )

                # -------------------------------------------------
                # SKILLS
                # -------------------------------------------------

                skills = [
                    skill.strip()
                    for skill in resume["skills"].split(",")
                    if skill.strip()
                ]

                for skill in skills:

                    session.run("""
                        MATCH (r:Resume {
                            employee_id: $employee_id
                        })

                        MERGE (s:Skill {
                            name: $skill
                        })

                        MERGE (r)-[:MENTIONS_SKILL]->(s)
                    """,
                        employee_id=employee_id,
                        skill=skill
                    )

                # -------------------------------------------------
                # PROJECTS
                # -------------------------------------------------

                projects = [
                    project.strip()
                    for project in resume["projects"].split("\n")
                    if project.strip()
                ]

                for project in projects:

                    session.run("""
                        MATCH (r:Resume {
                            employee_id: $employee_id
                        })

                        MERGE (p:Project {
                            name: $project
                        })

                        MERGE (r)-[:MENTIONS_PROJECT]->(p)
                    """,
                        employee_id=employee_id,
                        project=project
                    )

                # -------------------------------------------------
                # CERTIFICATION
                # -------------------------------------------------

                if resume["certifications"]:

                    session.run("""
                        MATCH (r:Resume {
                            employee_id: $employee_id
                        })

                        MERGE (c:Certification {
                            name: $certification
                        })

                        MERGE (r)-[:HAS_CERTIFICATION]->(c)
                    """,
                        employee_id=employee_id,
                        certification=resume["certifications"]
                    )

                # -------------------------------------------------
                # FEEDBACK
                # -------------------------------------------------

                if resume["feedback"]:

                    session.run("""
                        MATCH (r:Resume {
                            employee_id: $employee_id
                        })

                        CREATE (f:Feedback {
                            text: $feedback
                        })

                        CREATE (r)-[:HAS_FEEDBACK]->(f)
                    """,
                        employee_id=employee_id,
                        feedback=resume["feedback"]
                    )

    finally:
        driver.close()

    print("\nNeo4j graph creation completed!")


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():

    print("=" * 60)
    print("EMPLOYEE KNOWLEDGE GRAPH ETL")
    print("=" * 60)

    # -----------------------------------------------------
    # LOAD STRUCTURED DATA
    # -----------------------------------------------------

    employees, companies, departments, performances = get_mysql_data()

    # -----------------------------------------------------
    # LOAD UNSTRUCTURED DATA
    # -----------------------------------------------------

    print("\nReading unstructured employee files...")

    resumes = []

    for filename in sorted(os.listdir(RESUME_FOLDER)):

        if filename.lower().endswith(".txt"):

            file_path = os.path.join(
                RESUME_FOLDER,
                filename
            )

            resume = parse_resume(file_path)

            resumes.append(resume)

            print(
                f"Loaded {filename}: "
                f"{resume['employee_id']} - "
                f"{resume['name']}"
            )

    print(
        f"\nUnstructured files loaded: {len(resumes)}"
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    valid_resumes = [
        resume
        for resume in resumes
        if resume["employee_id"] and resume["name"]
    ]

    print(
        f"Valid resumes: {len(valid_resumes)}"
    )

    if len(valid_resumes) != len(resumes):

        print(
            "\nWARNING: Some resume files could not be parsed."
        )

        print(
            "Please check the TXT file formatting before "
            "continuing."
        )

        return

    # -----------------------------------------------------
    # CREATE NEO4J GRAPH
    # -----------------------------------------------------

    create_graph(
        employees,
        companies,
        departments,
        performances,
        resumes
    )

    # -----------------------------------------------------
    # COMPLETION
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("ETL COMPLETED SUCCESSFULLY")
    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()