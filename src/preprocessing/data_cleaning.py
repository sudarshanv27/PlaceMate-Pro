import pandas as pd

df = pd.read_csv("data/raw/student_placement_data.csv")

df.drop_duplicates(inplace=True)
df.fillna(0, inplace=True)

df.to_csv("data/processed/cleaned_student_placement_data.csv", index=False)

print("Cleaned dataset saved successfully!")
