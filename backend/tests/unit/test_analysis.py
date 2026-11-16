from datetime import date

from app.modules.kyc.analysis import analyze_front
from tests.helpers import cni_lines, line

KWARGS = {"today": date(2026, 11, 14), "review_threshold": 0.9, "min_line_score": 0.3}


def codes(result):
    return {f["code"] for f in result.flags}


def test_clean_card_is_low_risk_with_fingerprint():
    result = analyze_front(cni_lines(), sharpness=120.0, **KWARGS)
    assert result.risk_level.value == "low"
    assert codes(result) == {"INFERRED_FIELD"}
    assert result.fields["date_of_birth"]["normalized"] == "1992-06-15"
    assert result.confidence == 0.96
    assert result.identity_fingerprint and len(result.identity_fingerprint) == 64


def test_fingerprint_ignores_case_and_accents():
    a = analyze_front(cni_lines(surname="Atángana Mohammadou"), sharpness=100, **KWARGS)
    b = analyze_front(cni_lines(surname="ATANGANA MOHAMMADOU"), sharpness=100, **KWARGS)
    assert a.identity_fingerprint == b.identity_fingerprint


def test_minor_is_high_risk():
    result = analyze_front(cni_lines(dob="01.01.2015"), sharpness=100, **KWARGS)
    assert "UNDERAGE" in codes(result) and result.risk_level.value == "high"


def test_future_birth_date_is_invalid():
    result = analyze_front(cni_lines(dob="01.01.2030"), sharpness=100, **KWARGS)
    assert "INVALID_DATE_OF_BIRTH" in codes(result) and result.identity_fingerprint is None


def test_low_confidence_flagged_by_severity():
    lines = [ln if ln.text != "SALAH" else line("SALAH", 0.7, ln.x1, ln.y1, ln.x2, ln.y2) for ln in cni_lines()]
    flag = next(f for f in analyze_front(lines, sharpness=100, **KWARGS).flags if f["code"] == "LOW_CONFIDENCE")
    assert (flag["field"], flag["severity"]) == ("given_names", "medium")


def test_unknown_document_and_blur():
    result = analyze_front(cni_lines(header=False), sharpness=5.0, **KWARGS)
    assert {"DOCUMENT_TYPE_UNRECOGNIZED", "LOW_SHARPNESS"} <= codes(result)


def test_no_text_is_high_risk():
    result = analyze_front([], sharpness=100, **KWARGS)
    assert "NO_TEXT_DETECTED" in codes(result) and result.risk_level.value == "high" and result.confidence is None
