
from skill_extractor import extract_skills


test_cases = [
    "I know C and C++.",
    "I use GitHub for version control.",
    "I use Git for version control.",
    "My skills include Java and JavaScript.",
    "I have experience with Python, SQL, and React.",
    "I am learning HTML, CSS, and Node.js.",
]


print("ResumeIQ - Skill Matching Validation")
print("=" * 40)

for text in test_cases:
    print(f"\nInput: {text}")
    print("Detected:", extract_skills(text))
