from difflib import SequenceMatcher

from app.shared.validation.fields import canonical

COMPARED_FIELDS = ("surname", "given_names", "date_of_birth")


def _name_similarity(declared: str, read: str) -> tuple[str, float]:
    left, right = canonical(declared), canonical(read)
    if left == right:
        return "match", 1.0
    left_tokens, right_tokens = set(left.split()), set(right.split())
    ratio = SequenceMatcher(None, " ".join(sorted(left_tokens)), " ".join(sorted(right_tokens))).ratio()
    if left_tokens and right_tokens and (left_tokens <= right_tokens or right_tokens <= left_tokens):
        return "partial", round(max(ratio, 0.8), 4)
    return "ratio", round(ratio, 4)


def compare_identity(declared: dict, fields: dict, *, name_match: float, name_partial: float) -> dict[str, dict]:
    """Compare chaque champ déclaré au champ lu ; les valeurs ne sont jamais recopiées dans le résultat."""
    result: dict[str, dict] = {}
    for name in COMPARED_FIELDS:
        read = (fields.get(name) or {}).get("normalized")
        wanted = declared.get(name)
        if not wanted or not read:
            result[name] = {"status": "missing", "similarity": 0.0}
        elif name == "date_of_birth":
            same = wanted == read
            result[name] = {"status": "match" if same else "mismatch", "similarity": 1.0 if same else 0.0}
        else:
            kind, similarity = _name_similarity(wanted, read)
            if kind == "ratio":
                kind = "match" if similarity >= name_match else "partial" if similarity >= name_partial else "mismatch"
            result[name] = {"status": kind, "similarity": similarity}
    return result


def overall_status(comparison: dict[str, dict]) -> str:
    statuses = {entry["status"] for entry in comparison.values()}
    if "mismatch" in statuses or "missing" in statuses:
        return "failed"
    if "partial" in statuses:
        return "inconclusive"
    return "passed"
