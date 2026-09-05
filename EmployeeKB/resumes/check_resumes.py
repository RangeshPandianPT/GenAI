import os

RESUME_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "resumes"
)

print("=" * 70)
print("CHECKING RESUME FILES")
print("=" * 70)

for filename in sorted(os.listdir(RESUME_FOLDER)):

    if filename.lower().endswith(".txt"):

        file_path = os.path.join(
            RESUME_FOLDER,
            filename
        )

        print("\n" + "=" * 70)
        print(f"FILE: {filename}")
        print("=" * 70)

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        print(repr(text[:500]))