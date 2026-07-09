import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

np.random.seed(42)
N_SAMPLES = 1000

attendance = np.random.uniform(0, 100, N_SAMPLES)
assignments = np.random.uniform(0, 100, N_SAMPLES)
quiz_scores = np.random.uniform(0, 100, N_SAMPLES)
internal_marks = attendance + assignments + quiz_scores

total_pct = internal_marks / 3.0

noise_p = np.random.uniform(-10, 10, N_SAMPLES)
noise_a = np.random.uniform(-8, 8, N_SAMPLES)
noise_q = np.random.uniform(-8, 8, N_SAMPLES)

attendance = np.clip(attendance + noise_a * 0.3, 0, 100)
assignments = np.clip(assignments + noise_p * 0.4, 0, 100)
quiz_scores = np.clip(quiz_scores + noise_q * 0.3, 0, 100)
internal_marks = attendance + assignments + quiz_scores
total_pct = internal_marks / 3.0

pass_fail = np.where(total_pct >= 40, "Pass", "Fail")

def assign_grade(pct):
    if pct >= 90: return "A"
    elif pct >= 75: return "B"
    elif pct >= 60: return "C"
    elif pct >= 40: return "D"
    else: return "F"

def assign_performance(pct):
    if pct >= 85: return "Excellent"
    elif pct >= 65: return "Good"
    elif pct >= 40: return "Average"
    else: return "Poor"

grades = np.array([assign_grade(p) for p in total_pct])
performances = np.array([assign_performance(p) for p in total_pct])

X = np.column_stack([attendance, assignments, quiz_scores, internal_marks])
feature_names = ["attendance", "assignments", "quiz_scores", "internal_marks"]

X_train, X_test, y_train_pf, y_test_pf = train_test_split(X, pass_fail, test_size=0.2, random_state=42)
_, _, y_train_gr, y_test_gr = train_test_split(X, grades, test_size=0.2, random_state=42)
_, _, y_train_pr, y_test_pr = train_test_split(X, performances, test_size=0.2, random_state=42)

clf_pf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
clf_pf.fit(X_train, y_train_pf)
pf_acc = accuracy_score(y_test_pf, clf_pf.predict(X_test))

clf_gr = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
clf_gr.fit(X_train, y_train_gr)
gr_acc = accuracy_score(y_test_gr, clf_gr.predict(X_test))

clf_pr = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
clf_pr.fit(X_train, y_train_pr)
pr_acc = accuracy_score(y_test_pr, clf_pr.predict(X_test))

model_dir = os.path.dirname(os.path.abspath(__file__))
joblib.dump(clf_pf, os.path.join(model_dir, "model_pass_fail.joblib"))
joblib.dump(clf_gr, os.path.join(model_dir, "model_grade.joblib"))
joblib.dump(clf_pr, os.path.join(model_dir, "model_performance.joblib"))
joblib.dump(feature_names, os.path.join(model_dir, "feature_names.joblib"))

print("Model training complete!")
print(f"  Pass/Fail accuracy:     {pf_acc:.3f}")
print(f"  Grade accuracy:         {gr_acc:.3f}")
print(f"  Performance accuracy:   {pr_acc:.3f}")
print(f"\nClassification Report (Grade):")
print(classification_report(y_test_gr, clf_gr.predict(X_test)))
print(f"\nModels saved to: {model_dir}")
