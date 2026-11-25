from datetime import date

from app.modules.kyc import matching
from app.modules.kyc.analysis import analyze_document, compute_risk, declared_match_check, derive_flags
from tests.helpers import cni_lines, line

TODAY = date(2026, 11, 17)
TH = {"ocr_review": 0.9, "name_match": 0.9, "name_partial": 0.75}
DECLARED = {"surname": "Atangana Mohammadou", "given_names": "Salah", "date_of_birth": "1992-06-15"}


def analyze(lines=None, declared=DECLARED, sharpness=120.0):
    return analyze_document(
        lines if lines is not None else cni_lines(),
        sharpness=sharpness,
        today=TODAY,
        thresholds=TH,
        min_line_score=0.3,
        declared=declared,
    )


def statuses(analysis):
    return {c.check_type.value: c.status.value for c in analysis.checks}


def codes(analysis, checks_extra=None):
    checks = {c.check_type.value: {"status": c.status.value, "details": c.details} for c in analysis.checks}
    checks.update(checks_extra or {})
    return {f["code"] for f in derive_flags(analysis.fields, checks, today=TODAY, thresholds=TH)}


def test_clean_card_passes_every_executed_check():
    result = analyze()
    assert statuses(result) == {
        "document_quality": "passed",
        "document_recognition": "passed",
        "ocr_extraction": "passed",
        "declared_match": "passed",
        "expiry": "not_run",
    }
    assert result.confidence == 0.96 and result.identity_fingerprint and len(result.identity_fingerprint) == 64


def test_declared_and_read_values_stay_separate_and_are_not_leaked_in_check_details():
    result = analyze()
    declared_check = next(c for c in result.checks if c.check_type.value == "declared_match")
    assert "Atangana" not in str(declared_check.details) and result.fields["surname"]["value"] == "Atángana Mohammadou"


def test_missing_declared_identity_means_comparison_not_run():
    result = analyze(declared=None)
    assert statuses(result)["declared_match"] == "not_run"
    assert "DECLARED_IDENTITY_MISSING" in codes(result)


def test_mismatch_and_partial_match_are_classified():
    wrong = analyze(declared={**DECLARED, "surname": "Ndongo", "date_of_birth": "1990-01-01"})
    assert statuses(wrong)["declared_match"] == "failed"
    partial = analyze(declared={**DECLARED, "surname": "Atangana"})
    assert statuses(partial)["declared_match"] == "inconclusive" and "DECLARED_PARTIAL" in codes(partial)


def test_fingerprint_ignores_case_and_accents():
    assert analyze().identity_fingerprint == analyze(cni_lines(surname="ATANGANA MOHAMMADOU")).identity_fingerprint


def test_unrecognized_and_empty_documents():
    assert statuses(analyze(cni_lines(header=False)))["document_recognition"] == "failed"
    empty = analyze([])
    assert statuses(empty)["document_recognition"] == "failed" and "NO_TEXT_DETECTED" in codes(empty)


def test_missing_required_field_fails_extraction():
    lines = [ln for ln in cni_lines() if ln.text != "15.06.1992"]
    result = analyze(lines)
    assert statuses(result)["ocr_extraction"] == "failed"
    assert "MISSING_FIELD" in codes(result)


def test_low_confidence_is_inconclusive_with_severity_by_score():
    weak = [ln if ln.text != "SALAH" else line("SALAH", 0.7, ln.x1, ln.y1, ln.x2, ln.y2) for ln in cni_lines()]
    result = analyze(weak)
    assert statuses(result)["ocr_extraction"] == "inconclusive"
    flag = next(
        f
        for f in derive_flags(
            result.fields,
            {c.check_type.value: {"status": c.status.value, "details": c.details} for c in result.checks},
            today=TODAY,
            thresholds=TH,
        )
        if f["code"] == "LOW_CONFIDENCE"
    )
    assert flag["severity"] == "medium"


def test_blur_fails_quality_and_minor_is_flagged():
    assert statuses(analyze(sharpness=5.0))["document_quality"] == "failed"
    minor = analyze(cni_lines(dob="01.01.2015"))
    assert "UNDERAGE" in codes(minor) and compute_risk(derive_flags(minor.fields, {}, today=TODAY, thresholds=TH)).value == "high"


def test_expiry_is_checked_only_when_it_can_be_read():
    with_expiry = cni_lines() + [line("DATEOFEXPIRY", 0.99, 600, 125, 780, 138), line("01.01.2020", 1.0, 600, 148, 760, 178)]
    expired = analyze(with_expiry)
    assert statuses(expired)["expiry"] == "failed" and "DOCUMENT_EXPIRED" in codes(expired)
    valid = analyze(cni_lines() + [line("DATEOFEXPIRY", 0.99, 600, 125, 780, 138), line("01.01.2035", 1.0, 600, 148, 760, 178)])
    assert statuses(valid)["expiry"] == "passed"


def test_name_matching_primitives():
    fields = {
        "surname": {"normalized": "Atángana Mohammadou"},
        "given_names": {"normalized": "SALAH"},
        "date_of_birth": {"normalized": "1992-06-15"},
    }
    assert matching.overall_status(matching.compare_identity(DECLARED, fields, name_match=0.9, name_partial=0.75)) == "passed"
    typo = matching.compare_identity({**DECLARED, "given_names": "Salaah"}, fields, name_match=0.9, name_partial=0.75)
    assert typo["given_names"]["status"] in ("match", "partial")
    assert declared_match_check({}, fields, TH).status.value == "not_run"
