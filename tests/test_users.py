import re

import pytest
from jsonschema import validate

from schemas import USER_SCHEMA

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def test_list_returns_10_users(api):
    r = api.get("/users")
    assert r.status_code == 200
    assert len(r.json()) == 10


def test_every_user_matches_schema(api):
    for user in api.get("/users").json():
        validate(instance=user, schema=USER_SCHEMA)


def test_user_emails_are_valid_and_unique(api):
    emails = [u["email"] for u in api.get("/users").json()]
    assert all(EMAIL_RE.match(e) for e in emails)
    assert len(emails) == len(set(emails))


@pytest.mark.parametrize("user_id", [1, 10])
def test_get_single_user(api, user_id):
    r = api.get(f"/users/{user_id}")
    assert r.status_code == 200
    assert r.json()["id"] == user_id


def test_missing_user_returns_404(api):
    assert api.get("/users/9999").status_code == 404


def test_user_posts_belong_to_user(api):
    # Cross-resource consistency: every post of user 3 must reference user 3.
    posts = api.get("/posts", params={"userId": 3}).json()
    assert posts, "expected at least one post for user 3"
    assert {p["userId"] for p in posts} == {3}
