"""Fonctions de sécurité à compléter avant toute mise en production."""


def get_password_hash(password: str) -> str:
    raise NotImplementedError("Brancher une bibliothèque de hachage adaptée (Argon2/bcrypt).")


def verify_password(plain_password: str, password_hash: str) -> bool:
    raise NotImplementedError("Implémenter la vérification du mot de passe.")
