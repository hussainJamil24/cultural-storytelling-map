"""Tests for story submission and moderation rules."""
from conftest import auth_header, register

# a valid story payload (real Cyprus coordinates, allowed category)
STORY = {
    "title": "Test Story",
    "content": "A meaningful cultural story.",
    "latitude": 35.1856,
    "longitude": 33.3823,
    "category": "heritage",
}


def test_create_story_requires_login(client):
    # no Authorization header → should be rejected
    res = client.post("/stories", json=STORY)
    assert res.status_code == 401


def test_create_story_when_logged_in(client):
    headers = auth_header(client)
    res = client.post("/stories", json=STORY, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Test Story"
    assert body["status"] == "pending"  # new stories await moderation


def test_invalid_category_rejected(client):
    headers = auth_header(client)
    bad = {**STORY, "category": "not-a-real-category"}
    res = client.post("/stories", json=bad, headers=headers)
    assert res.status_code == 422  # validation error


def test_anonymous_story_hides_user_id(client):
    headers = auth_header(client)
    res = client.post("/stories", json={**STORY, "is_anonymous": True}, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert body["is_anonymous"] is True
    assert body["user_id"] is None  # author hidden from the response


def test_moderation_requires_admin(client):
    # a regular (non-admin) user submits a story...
    headers = auth_header(client)
    story_id = client.post("/stories", json=STORY, headers=headers).json()["id"]

    # ...and tries to approve it themselves → forbidden
    res = client.patch(
        f"/stories/{story_id}/status",
        json={"status": "approved"},
        headers=headers,
    )
    assert res.status_code == 403


def test_public_only_sees_approved_stories(client):
    headers = auth_header(client)
    client.post("/stories", json=STORY, headers=headers)  # stays pending

    # public listing (no auth) should not include the pending story
    res = client.get("/stories")
    assert res.status_code == 200
    assert res.json() == []
