from app.common.enums import UserRole

PUBLIC = "/api/v1/public/content"
ADMIN = "/api/v1/admin/cms"


def entry(**overrides):
    base = {
        "kind": "blog",
        "locale": "fr",
        "slug": "kyc-afrique",
        "title": "Le KYC en Afrique",
        "summary": "Panorama",
        "body": "# Titre\n\nContenu **markdown**.",
        "tags": ["KYC", "afrique"],
    }
    return {**base, **overrides}


def test_editorial_workflow_draft_publish_unpublish(client, staff):
    editor = staff(UserRole.CONTENT_EDITOR)
    created = client.post(ADMIN, json=entry(), headers=editor)
    assert created.status_code == 201 and created.json()["status"] == "draft" and created.json()["tags"] == ["afrique", "kyc"]
    entry_id = created.json()["id"]
    assert client.get(f"{PUBLIC}?kind=blog&locale=fr").json()["total"] == 0
    assert client.get(f"{PUBLIC}/blog/kyc-afrique?locale=fr").status_code == 404
    published = client.post(f"{ADMIN}/{entry_id}/publish", headers=editor).json()
    assert published["status"] == "published" and published["published_at"]
    listing = client.get(f"{PUBLIC}?kind=blog&locale=fr")
    assert listing.json()["total"] == 1 and listing.headers["cache-control"] == "public, max-age=60"
    assert "body" not in listing.json()["items"][0]
    assert client.get(f"{PUBLIC}/blog/kyc-afrique?locale=fr").json()["body"].startswith("# Titre")
    assert client.post(f"{ADMIN}/{entry_id}/unpublish", headers=editor).json()["status"] == "draft"
    assert client.get(f"{PUBLIC}/blog/kyc-afrique?locale=fr").status_code == 404
    assert client.post(f"{ADMIN}/{entry_id}/archive", headers=editor).json()["status"] == "archived"
    assert client.delete(f"{ADMIN}/{entry_id}", headers=editor).status_code == 204
    assert client.get(f"{ADMIN}/{entry_id}", headers=editor).status_code == 404


def test_content_is_per_language_with_unique_slugs(client, staff):
    editor = staff(UserRole.CONTENT_EDITOR)
    assert client.post(ADMIN, json=entry(), headers=editor).status_code == 201
    duplicate = client.post(ADMIN, json=entry(), headers=editor)
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "SLUG_ALREADY_USED"
    english = client.post(ADMIN, json=entry(locale="en", title="KYC in Africa"), headers=editor)
    assert english.status_code == 201
    for item in client.get(ADMIN, headers=editor).json()["items"]:
        client.post(f"{ADMIN}/{item['id']}/publish", headers=editor)
    assert [i["title"] for i in client.get(f"{PUBLIC}?locale=en").json()["items"]] == ["KYC in Africa"]
    assert client.get(f"{PUBLIC}/blog/kyc-afrique?locale=en").json()["title"] == "KYC in Africa"


def test_faq_is_ordered_by_position_filtered_by_category_and_searchable(client, staff):
    editor = staff(UserRole.CONTENT_EDITOR)
    for slug, position, category, title, body in (
        ("tarifs", 2, "commercial", "Comment sont facturées les vérifications ?", "À la demande."),
        ("delais", 1, "technique", "Quel est le délai de traitement ?", "Quelques secondes."),
        ("langues", 3, "technique", "Quelles langues ?", "Français et anglais."),
    ):
        created = client.post(
            ADMIN, json=entry(kind="faq", slug=slug, title=title, body=body, category=category, position=position), headers=editor
        ).json()
        client.post(f"{ADMIN}/{created['id']}/publish", headers=editor)
    assert [i["slug"] for i in client.get(f"{PUBLIC}?kind=faq&locale=fr").json()["items"]] == ["delais", "tarifs", "langues"]
    assert [i["slug"] for i in client.get(f"{PUBLIC}?kind=faq&locale=fr&category=technique").json()["items"]] == [
        "delais",
        "langues",
    ]
    assert [i["slug"] for i in client.get(f"{PUBLIC}?kind=faq&locale=fr&search=délai").json()["items"]] == ["delais"]
    assert [i["slug"] for i in client.get(f"{PUBLIC}?kind=faq&locale=fr&search=anglais").json()["items"]] == ["langues"]


def test_tags_filter_and_pagination(client, staff):
    editor = staff(UserRole.CONTENT_EDITOR)
    for i in range(5):
        created = client.post(
            ADMIN, json=entry(slug=f"post-{i}", title=f"Article {i}", tags=["kyc"] if i % 2 == 0 else ["kyb"]), headers=editor
        ).json()
        client.post(f"{ADMIN}/{created['id']}/publish", headers=editor)
    assert client.get(f"{PUBLIC}?kind=blog&locale=fr&page_size=2").json()["items"].__len__() == 2
    assert {i["slug"] for i in client.get(f"{PUBLIC}?kind=blog&locale=fr&tag=kyb").json()["items"]} == {"post-1", "post-3"}
    assert client.get(f"{PUBLIC}?page_size=101").status_code == 422


def test_active_markup_is_rejected_and_validation_applies(client, staff):
    editor = staff(UserRole.CONTENT_EDITOR)
    for body in ("<script>alert(1)</script>", "[x](javascript:alert(1))", '<img src=x onerror="alert(1)">'):
        assert client.post(ADMIN, json=entry(body=body), headers=editor).status_code == 422
    assert client.post(ADMIN, json=entry(slug="Bad Slug"), headers=editor).status_code == 422
    assert client.post(ADMIN, json=entry(kind="news"), headers=editor).status_code == 422
    created = client.post(ADMIN, json=entry(), headers=editor).json()
    assert client.patch(f"{ADMIN}/{created['id']}", json={"body": "<iframe src=x>"}, headers=editor).status_code == 422
    updated = client.patch(f"{ADMIN}/{created['id']}", json={"title": "Titre corrigé", "position": 4}, headers=editor).json()
    assert (updated["title"], updated["position"]) == ("Titre corrigé", 4)


def test_only_editorial_roles_can_manage_content(client, org, staff, super_admin):
    for headers in (
        org["admin"],
        staff(UserRole.SALES_AGENT),
        staff(UserRole.PLATFORM_COMPLIANCE),
        staff(UserRole.BILLING_MANAGER),
    ):
        assert client.post(ADMIN, json=entry(), headers=headers).status_code == 403
        assert client.get(ADMIN, headers=headers).status_code == 403
    assert client.post(ADMIN, json=entry(), headers=super_admin).status_code == 201
    assert client.post(ADMIN, json=entry(slug="autre")).status_code == 401
    audit = [i["action"] for i in client.get("/api/v1/audit-logs?page_size=200", headers=super_admin).json()["items"]]
    assert "cms.created" in audit
