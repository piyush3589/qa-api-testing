import pytest
from jsonschema import validate

from schemas import POST_SCHEMA


class TestGetPosts:
    def test_list_returns_200_and_json(self, api):
        r = api.get("/posts")
        assert r.status_code == 200
        assert "application/json" in r.headers["Content-Type"]

    def test_list_has_100_posts(self, api):
        assert len(api.get("/posts").json()) == 100

    def test_every_post_matches_schema(self, api):
        for post in api.get("/posts").json():
            validate(instance=post, schema=POST_SCHEMA)

    def test_post_ids_are_unique(self, api):
        ids = [p["id"] for p in api.get("/posts").json()]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("post_id", [1, 50, 100])
    def test_get_single_post(self, api, post_id):
        r = api.get(f"/posts/{post_id}")
        assert r.status_code == 200
        body = r.json()
        validate(instance=body, schema=POST_SCHEMA)
        assert body["id"] == post_id

    @pytest.mark.parametrize("post_id", [0, 101, 9999])
    def test_missing_post_returns_404(self, api, post_id):
        assert api.get(f"/posts/{post_id}").status_code == 404

    def test_non_numeric_id_returns_404(self, api):
        assert api.get("/posts/abc").status_code == 404

    @pytest.mark.parametrize("user_id", [1, 5, 10])
    def test_filter_by_user_id(self, api, user_id):
        posts = api.get("/posts", params={"userId": user_id}).json()
        assert len(posts) == 10
        assert all(p["userId"] == user_id for p in posts)

    def test_filter_with_no_match_returns_empty_list(self, api):
        r = api.get("/posts", params={"userId": 9999})
        assert r.status_code == 200
        assert r.json() == []


class TestCreatePost:
    def test_create_post_returns_201_with_new_id(self, api):
        payload = {"title": "qa title", "body": "qa body", "userId": 1}
        r = api.post("/posts", json=payload)
        assert r.status_code == 201
        body = r.json()
        assert body["title"] == payload["title"]
        assert body["body"] == payload["body"]
        assert body["userId"] == payload["userId"]
        assert isinstance(body["id"], int)

    def test_create_post_with_empty_body_still_gets_id(self, api):
        # JSONPlaceholder does not validate input; this documents that behaviour.
        r = api.post("/posts", json={})
        assert r.status_code == 201
        assert "id" in r.json()


class TestUpdateAndDeletePost:
    def test_put_replaces_post(self, api):
        payload = {"id": 1, "title": "new", "body": "new body", "userId": 1}
        r = api.put("/posts/1", json=payload)
        assert r.status_code == 200
        assert r.json()["title"] == "new"

    def test_patch_updates_only_given_field(self, api):
        r = api.patch("/posts/1", json={"title": "patched"})
        assert r.status_code == 200
        body = r.json()
        assert body["title"] == "patched"
        assert body["userId"] == 1  # untouched field is preserved

    def test_delete_post(self, api):
        r = api.delete("/posts/1")
        assert r.status_code == 200
        assert r.json() == {}

    def test_update_missing_post_returns_404(self, api):
        assert api.put("/posts/9999", json={"title": "x"}).status_code == 404
