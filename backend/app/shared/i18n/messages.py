from typing import Any

SUPPORTED = ("fr", "en")

FLAGS: dict[str, dict[str, str]] = {
    "NO_TEXT_DETECTED": {"fr": "Aucun texte détecté sur le document", "en": "No text detected on the document"},
    "DOCUMENT_TYPE_UNRECOGNIZED": {
        "fr": "Le document ne ressemble pas au type attendu",
        "en": "The document does not look like the expected type",
    },
    "LOW_SHARPNESS": {"fr": "Image floue, lecture potentiellement dégradée", "en": "Blurry image, reading may be degraded"},
    "MISSING_FIELD": {"fr": "Champ « {field} » introuvable", "en": "Field '{field}' not found"},
    "INVALID_VALUE": {"fr": "Valeur invalide pour « {field} »", "en": "Invalid value for '{field}'"},
    "LOW_CONFIDENCE": {"fr": "Lecture peu fiable pour « {field} » ({score})", "en": "Unreliable reading for '{field}' ({score})"},
    "INFERRED_FIELD": {
        "fr": "« {field} » déduit de sa position sur la carte",
        "en": "'{field}' inferred from its position on the card",
    },
    "UNDERAGE": {"fr": "Le titulaire est mineur", "en": "The holder is a minor"},
    "DECLARED_MISMATCH": {
        "fr": "« {field} » déclaré diffère de celui lu sur le document",
        "en": "Declared '{field}' differs from the one read on the document",
    },
    "DECLARED_PARTIAL": {
        "fr": "« {field} » déclaré ne correspond que partiellement au document",
        "en": "Declared '{field}' only partially matches the document",
    },
    "DECLARED_IDENTITY_MISSING": {
        "fr": "Identité déclarée manquante : comparaison impossible",
        "en": "Declared identity missing: comparison impossible",
    },
    "DOCUMENT_EXPIRED": {"fr": "Le document est expiré", "en": "The document is expired"},
    "EXPIRY_NOT_DETERMINABLE": {
        "fr": "Date d'expiration non déterminable de façon fiable",
        "en": "Expiry date cannot be reliably determined",
    },
    "DUPLICATE_DOCUMENT_IMAGE": {
        "fr": "Cette image a déjà été soumise dans un autre dossier",
        "en": "This image has already been submitted in another case",
    },
    "POSSIBLE_DUPLICATE_IDENTITY": {
        "fr": "Une identité identique existe déjà dans un autre dossier",
        "en": "An identical identity already exists in another case",
    },
    "AWAITING_FACE_MATCH": {"fr": "Comparaison faciale en attente", "en": "Face comparison pending"},
    "AWAITING_LIVENESS": {"fr": "Contrôle de présence réelle en attente", "en": "Liveness check pending"},
    "FACE_MATCH_FAILED": {
        "fr": "Le visage ne correspond pas au portrait du document",
        "en": "The face does not match the document portrait",
    },
    "LIVENESS_FAILED": {"fr": "Présence réelle non établie", "en": "Liveness not established"},
}

REASONS: dict[str, dict[str, str]] = {
    "IMAGE_QUALITY": {
        "fr": "L'image est de qualité insuffisante. Merci de refaire la capture dans un endroit bien éclairé.",
        "en": "The image quality is insufficient. Please retake it in a well-lit place.",
    },
    "DOCUMENT_NOT_RECOGNIZED": {
        "fr": "Le document n'a pas été reconnu. Merci de présenter le bon type de document, bien cadré.",
        "en": "The document was not recognized. Please present the correct document type, well framed.",
    },
    "MISSING_FIELDS": {
        "fr": "Certaines informations du document n'ont pas pu être lues. Merci de refaire la capture.",
        "en": "Some document information could not be read. Please retake the capture.",
    },
    "INVALID_FIELDS": {
        "fr": "Certaines informations lues sont invalides. Merci de refaire la capture.",
        "en": "Some information read is invalid. Please retake the capture.",
    },
    "DECLARED_IDENTITY_REQUIRED": {
        "fr": "Merci de renseigner votre identité pour poursuivre la vérification.",
        "en": "Please provide your identity details to continue the verification.",
    },
    "COMPLEMENT_REQUESTED": {
        "fr": "Un complément d'information ou une nouvelle capture est demandé.",
        "en": "Additional information or a new capture is requested.",
    },
    "ATTEMPTS_EXHAUSTED": {
        "fr": "Le nombre de tentatives autorisées est atteint. Votre dossier est transmis à un analyste.",
        "en": "The allowed number of attempts has been reached. Your case is forwarded to an analyst.",
    },
    "REVIEW_REQUIRED": {
        "fr": "Votre dossier est en cours d'examen par un analyste.",
        "en": "Your case is being reviewed by an analyst.",
    },
    "AUTO_DECISION_DISABLED": {
        "fr": "Votre dossier est en cours d'examen par un analyste.",
        "en": "Your case is being reviewed by an analyst.",
    },
    "AWAITING_FACE_MATCH": {"fr": "Une vérification faciale est requise.", "en": "A face verification is required."},
    "AWAITING_LIVENESS": {"fr": "Un contrôle de présence réelle est requis.", "en": "A liveness check is required."},
    "TECHNICAL_ERROR": {
        "fr": "Un incident technique a interrompu le traitement. Votre identité n'est pas refusée : le traitement sera repris.",
        "en": "A technical incident interrupted processing. Your identity is not refused: processing will resume.",
    },
    "VERIFIED_AUTOMATIC": {"fr": "Identité vérifiée.", "en": "Identity verified."},
    "VERIFIED_MANUAL": {"fr": "Identité vérifiée après examen.", "en": "Identity verified after review."},
    "REJECTED_MANUAL": {"fr": "Identité non vérifiée après examen.", "en": "Identity not verified after review."},
    "UNDERAGE": {
        "fr": "Identité non vérifiée : critère d'âge non satisfait.",
        "en": "Identity not verified: age criterion not met.",
    },
    "DECLARED_MISMATCH": {
        "fr": "Les informations déclarées ne correspondent pas au document.",
        "en": "Declared information does not match the document.",
    },
    "DOCUMENT_EXPIRED": {"fr": "Le document présenté est expiré.", "en": "The document presented is expired."},
    "REQUEST_EXPIRED": {
        "fr": "La demande a expiré avant d'être terminée. Cela ne constitue pas un refus : une nouvelle demande est possible.",
        "en": "The request expired before completion. This is not a refusal: a new request is possible.",
    },
    "AWAITING_DOCUMENTS": {"fr": "Merci de téléverser votre document d'identité.", "en": "Please upload your identity document."},
    "IN_PROGRESS": {"fr": "Vérification en cours.", "en": "Verification in progress."},
    "PROCESSING": {"fr": "Analyse en cours.", "en": "Analysis in progress."},
    "DUPLICATE_DOCUMENT_IMAGE": {
        "fr": "Votre dossier est en cours d'examen par un analyste.",
        "en": "Your case is being reviewed by an analyst.",
    },
    "POSSIBLE_DUPLICATE_IDENTITY": {
        "fr": "Votre dossier est en cours d'examen par un analyste.",
        "en": "Your case is being reviewed by an analyst.",
    },
    "LOW_CONFIDENCE": {
        "fr": "Votre dossier est en cours d'examen par un analyste.",
        "en": "Your case is being reviewed by an analyst.",
    },
    "DECLARED_PARTIAL": {
        "fr": "Votre dossier est en cours d'examen par un analyste.",
        "en": "Your case is being reviewed by an analyst.",
    },
    "ADMIN_TRANSITION": {"fr": "Statut modifié par l'équipe conformité.", "en": "Status changed by the compliance team."},
}

