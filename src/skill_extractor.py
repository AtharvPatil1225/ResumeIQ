
import re

# ---------------------------------------------------------------------------
# Skill taxonomy — grouped by category for maintainability.
# Each entry is the canonical display name; matching is case-insensitive.
# The "C" language is handled specially below to avoid false positives.
# ---------------------------------------------------------------------------

# Programming languages
_LANGUAGES = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
    "Go", "Rust", "Kotlin", "Swift", "R", "Scala", "MATLAB", "PHP",
    "Ruby", "Perl", "Shell", "Bash", "PowerShell", "Dart", "Lua",
]

# Web / frontend / backend frameworks
_WEB = [
    "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django",
    "Flask", "FastAPI", "Spring Boot", "Spring", "ASP.NET", ".NET",
    "Next.js", "Nuxt.js", "Laravel", "Symfony", "Ruby on Rails",
    "Svelte", "Bootstrap", "Tailwind CSS", "jQuery", "HTML", "CSS",
    "REST API", "GraphQL", "WebSocket",
]

# Machine learning, AI, and data science
_ML_AI = [
    "Machine Learning", "Deep Learning", "Natural Language Processing",
    "NLP", "Computer Vision", "Reinforcement Learning",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
    "Hugging Face", "OpenCV", "NLTK", "spaCy", "Gensim",
    "XGBoost", "LightGBM", "CatBoost", "Random Forest",
    "Logistic Regression", "Linear Regression", "SVM",
    "BERT", "GPT", "Transformer", "Word2Vec", "FastText",
    "MLflow", "Weights and Biases",
]

# Data engineering and analytics
_DATA = [
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly", "Power BI",
    "Tableau", "Excel", "SQL", "PySpark", "Apache Spark",
    "Hadoop", "Kafka", "Airflow", "dbt", "Snowflake",
    "Data Cleaning", "Data Analysis", "Data Visualization",
    "Statistics", "Probability",
]

# Cloud, DevOps, and infrastructure
_DEVOPS = [
    "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes",
    "Terraform", "Ansible", "Jenkins", "CI/CD", "GitHub Actions",
    "GitLab CI", "Linux", "Nginx", "Apache", "Prometheus",
    "Grafana", "ELK Stack", "Elasticsearch",
]

# Databases
_DATABASES = [
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "SQL Server",
    "Redis", "Cassandra", "DynamoDB", "Firebase", "Supabase",
    "Neo4j", "InfluxDB",
]

# Tools, IDEs, and version control
_TOOLS = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
    "VS Code", "IntelliJ", "PyCharm", "Eclipse", "Postman",
    "Jupyter", "Google Colab", "Linux", "Windows", "macOS",
]

# Mobile development
_MOBILE = [
    "Android", "iOS", "React Native", "Flutter", "Xamarin",
]

# Security and networking (brief subset)
_SECURITY = [
    "Cybersecurity", "Network Security", "Penetration Testing",
    "Cryptography", "OAuth", "JWT",
]

SKILLS = (
    _LANGUAGES + _WEB + _ML_AI + _DATA + _DEVOPS
    + _DATABASES + _TOOLS + _MOBILE + _SECURITY
)

# Remove duplicates while preserving order.
_seen: set = set()
SKILLS = [
    s for s in SKILLS
    if s.lower() not in _seen and not _seen.add(s.lower())  # type: ignore[func-returns-value]
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
