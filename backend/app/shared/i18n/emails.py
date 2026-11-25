from typing import Any

from app.shared.i18n.messages import normalize_lang

TEMPLATES: dict[str, dict[str, tuple[str, str]]] = {
    "request_confirmation": {
        "fr": (
            "Votre demande {reference} a bien été reçue",
            "Bonjour {full_name},\n\nNous avons bien reçu votre demande. Son numéro de référence est {reference}.\n"
            "Notre équipe {team} vous répondra dans les meilleurs délais.\n\nL'équipe IZI LENS",
        ),
        "en": (
            "Your request {reference} has been received",
            "Hello {full_name},\n\nWe have received your request. Its reference number is {reference}.\n"
            "Our {team} team will get back to you shortly.\n\nThe IZI LENS team",
        ),
    },
    "request_internal": {
        "fr": (
            "[{team}] Nouvelle demande {reference}",
            "Nouvelle demande {kind} ({reference}) reçue.\nType : {type}\nConsultez-la dans le back-office.",
        ),
        "en": (
            "[{team}] New request {reference}",
            "New {kind} request ({reference}) received.\nType: {type}\nOpen it in the back-office.",
        ),
    },
    "account_invitation": {
        "fr": (
            "Votre accès IZI LENS pour {organization}",
            "Bonjour {full_name},\n\nUn compte administrateur a été créé pour {organization}.\nConnexion : {login_url}\n{credentials}\n\nL'équipe IZI LENS",
        ),
        "en": (
            "Your IZI LENS access for {organization}",
            "Hello {full_name},\n\nAn administrator account has been created for {organization}.\nSign in: {login_url}\n{credentials}\n\nThe IZI LENS team",
        ),
    },
    "access_decision": {
        "fr": (
            "Votre demande d'accès {reference} : {decision}",
            "Bonjour {full_name},\n\nVotre demande d'accès développeur {reference} est {decision}.\n{note}\n\nL'équipe IZI LENS",
        ),
        "en": (
            "Your access request {reference}: {decision}",
            "Hello {full_name},\n\nYour developer access request {reference} is {decision}.\n{note}\n\nThe IZI LENS team",
        ),
    },
}


def render(template: str, locale: str, params: dict[str, Any]) -> tuple[str, str]:
    subject, body = TEMPLATES[template][normalize_lang(locale)]
    return subject.format(**params), body.format(**params)