STATUS_LABELS: dict[str, dict[str, str]] = {
    "created": {"fr": "Demande créée", "en": "Request created"},
    "in_progress": {"fr": "En cours", "en": "In progress"},
    "action_required": {"fr": "Action requise", "en": "Action required"},
    "processing": {"fr": "Traitement en cours", "en": "Processing"},
    "manual_review": {"fr": "Examen par un analyste", "en": "Manual review"},
    "verified": {"fr": "Identité vérifiée", "en": "Identity verified"},
    "not_verified": {"fr": "Identité non vérifiée", "en": "Identity not verified"},
    "failed": {"fr": "Incident technique", "en": "Technical incident"},
    "expired": {"fr": "Demande expirée", "en": "Request expired"},
}

INSTRUCTIONS: dict[str, dict[str, list[str]]] = {
    "fr": {
        "steps": [
            "Acceptez les conditions de traitement de vos données.",
            "Renseignez votre identité telle qu'elle figure sur votre document.",
            "Photographiez votre document à plat, sans reflet, avec les quatre coins visibles.",
            "Patientez pendant l'analyse puis suivez les éventuelles instructions.",
        ],
    },
    "en": {
        "steps": [
            "Accept the terms for processing your data.",
            "Enter your identity as it appears on your document.",
            "Photograph your document flat, without glare, with all four corners visible.",
            "Wait during the analysis then follow any instructions.",
        ],
    },
}

SCOPE_DISCLAIMER = {
    "fr": "Ce résultat porte uniquement sur les contrôles listés ; il ne constitue pas une approbation complète de conformité.",
    "en": "This result covers only the listed checks; it is not a complete compliance approval.",
}


def normalize_lang(lang: str | None) -> str:
    return lang if lang in SUPPORTED else "fr"


def _render(table: dict[str, dict[str, str]], key: str | None, lang: str, **params: Any) -> str | None:
    if key is None:
        return None
    entry = table.get(key)
    if entry is None:
        return key
    template = entry.get(normalize_lang(lang)) or entry["fr"]
    try:
        return template.format(**params)
    except (KeyError, IndexError):
        return template


def flag_message(flag: dict[str, Any], lang: str) -> str:
    params = {"field": field_label(flag.get("field"), lang), "score": flag.get("score_label", "")}
    return _render(FLAGS, flag["code"], lang, **params) or flag["code"]


def reason_message(reason: str | None, lang: str) -> str | None:
    return _render(REASONS, reason, lang)


def status_label(status: str, lang: str) -> str:
    return _render(STATUS_LABELS, status, lang) or status


FIELD_LABELS = {
    "surname": {"fr": "nom", "en": "surname"},
    "given_names": {"fr": "prénoms", "en": "given names"},
    "date_of_birth": {"fr": "date de naissance", "en": "date of birth"},
    "place_of_birth": {"fr": "lieu de naissance", "en": "place of birth"},
    "sex": {"fr": "sexe", "en": "sex"},
    "height": {"fr": "taille", "en": "height"},
    "profession": {"fr": "profession", "en": "occupation"},
    "date_of_expiry": {"fr": "date d'expiration", "en": "expiry date"},
}


def field_label(field: str | None, lang: str) -> str:
    if not field:
        return ""
    entry = FIELD_LABELS.get(field)
    return entry[normalize_lang(lang)] if entry else field
