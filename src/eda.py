import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/processed/cleaned_student_placement_data.csv")

print("Dataset Shape:", df.shape)
print(df.describe())

# Placement distribution
plt.figure()
sns.countplot(x="placement_status", data=df)
plt.title("Placement Status Distribution")
plt.show()

# CGPA vs Placement
plt.figure()
sns.boxplot(x="placement_status", y="cgpa", data=df)
plt.title("CGPA vs Placement Status")
plt.show()

# Internship count vs Placement
plt.figure()
sns.barplot(x="internship_count", y="placement_status", data=df)
plt.title("Internship Count vs Placement")
plt.show()

# Correlation heatmap (NUMERIC ONLY)
plt.figure(figsize=(12, 8))
numeric_df = df.select_dtypes(include=["number"])
sns.heatmap(numeric_df.corr(), cmap="coolwarm")
plt.title("Feature Correlation Heatmap")
plt.show()
