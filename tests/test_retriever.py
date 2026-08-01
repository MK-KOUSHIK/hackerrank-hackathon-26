import pytest
from src.loaders import DataLoader
from src.retriever import EvidenceRetriever

def test_evidence_retriever():
    loader = DataLoader()
    retriever = EvidenceRetriever(loader)
    
    # Test repeat business sender (e.g. u_012, business_092)
    res = retriever.get_evidence(user_id="u_012", business_id="business_092")
    assert isinstance(res["evidence_ids"], list)
    assert len(res["evidence_ids"]) > 0

def test_media_repetition_case():
    loader = DataLoader()
    retriever = EvidenceRetriever(loader)
    
    # Test media repetition (u_033, img_008)
    res = retriever.get_evidence(user_id="u_033", media_id="img_008")
    assert res["has_dismissed_history"] is True
