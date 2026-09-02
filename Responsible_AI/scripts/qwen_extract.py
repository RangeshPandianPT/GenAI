import requests
import json
import os

OLLAMA_URL = "http://localhost:11434/api/generate"

INPUT_FOLDER = "extracted_text"
OUTPUT_FOLDER = "json_data"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_resume(text, resume_id):

    prompt = f"""
You are a professional resume information extraction system.

Read the resume below and convert it into the EXACT JSON structure
provided below.

IMPORTANT RULES:
1. Return ONLY valid JSON.
2. Do not add any new fields.
3. Do not remove any fields.
4. If information is missing, use null or [].
5. Keep the resume_id exactly as "{resume_id}".

JSON STRUCTURE:

{{
    "resume_id": "{resume_id}",
    "personal_information": {{
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": ""
    }},
    "education": [
        {{
            "degree": "",
            "institution": "",
            "field": "",
            "year": ""
        }}
    ],
    "experience": [
        {{
            "company": "",
            "role": "",
            "start_date": "",
            "end_date": "",
            "responsibilities": []
        }}
    ],
    "skills": [
        {{
            "name": "",
            "category": ""
        }}
    ],
    "projects": [
        {{
            "name": "",
            "description": "",
            "technologies": []
        }}
    ],
    "certifications": [],
    "achievements": [],
    "summary": ""
}}

RESUME TEXT:
{text}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
    )

    response.raise_for_status()

    result = response.json()

    return json.loads(result["response"])


# Process all TXT files

for filename in os.listdir(INPUT_FOLDER):

    if filename.lower().endswith(".txt"):

        input_path = os.path.join(
            INPUT_FOLDER,
            filename
        )

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as file:
            text = file.read()

        resume_id = filename.rsplit(".", 1)[0].upper()

        print(f"\nProcessing {resume_id}...")

        try:

            data = extract_resume(
                text,
                resume_id
            )

            output_filename = resume_id + ".json"

            output_path = os.path.join(
                OUTPUT_FOLDER,
                output_filename
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print(f"Saved: {output_filename}")

        except Exception as e:

            print(
                f"ERROR processing {filename}: {e}"
            )


print("\nQwen processing completed!")