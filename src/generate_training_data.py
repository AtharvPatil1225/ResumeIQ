
from pathlib import Path
import pandas as pd


def main():
    project_folder = Path(__file__).resolve().parent.parent
    output_path = (
        project_folder
        / "data"
        / "training"
        / "resume_job_pairs_expanded.csv"
    )

    # Each role has one job description and three synthetic resume examples.
    role_examples = {
        "Data Analyst": {
            "job": (
                "Data Analyst required with Python, SQL, pandas, "
                "data cleaning, visualization and analytical skills."
            ),
            "strong": [
                "Python SQL pandas data cleaning visualization analytics project",
                "Data analyst project using Python pandas SQL and charts",
                "Python SQL data analysis dashboard and reporting experience",
                "Pandas data cleaning SQL queries and visualization project",
                "Python analytics project with SQL and data visualization",
            ],
            "partial": [
                "Python basics and one beginner data analysis project",
                "SQL queries and basic spreadsheet data analysis",
                "Python pandas basics with limited visualization experience",
                "College project involving Python and simple charts",
                "Basic SQL and introductory Python programming",
            ],
            "poor": [
                "Graphic design illustration and poster creation",
                "Video editing animation and photography projects",
                "Event management and public speaking activities",
                "Mechanical workshop and hardware assembly project",
                "Creative writing and social media content creation",
            ],
        },
        "Backend Developer": {
            "job": (
                "Backend Developer required with Java, OOP, SQL, "
                "REST APIs, database design and debugging."
            ),
            "strong": [
                "Java OOP SQL REST API and database development project",
                "Java backend application with SQL and API integration",
                "Object oriented Java programming and database design",
                "Java REST services SQL queries and debugging project",
                "Backend development using Java OOP and relational databases",
            ],
            "partial": [
                "Java basics and one small college programming project",
                "SQL database project with introductory Java knowledge",
                "Basic OOP concepts and simple Java programs",
                "Java coursework with limited database experience",
                "Introductory Java and SQL query practice",
            ],
            "poor": [
                "Graphic design and digital illustration portfolio",
                "Video editing and animation projects",
                "Marketing campaign and social media management",
                "Photography portfolio and creative writing",
                "Event coordination and public speaking activities",
            ],
        },
        "Frontend Developer": {
            "job": (
                "Frontend Developer required with HTML, CSS, JavaScript, "
                "React, responsive design and web development."
            ),
            "strong": [
                "HTML CSS JavaScript React responsive web application",
                "React frontend project using HTML CSS and JavaScript",
                "Responsive website built with React CSS and JavaScript",
                "Frontend development project with HTML CSS and React",
                "JavaScript React components and responsive web design",
            ],
            "partial": [
                "HTML CSS with basic JavaScript knowledge",
                "Static website project using HTML and CSS",
                "Basic JavaScript and introductory web development",
                "HTML CSS coursework and one simple website",
                "Beginner frontend project with limited React experience",
            ],
            "poor": [
                "Python data analysis and SQL reporting project",
                "Java backend database application",
                "Video editing and motion graphics portfolio",
                "Mechanical design and hardware workshop",
                "Accounting and financial record management",
            ],
        },
        "Machine Learning Intern": {
            "job": (
                "Machine Learning Intern required with Python, pandas, "
                "scikit-learn, statistics, model evaluation and ML projects."
            ),
            "strong": [
                "Python pandas scikit-learn classification model evaluation project",
                "Machine learning project using Python and scikit-learn",
                "Python data preprocessing model training and evaluation",
                "Pandas statistics and machine learning classification project",
                "Scikit-learn regression project with evaluation metrics",
            ],
            "partial": [
                "Python basics and introductory machine learning coursework",
                "Pandas basics and a small data analysis project",
                "Basic statistics and beginner Python programming",
                "College project exploring introductory machine learning",
                "Python programming with limited model evaluation experience",
            ],
            "poor": [
                "Graphic design and illustration portfolio",
                "Frontend website using HTML and CSS only",
                "Video editing and animation projects",
                "Event planning and public speaking",
                "Mechanical assembly and workshop activities",
            ],
        },
        "DevOps Intern": {
            "job": (
                "DevOps Intern required with Linux, Git, Docker, CI/CD, "
                "cloud fundamentals, scripting and automation."
            ),
            "strong": [
                "Linux Git Docker CI/CD pipeline and automation project",
                "Docker containers Git workflows and CI/CD configuration",
                "Linux scripting cloud fundamentals and automated deployment",
                "Git Docker and continuous integration project",
                "DevOps project using Linux containers and deployment automation",
            ],
            "partial": [
                "Basic Git commands and introductory Linux usage",
                "Linux basics and a small shell scripting exercise",
                "Git version control and introductory cloud coursework",
                "Docker basics with limited deployment experience",
                "Basic scripting and introductory DevOps concepts",
            ],
            "poor": [
                "Graphic design and poster creation",
                "Video editing and photography portfolio",
                "Data analysis using spreadsheets only",
                "Event management and communication activities",
                "Creative writing and social media content",
            ],
        },
        "Database Developer": {
            "job": (
                "Database Developer required with SQL, relational databases, "
                "database design, normalization, joins and query optimization."
            ),
            "strong": [
                "SQL relational database design normalization and joins project",
                "Database application using SQL joins and relational tables",
                "SQL queries normalization and database schema design",
                "Relational database project with query optimization",
                "SQL database management and structured query development",
            ],
            "partial": [
                "Basic SQL queries and a small database college project",
                "Introductory relational database concepts and SQL",
                "Simple database tables with basic query practice",
                "SQL coursework with limited normalization experience",
                "Basic joins and introductory database design",
            ],
            "poor": [
                "Graphic design illustration and poster creation",
                "Video editing and animation portfolio",
                "Frontend design using HTML and CSS",
                "Event management and public speaking",
                "Photography and creative writing projects",
            ],
        },
    }

    rows = []

    for role, examples in role_examples.items():
        for label, category in [
            (2, "strong"),
            (1, "partial"),
            (0, "poor"),
        ]:
            for resume_text in examples[category]:
                rows.append({
                    "resume_text": resume_text,
                    "job_description": examples["job"],
                    "match_label": label,
                })

    df = pd.DataFrame(rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Refuse to overwrite an existing dataset.
    if output_path.exists():
        print("Output file already exists. No file was overwritten.")
        print("File:", output_path)
        return

    df.to_csv(output_path, index=False, encoding="utf-8")

    print("Synthetic training dataset created successfully.")
    print("Output file:", output_path)
    print("Total examples:", len(df))
    print("\nExamples per label:")
    print(df["match_label"].value_counts().sort_index())
    print("\nExamples per job role:")
    print(df.groupby("job_description").size())
    print("\nDuplicate rows:", df.duplicated().sum())
    print(
        "\nReminder: These are synthetic examples for pipeline "
        "experimentation, not real-world validation."
    )


if __name__ == "__main__":
    main()
