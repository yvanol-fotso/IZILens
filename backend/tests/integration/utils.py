from tests.helpers import DECLARED, files, form

CASES = "/api/v1/kyc/cases"


def submit(client, who, *, reference=None, declared=True, with_documents=True, front=None, back=None, lang=None, **extra):
    data = form(
        **({"reference": reference} if reference else {}),
        **(DECLARED if declared else {}),
        **({"language": lang} if lang else {}),
        **extra,
    )
    return client.post(CASES, data=data, files=files(front=front, back=back) if with_documents else None, headers=who)


def case(client, who, case_id, **params):
    response = client.get(f"{CASES}/{case_id}", params=params, headers=who)
    assert response.status_code == 200, response.text
    return response.json()


def upload(client, who, case_id, front=None, back=None):
    return client.post(f"{CASES}/{case_id}/documents", files=files(front=front, back=back), headers=who)


def codes(detail):
    return {f["code"] for f in detail["flags"]}
