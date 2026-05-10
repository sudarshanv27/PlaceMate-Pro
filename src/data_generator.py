import pandas as pd
import numpy as np

np.random.seed(42)
records = 10000

student_names = [f"Student_{i}" for i in range(1, records+1)]

data = {
    "Student-name": student_names,
    "student_id": [f"STU{100000+i}" for i in range(records)],
    "cgpa": np.round(np.random.uniform(5.0, 10.0, records), 2),
    "coding_skill": np.random.randint(1, 11, records),
    "communication_skill": np.random.randint(1, 11, records),
    "aptitude_skill": np.random.randint(1, 11, records),
    "problem_solving": np.random.randint(1, 11, records),
    "projects_count": np.random.randint(0, 7, records),
    "internship_count": np.random.randint(0, 5, records),
    "internship_company_level": np.random.choice([0, 1, 2], records),
    "certification_count": np.random.randint(0, 9, records),
    "certification_company_level": np.random.choice([0, 1, 2], records),
    "technical_skills": np.random.randint(1, 12, records),
    "tools_known": np.random.randint(1, 15, records),
}

# Placement scoring logic
placement_score = (
    data["cgpa"] * 0.35 +
    data["coding_skill"] * 0.20 +
    data["communication_skill"] * 0.15 +
    data["aptitude_skill"] * 0.10 +
    data["problem_solving"] * 0.10 +
    data["internship_count"] * 0.05 +
    data["projects_count"] * 0.05
)

placement_probability = np.clip(
    (placement_score / placement_score.max()) * 100, 0, 100
)

data["placement_probability"] = np.round(placement_probability, 2)
data["placement_status"] = (placement_probability > 50).astype(int)

df = pd.DataFrame(data)

df.to_csv("data/raw/student_placement_data.csv", index=False)

print("10,000 synthetic student records generated successfully!")
