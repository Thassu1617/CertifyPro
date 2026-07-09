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
    _load_models()
    if _clf_pf is None:
        return _rule_based_prediction(percentage, marks_obtained=exam_marks, total_marks=100)
    if attendance is None:
        attendance = min(percentage * 0.9, 100)
    if quiz_scores is None:
        quiz_scores = min(percentage * 0.85, 100)
    if assignment_scores is None:
        assignment_scores = min(percentage * 0.8, 100)
    if exam_marks is None:
        exam_marks = percentage
    features = np.array([[percentage, attendance, quiz_scores, assignment_scores, exam_marks]])
    features_scaled = _scaler.transform(features)

    pf_pred = _clf_pf.predict(features_scaled)[0]
    gr_pred = _clf_gr.predict(features_scaled)[0]
    pr_pred = _clf_pr.predict(features_scaled)[0]

    pf_proba = np.max(_clf_pf.predict_proba(features_scaled)[0])
    gr_proba = np.max(_clf_gr.predict_proba(features_scaled)[0])
    pr_proba = np.max(_clf_pr.predict_proba(features_scaled)[0])

    confidence = float(np.mean([pf_proba, gr_proba, pr_proba]))

    return {
        "predicted_pass": str(pf_pred),
        "predicted_grade": str(gr_pred),
        "predicted_performance": str(pr_pred),
        "confidence_score": round(confidence, 4),
    }