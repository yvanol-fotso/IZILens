import pytest

from app.common.enums import CaseStatus as S
from app.modules.kyc.defaults import DEFAULT_JOURNEY
from app.modules.kyc.rules import evaluate

REQUIRED = DEFAULT_JOURNEY["required_checks"]
RULES = DEFAULT_JOURNEY["decision_rules"]


def ok(**override):
    checks = {
        "document_quality": {"status": "passed", "details": {}},
        "document_recognition": {"status": "passed", "details": {}},
        "ocr_extraction": {"status": "passed", "details": {}},
        "declared_match": {"status": "passed", "details": {}},
        "expiry": {"status": "not_run", "details": {"reason": "NOT_DETERMINABLE"}},
        "duplicate_image": {"status": "passed", "details": {}},
        "duplicate_identity": {"status": "passed", "details": {}},
    }
    for key, (status, details) in override.items():
        checks[key] = {"status": status, "details": details}
    return checks


def run(checks, flags=(), *, required=REQUIRED, rules=RULES, auto=True, retry=True):
    return evaluate(
        checks, list(flags), required_checks=required, decision_rules=rules, auto_decision_enabled=auto, can_retry=lambda _: retry
    )


def test_clear_case_is_verified_automatically_only_when_enabled():
    assert run(ok()).status == S.VERIFIED
    outcome = run(ok(), auto=False)
    assert (outcome.status, outcome.reason) == (S.MANUAL_REVIEW, "AUTO_DECISION_DISABLED")


def test_high_severity_flag_blocks_automatic_verification():
    assert run(ok(), [{"code": "X", "severity": "high"}]).status == S.MANUAL_REVIEW


def test_technical_error_is_never_a_refusal():
    outcome = run(ok(ocr_extraction=("error", {})))
    assert (outcome.status, outcome.reason) == (S.FAILED, "TECHNICAL_ERROR")


@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"document_quality": ("failed", {})}, "IMAGE_QUALITY"),
        ({"document_recognition": ("failed", {"reason": "TYPE_UNRECOGNIZED"})}, "DOCUMENT_NOT_RECOGNIZED"),
        ({"ocr_extraction": ("failed", {"missing": ["surname"]})}, "MISSING_FIELDS"),
        ({"ocr_extraction": ("failed", {"invalid": ["date_of_birth"]})}, "INVALID_FIELDS"),
    ],
)
def test_recapture_requested_while_attempts_remain_then_review(override, reason):
    assert (run(ok(**override)).status, run(ok(**override)).reason) == (S.ACTION_REQUIRED, reason)
    exhausted = run(ok(**override), retry=False)
    assert (exhausted.status, exhausted.reason) == (S.MANUAL_REVIEW, "ATTEMPTS_EXHAUSTED")


def test_declared_identity_required_before_dependent_checks():
    outcome = run(ok(declared_match=("not_run", {"reason": "DECLARED_IDENTITY_MISSING"})))
    assert (outcome.status, outcome.reason) == (S.ACTION_REQUIRED, "DECLARED_IDENTITY_REQUIRED")


def test_underage_rejected_by_default_but_rule_is_configurable():
    flags = [{"code": "UNDERAGE", "severity": "high"}]
    assert run(ok(), flags).status == S.NOT_VERIFIED
    assert run(ok(), flags, rules={**RULES, "underage": "manual_review"}).status == S.MANUAL_REVIEW


@pytest.mark.parametrize(
    ("override", "rule"),
    [
        ({"declared_match": ("failed", {})}, "declared_mismatch"),
        ({"declared_match": ("inconclusive", {})}, "declared_partial"),
        ({"expiry": ("failed", {"expired": True})}, "expired_document"),
        ({"duplicate_image": ("inconclusive", {})}, "duplicate_image"),
        ({"duplicate_identity": ("inconclusive", {})}, "duplicate_identity"),
        ({"ocr_extraction": ("inconclusive", {})}, "low_confidence"),
    ],
)
def test_ambiguity_goes_to_review_and_rules_can_reject(override, rule):
    assert run(ok(**override)).status == S.MANUAL_REVIEW
    assert run(ok(**override), rules={**RULES, rule: "not_verified"}).status == S.NOT_VERIFIED


def test_mandatory_biometrics_hold_the_case_then_gate_verification():
    required = [*REQUIRED, "face_match", "liveness"]
    waiting = run(ok(), required=required)
    assert (waiting.status, waiting.reason) == (S.IN_PROGRESS, "AWAITING_FACE_MATCH")
    both = run(ok(face_match=("passed", {})), required=required)
    assert (both.status, both.reason) == (S.IN_PROGRESS, "AWAITING_LIVENESS")
    assert run(ok(face_match=("passed", {}), liveness=("passed", {})), required=required).status == S.VERIFIED


def test_liveness_failure_cannot_be_hidden_by_a_positive_face_match():
    required = [*REQUIRED, "face_match", "liveness"]
    outcome = run(ok(face_match=("passed", {}), liveness=("failed", {})), required=required)
    assert outcome.status == S.MANUAL_REVIEW and "biometric_failure" in outcome.triggers


def test_required_check_not_passed_is_never_silently_verified():
    outcome = run(ok(declared_match=("not_run", {"reason": "READ_DATA_INCOMPLETE"})))
    assert outcome.status == S.MANUAL_REVIEW
