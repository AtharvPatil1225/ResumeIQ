
import re

SKILLS = [
    "Machine Learning",
    "Deep Learning",
    "Data Science",
    "Scikit-learn",
    "JavaScript",
    "TypeScript",
    "Node.js",
    "TensorFlow",
    "PyTorch",
    "Kubernetes",
    "MongoDB",
    "PostgreSQL",
    "Java",
    "Python",
    "C++",
    "C#",
    "C",
    "SQL",
    "HTML",
    "CSS",
    "React",
    "Pandas",
    "NumPy",
    "FastAPI",
    "Flask",
    "GitHub",
    "Git",
    "AWS",
    "Docker",
    "MySQL",
]



def extract_skills(text):
    """Detect known skills using whole-term matching."""
    found_skills = []

    for skill in sorted(SKILLS, key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        # C is a single-letter skill, so match uppercase C only.
        # Case-insensitive matching would also match ordinary lowercase c.
        if skill == "C":
            matched = re.search(pattern, text)
        else:
            matched = re.search(pattern, text, re.IGNORECASE)

        if matched:
            found_skills.append(skill)

    return sorted(found_skills)



if __name__ == "__main__":
    examples = [
        "I know C, C++, Python, and Java.",
        "I use GitHub for my projects.",
        "My skills include JavaScript, React, and SQL.",
        "I have experience with Machine Learning and AWS.",
        "I know HTML, CSS, Node.js, and MongoDB.",
    ]

    print("ResumeIQ - Skill Extraction Test")
    print("-" * 35)

    for example in examples:
        print("\nExample:", example)
        print("Detected skills:", extract_skills(example))
