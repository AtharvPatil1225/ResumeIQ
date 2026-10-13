from skill_extractor import extract_skills


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