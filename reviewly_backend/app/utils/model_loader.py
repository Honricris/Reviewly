# app/utils/model_loader.py
from sentence_transformers import SentenceTransformer

_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        _model_instance = SentenceTransformer("blevlabs/stella_en_v5", trust_remote_code=True)
    return _model_instance
