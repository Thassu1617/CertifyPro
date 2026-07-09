import os
import numpy as np
import joblib

model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ML_model")

_clf_pf = None
_clf_gr = None
_clf_pr = None
_feature_names = None


def _load_models():
    global _clf_pf, _clf_gr, _clf_pr, _feature_names
    if _clf_pf is None:
        _clf_pf = joblib.load(os.path.join(model_dir, "model_pass_fail.joblib"))
        _clf_gr = joblib.load(os.path.join(model_dir, "model_grade.joblib"))
        _clf_pr = joblib.load(os.path.join(model_dir, "model_performance.joblib"))
        _feature_names = joblib.load(os.path.join(model_dir, "feature_names.joblib"))


def predict(attendance, assignments, quiz_scores):
    _load_models()
    internal_marks = attendance + assignments + quiz_scores
    features = np.array([[attendance, assignments, quiz_scores, internal_marks]])

    pf_pred = _clf_pf.predict(features)[0]
    gr_pred = _clf_gr.predict(features)[0]
    pr_pred = _clf_pr.predict(features)[0]

    pf_proba = np.max(_clf_pf.predict_proba(features)[0])
    gr_proba = np.max(_clf_gr.predict_proba(features)[0])
    pr_proba = np.max(_clf_pr.predict_proba(features)[0])

    confidence = float(np.mean([pf_proba, gr_proba, pr_proba]))

    return {
        "predicted_pass": str(pf_pred),
        "predicted_grade": str(gr_pred),
        "predicted_performance": str(pr_pred),
        "confidence_score": round(confidence, 4),
    }
