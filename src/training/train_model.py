import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV,
    cross_val_score,
    learning_curve
)

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
    roc_curve
)

from scipy.stats import ttest_rel

# -----------------------------
# CREATE GRAPH FOLDER
# -----------------------------
GRAPH_DIR = r"E:\Student Placement Prediction\graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

# -----------------------------
# 1. Load dataset
# -----------------------------
df = pd.read_csv(r"E:\data\student_placement_dataset_1000.csv")

# -----------------------------
# 2. FEATURE ENGINEERING
# -----------------------------
df["avg_skill"] = (
    df["coding_skill"] +
    df["communication_skill"] +
    df["aptitude_skill"] +
    df["problem_solving"]
) / 4

df["intern_cert_ratio"] = df["internship_count"] / (df["certification_count"] + 1)

# -----------------------------
# Feature list
# -----------------------------
feature_columns = [
    'cgpa',
    'coding_skill',
    'communication_skill',
    'aptitude_skill',
    'problem_solving',
    'projects_count',
    'internship_count',
    'internship_company_level',
    'certification_count',
    'certification_company_level',
    'avg_skill',
    'intern_cert_ratio'
]

X = df[feature_columns]
y = df['placement_status']

# -----------------------------
# 3. Stratified split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# -----------------------------
# 4. Scaling
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# 5. BASELINE MODELS
# -----------------------------
baseline_models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Decision Tree": DecisionTreeClassifier(max_depth=6, class_weight="balanced"),
    "SVM": SVC(probability=True, class_weight="balanced")
}

print("\n🔍 BASELINE MODEL RESULTS\n")

plt.figure()

for name, model in baseline_models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:,1]

    print(f"\n===== {name} =====")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("F1:", f1_score(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))

    # ROC
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plt.plot(fpr, tpr, label=name)

plt.title("ROC Curve - Baseline Models")
plt.legend()
plt.savefig(os.path.join(GRAPH_DIR, "roc_curve_baseline.png"), dpi=300)
plt.show()

# -----------------------------
# 6. ADVANCED MODEL + TUNING
# -----------------------------
rf = RandomForestClassifier(class_weight="balanced", random_state=42)

param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [None, 8, 12],
    "min_samples_split": [2, 5]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid = GridSearchCV(
    rf,
    param_grid,
    cv=cv,
    scoring="f1",
    n_jobs=-1
)

grid.fit(X_train_scaled, y_train)
best_model = grid.best_estimator_

print("\n✅ Best Params:", grid.best_params_)

# -----------------------------
# 7. STATISTICAL VALIDATION
# -----------------------------
rf_cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=cv, scoring="f1")
log_cv_scores = cross_val_score(
    baseline_models["Logistic Regression"],
    X_train_scaled,
    y_train,
    cv=cv,
    scoring="f1"
)

t_stat, p_value = ttest_rel(rf_cv_scores, log_cv_scores)

print("\n📊 STATISTICAL TEST")
print("RF mean F1:", rf_cv_scores.mean())
print("Logistic mean F1:", log_cv_scores.mean())
print("P-value:", p_value)

# -----------------------------
# 8. LEARNING CURVE
# -----------------------------
train_sizes, train_scores, test_scores = learning_curve(
    best_model,
    X_train_scaled,
    y_train,
    cv=cv,
    scoring="f1"
)

plt.figure()
plt.plot(train_sizes, train_scores.mean(axis=1), label="Train")
plt.plot(train_sizes, test_scores.mean(axis=1), label="CV")
plt.title("Learning Curve")
plt.legend()
plt.savefig(os.path.join(GRAPH_DIR, "learning_curve.png"), dpi=300)
plt.show()

# -----------------------------
# 9. FEATURE IMPORTANCE
# -----------------------------
importances = best_model.feature_importances_
imp_df = pd.DataFrame({
    "Feature": feature_columns,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print("\n🔎 FEATURE IMPORTANCE\n", imp_df)

plt.figure(figsize=(8,5))
plt.barh(imp_df["Feature"], imp_df["Importance"])
plt.title("Feature Importance")
plt.savefig(os.path.join(GRAPH_DIR, "feature_importance.png"), dpi=300)
plt.show()

# -----------------------------
# 10. FINAL EVALUATION
# -----------------------------
y_pred = best_model.predict(X_test_scaled)
y_prob = best_model.predict_proba(X_test_scaled)[:,1]

print("\n🏆 FINAL MODEL PERFORMANCE")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1:", f1_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print(confusion_matrix(y_test, y_pred))

# -----------------------------
# 11. BUSINESS OPTIMIZATION
# -----------------------------
thresholds = np.arange(0.3, 0.8, 0.05)
profits = []

TP_VALUE = 50000
FP_COST = 15000

for t in thresholds:
    preds = (y_prob >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()
    profit = (tp * TP_VALUE) - (fp * FP_COST)
    profits.append(profit)

best_t = thresholds[np.argmax(profits)]

plt.figure()
plt.plot(thresholds, profits)
plt.xlabel("Threshold")
plt.ylabel("Profit")
plt.title("Profit vs Threshold")
plt.savefig(os.path.join(GRAPH_DIR, "profit_threshold_curve.png"), dpi=300)
plt.show()

print("\n💼 BUSINESS THRESHOLD:", best_t)

# -----------------------------
# 12. FINAL MODEL SELECTION
# -----------------------------
print("\n🏁 FINAL MODEL SELECTED")
print("Tuned Random Forest")
print("Best business threshold:", best_t)

# -----------------------------
# 13. SAVE MODEL
# -----------------------------
model_dir = r"E:\Student Placement Prediction\models"
os.makedirs(model_dir, exist_ok=True)

joblib.dump(best_model, os.path.join(model_dir, "final_model.pkl"))
joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
joblib.dump(feature_columns, os.path.join(model_dir, "feature_names.pkl"))

print("\n✅ ALL FILES SAVED SUCCESSFULLY")
