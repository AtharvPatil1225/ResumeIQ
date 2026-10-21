from skill_extractor import extract_skills, SKILLS


# --- Original test cases (preserved exactly) ---
test_cases = [
    ("I know C and C++.", {"C", "C++"}),
    ("I received a grade C in the exam.", set()),
    ("I use GitHub for version control.", {"GitHub"}),
    ("I use Git for version control.", {"Git"}),
    ("My skills include Java and JavaScript.", {"Java", "JavaScript"}),
    (
        "I have experience with Python, SQL, and React.",
        {"Python", "SQL", "React"},
    ),
    (
        "I am learning HTML, CSS, and Node.js.",
        {"HTML", "CSS", "Node.js"},
    ),
    ("The letter c appears in this sentence.", set()),
    ("I received a grade C in programming class.", set()),
    ("My programming skills include C and Python.", {"C", "Python"}),
    ("I use C++ for competitive programming.", {"C++"}),
    ("I know JavaScript but have never used Java.", {"Java", "JavaScript"}),
]


def test_extract_skills():
    for text, expected in test_cases:
        actual = set(extract_skills(text))
        assert actual == expected, (
            f"\nInput: {text}"
            f"\nExpected: {sorted(expected)}"
            f"\nActual: {sorted(actual)}"
        )


def test_ml_skills_detected():
    text = "Worked with TensorFlow, PyTorch, and Scikit-learn for ML projects."
    skills = set(extract_skills(text))
    assert "TensorFlow" in skills
    assert "PyTorch" in skills
    assert "Scikit-learn" in skills


def test_cloud_devops_detected():
    text = "Deployed services on AWS and Azure using Docker and Kubernetes."
    skills = set(extract_skills(text))
    assert "AWS" in skills
    assert "Azure" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills


def test_database_skills_detected():
    text = "Used PostgreSQL, MongoDB, and Redis in production."
    skills = set(extract_skills(text))
    assert "PostgreSQL" in skills
    assert "MongoDB" in skills
    assert "Redis" in skills


def test_web_framework_skills_detected():
    text = "Built APIs with Flask and FastAPI, frontend with React and Angular."
    skills = set(extract_skills(text))
    assert "Flask" in skills
    assert "FastAPI" in skills
    assert "React" in skills
    assert "Angular" in skills


def test_data_skills_detected():
    text = "Data analysis using Pandas, NumPy, and Matplotlib."
    skills = set(extract_skills(text))
    assert "Pandas" in skills
    assert "NumPy" in skills
    assert "Matplotlib" in skills


def test_no_duplicate_skills():
    text = "Python Python Python SQL SQL"
    skills = extract_skills(text)
    assert skills == sorted(set(skills))


def test_skills_list_has_no_internal_duplicates():
    seen = set()
    for skill in SKILLS:
        lower = skill.lower()
        assert lower not in seen, f"Duplicate skill in taxonomy: {skill!r}"
        seen.add(lower)


def test_empty_text_returns_empty_list():
    assert extract_skills("") == []
    assert extract_skills("   ") == []
