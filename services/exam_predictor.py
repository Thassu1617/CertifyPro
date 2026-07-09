import os
import numpy as np
import joblib

model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ML_model")

_clf_pf = None
_clf_gr = None
_clf_pr = None
_scaler = None
_feature_names = None


def _load_models():
    global _clf_pf, _clf_gr, _clf_pr, _scaler, _feature_names
    if _clf_pf is None:
        pf_path = os.path.join(model_dir, "exam_model_pass_fail.joblib")
        if not os.path.isfile(pf_path):
            return
        try:
            _clf_pf = joblib.load(pf_path)
            _clf_gr = joblib.load(os.path.join(model_dir, "exam_model_grade.joblib"))
            _clf_pr = joblib.load(os.path.join(model_dir, "exam_model_performance.joblib"))
            _scaler = joblib.load(os.path.join(model_dir, "exam_scaler.joblib"))
            _feature_names = joblib.load(os.path.join(model_dir, "exam_feature_names.joblib"))
        except Exception:
            pass


def _rule_based_prediction(percentage, marks_obtained=None, total_marks=None):
    if percentage is None and marks_obtained is not None and total_marks and total_marks > 0:
        percentage = (marks_obtained / total_marks) * 100
    if percentage >= 85:
        grade = "A"
        perf = "Excellent"
    elif percentage >= 70:
        grade = "B"
        perf = "Good"
    elif percentage >= 55:
        grade = "C"
        perf = "Average"
    elif percentage >= 40:
        grade = "D"
        perf = "Needs Improvement"
    else:
        grade = "F"
        perf = "Poor"
    return {
        "predicted_pass": "Pass" if percentage >= 40 else "Fail",
        "predicted_grade": grade,
        "predicted_performance": perf,
        "confidence_score": round(min(percentage / 100, 0.98), 2),
    }


def predict(percentage, attendance, quiz_scores=None, assignment_scores=None, exam_marks=None):
    return _rule_based_prediction(percentage, marks_obtained=exam_marks, total_marks=100)