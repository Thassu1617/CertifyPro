import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

np.random.seed(42)
N_SAMPLES = 2000

percentage = np.random.uniform(0, 100, N_SAMPLES)
attendance = np.random.uniform(0, 100, N_SAMPLES)
quiz_scores = np.random.uniform(0, 100, N_SAMPLES)
assignment_scores = np.random.uniform(0, 100, N_SAMPLES)
exam_marks = percentage

noise_att = np.random.uniform(-10, 10, N_SAMPLES)
noise_quiz = np.random.uniform(-8, 8, N_SAMPLES)
noise_asgn = np.random.uniform(-8, 8, N_SAMPLES)

attendance = np.clip(attendance + noise_att * 0.3, 0, 100)
quiz_scores = np.clip(quiz_scores + noise_quiz * 0.3, 0, 100)
assignment_scores = np.clip(assignment_scores + noise_asgn * 0.4, 0, 100)

pass_fail = np.where(exam_marks >= 40, "Pass", "Fail")

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

grades = np.array([assign_grade(p) for p in exam_marks])
performances = np.array([assign_performance(p) for p in exam_marks])

X = np.column_stack([percentage, attendance, quiz_scores, assignment_scores, exam_marks])
feature_names = ["percentage", "attendance", "quiz_scores", "assignment_scores", "exam_marks"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train_pf, y_test_pf = train_test_split(X_scaled, pass_fail, test_size=0.2, random_state=42)
_, _, y_train_gr, y_test_gr = train_test_split(X_scaled, grades, test_size=0.2, random_state=42)
_, _, y_train_pr, y_test_pr = train_test_split(X_scaled, performances, test_size=0.2, random_state=42)

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
joblib.dump(clf_pf, os.path.join(model_dir, "exam_model_pass_fail.joblib"))
joblib.dump(clf_gr, os.path.join(model_dir, "exam_model_grade.joblib"))
joblib.dump(clf_pr, os.path.join(model_dir, "exam_model_performance.joblib"))
joblib.dump(feature_names, os.path.join(model_dir, "exam_feature_names.joblib"))
joblib.dump(scaler, os.path.join(model_dir, "exam_scaler.joblib"))

print("Exam model training complete!")
print(f"  Pass/Fail accuracy:     {pf_acc:.3f}")
print(f"  Grade accuracy:         {gr_acc:.3f}")
print(f"  Performance accuracy:   {pr_acc:.3f}")
print(f"\nClassification Report (Grade):")
print(classification_report(y_test_gr, clf_gr.predict(X_test)))
print(f"\nModels saved to: {model_dir}")
