
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
        # Match the skill as a whole term.
        if skill == "C":
            # Prevent C from matching inside C++, C#, etc.
            pattern = r"(?<![\w+#])C(?![\w+#])"

            for matched in re.finditer(pattern, text, re.IGNORECASE):
                start = matched.start()
                end = matched.end()

                # Check the words immediately around C.
                before = text[max(0, start - 40):start]
                after = text[end:min(len(text), end + 20)]

                # Ignore a C that clearly refers to a grade.
                if re.search(r"\bgrade\s*$", before, re.IGNORECASE):
                    continue

                # Require programming-related context nearby.
                context = before + " " + after

                if re.search(
                    r"\b(programming|programmer|language|languages|"
                    r"proficient|proficiency|skills?|developer|"
                    r"developed|coding|coded|using|use|know|knows|"
                    r"learned|learning|experience|experienced)\b",
                    context,
                    re.IGNORECASE,
                ):
                    found_skills.append("C")
                    break

        else:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(skill)

    return sorted(set(found_skills))




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
