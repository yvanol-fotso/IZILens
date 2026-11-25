import pytest

from app.common.enums import CaseStatus
from app.modules.kyc import analysis, rules
from app.modules.kyc.states import EXPIRABLE, TERMINAL, TRANSITIONS, UPLOADABLE, can_transition
from app.shared.i18n import messages as i18n


def test_every_status_is_described_and_terminal_states_are_final():
    assert set(TRANSITIONS) == set(CaseStatus)
    assert all(not TRANSITIONS[s] for s in TERMINAL)
    assert {CaseStatus.VERIFIED, CaseStatus.NOT_VERIFIED, CaseStatus.EXPIRED} == TERMINAL
    assert set(CaseStatus) >= UPLOADABLE | EXPIRABLE


@pytest.mark.parametrize(
    ("current", "target", "allowed"),
    [
        (CaseStatus.CREATED, CaseStatus.PROCESSING, True),
        (CaseStatus.MANUAL_REVIEW, CaseStatus.VERIFIED, True),
        (CaseStatus.MANUAL_REVIEW, CaseStatus.PROCESSING, False),
        (CaseStatus.VERIFIED, CaseStatus.NOT_VERIFIED, False),
        (CaseStatus.EXPIRED, CaseStatus.CREATED, False),
        (CaseStatus.FAILED, CaseStatus.NOT_VERIFIED, False),
        (CaseStatus.FAILED, CaseStatus.PROCESSING, True),
    ],
)
def test_transition_table(current, target, allowed):
    assert can_transition(current, target) is allowed


def test_a_technical_failure_cannot_become_a_refusal_directly():
    assert CaseStatus.NOT_VERIFIED not in TRANSITIONS[CaseStatus.FAILED]


def test_every_status_and_reason_has_french_and_english_text():
    for status in CaseStatus:
        assert i18n.STATUS_LABELS[status.value]["fr"] and i18n.STATUS_LABELS[status.value]["en"]
    for reason in (
        *rules.TRIGGER_REASONS.values(),
        "IMAGE_QUALITY",
        "DOCUMENT_NOT_RECOGNIZED",
        "MISSING_FIELDS",
        "INVALID_FIELDS",
        "DECLARED_IDENTITY_REQUIRED",
        "ATTEMPTS_EXHAUSTED",
        "TECHNICAL_ERROR",
        "VERIFIED_AUTOMATIC",
        "VERIFIED_MANUAL",
        "REJECTED_MANUAL",
        "REQUEST_EXPIRED",
        "COMPLEMENT_REQUESTED",
        "AWAITING_FACE_MATCH",
        "AWAITING_LIVENESS",
        "AUTO_DECISION_DISABLED",
        "REVIEW_REQUIRED",
        "ADMIN_TRANSITION",
    ):
        assert set(i18n.REASONS[reason]) == {"fr", "en"}, reason


def test_every_flag_code_can_be_rendered_in_both_languages():
    for code, texts in i18n.FLAGS.items():
        assert set(texts) == {"fr", "en"}
        for lang in ("fr", "en"):
            assert i18n.flag_message({"code": code, "field": "surname", "score_label": "70%"}, lang)
    assert i18n.reason_message("IMAGE_QUALITY", "en") != i18n.reason_message("IMAGE_QUALITY", "fr")
    assert i18n.normalize_lang("de") == "fr"


def test_analysis_only_emits_flag_codes_that_have_a_message():
    emitted = {
        "NO_TEXT_DETECTED",
        "DOCUMENT_TYPE_UNRECOGNIZED",
        "LOW_SHARPNESS",
        "MISSING_FIELD",
        "INVALID_VALUE",
        "LOW_CONFIDENCE",
        "INFERRED_FIELD",
        "UNDERAGE",
        "DECLARED_MISMATCH",
        "DECLARED_PARTIAL",
        "DECLARED_IDENTITY_MISSING",
        "DOCUMENT_EXPIRED",
        "EXPIRY_NOT_DETERMINABLE",
        "DUPLICATE_DOCUMENT_IMAGE",
        "POSSIBLE_DUPLICATE_IDENTITY",
        "FACE_MATCH_FAILED",
        "LIVENESS_FAILED",
    }
    assert emitted <= set(i18n.FLAGS) and analysis.compute_risk([]).value == "low"
