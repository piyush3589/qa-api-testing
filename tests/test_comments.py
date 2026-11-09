import pytest
from jsonschema import validate

from schemas import COMMENT_SCHEMA


def test_nested_route_returns_comments_of_post(api):
    r = api.get("/posts/1/comments")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 5
    assert all(c["postId"] == 1 for c in comments)


def test_query_route_matches_nested_route(api):
    nested = api.get("/posts/2/comments").json()
    queried = api.get("/comments", params={"postId": 2}).json()
    assert nested == queried


@pytest.mark.parametrize("post_id", [1, 20, 100])
def test_comments_match_schema(api, post_id):
    for comment in api.get(f"/posts/{post_id}/comments").json():
        validate(instance=comment, schema=COMMENT_SCHEMA)


def test_total_comments_is_500(api):
    assert len(api.get("/comments").json()) == 500


def test_comments_of_missing_post_is_empty(api):
    r = api.get("/posts/9999/comments")
    assert r.status_code == 200
    assert r.json() == []
