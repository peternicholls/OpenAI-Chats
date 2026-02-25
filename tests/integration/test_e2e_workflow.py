"""E2E integration test — full user workflow.

T037: Covers the end-to-end happy path:
  import → list conversations → search → tag → rename tag → favourite →
  export (single & batch) → delete
"""

import pytest


@pytest.mark.asyncio
class TestFullWorkflow:
    """Full end-to-end workflow through the REST API with a populated database."""

    async def test_health_check(self, client):
        """API is reachable and healthy."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"

    # ------------------------------------------------------------------
    # Conversations
    # ------------------------------------------------------------------

    async def test_list_conversations_returns_seeded_data(self, client):
        response = await client.get("/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        ids = [c["id"] for c in data["items"]]
        assert "conv-001-test" in ids

    async def test_get_single_conversation(self, client):
        response = await client.get("/api/conversations/conv-001-test")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "conv-001-test"
        assert data["title"] == "Test Conversation 1"
        assert isinstance(data.get("messages"), list)

    async def test_get_nonexistent_conversation_returns_404(self, client):
        response = await client.get("/api/conversations/does-not-exist")
        assert response.status_code == 404

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def test_search_finds_expected_conversation(self, client):
        response = await client.post("/api/search", json={"query": "machine learning"})
        assert response.status_code == 200
        data = response.json()
        ids = [r["conversation_id"] for r in data.get("items", [])]
        assert "conv-003-test" in ids

    async def test_search_empty_query_returns_422(self, client):
        response = await client.post("/api/search", json={"query": ""})
        # Either 400 (invalid query) or 422 (validation) is acceptable
        assert response.status_code in (400, 422)

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    async def test_add_tag_then_list(self, client):
        await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "e2e-tag"},
        )
        response = await client.get("/api/tags")
        assert response.status_code == 200
        names = [t["name"] for t in response.json()]
        assert "e2e-tag" in names

    async def test_rename_tag_end_to_end(self, client):
        # Add the tag
        await client.post(
            "/api/conversations/conv-002-test/tags",
            json={"tag_name": "e2e-old"},
        )
        # Rename it
        rename_resp = await client.put("/api/tags/e2e-old", json={"new_name": "e2e-new"})
        assert rename_resp.status_code in (200, 204)

        # New name visible globally
        tags_resp = await client.get("/api/tags")
        names = [t["name"] for t in tags_resp.json()]
        assert "e2e-new" in names
        assert "e2e-old" not in names

        # New name visible on conversation
        conv_tags = await client.get("/api/conversations/conv-002-test/tags")
        assert "e2e-new" in conv_tags.json()

    async def test_filter_conversations_by_tag(self, client):
        await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "filter-tag"},
        )
        response = await client.get("/api/conversations?tag=filter-tag")
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(
            any(t == "filter-tag" for t in item.get("tags", []))
            for item in items
        )

    async def test_remove_tag(self, client):
        await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "remove-me"},
        )
        del_resp = await client.delete("/api/conversations/conv-001-test/tags/remove-me")
        assert del_resp.status_code == 204

        conv_tags = await client.get("/api/conversations/conv-001-test/tags")
        assert "remove-me" not in conv_tags.json()

    # ------------------------------------------------------------------
    # Favourites
    # ------------------------------------------------------------------

    async def test_toggle_favourite_and_list(self, client):
        # Toggle on
        toggle = await client.post("/api/conversations/conv-001-test/favorite")
        assert toggle.status_code == 200

        fav_resp = await client.get("/api/favorites")
        assert fav_resp.status_code == 200
        fav_ids = [c["id"] for c in fav_resp.json()["items"]]
        assert "conv-001-test" in fav_ids

        # Toggle off
        await client.post("/api/conversations/conv-001-test/favorite")
        fav_resp2 = await client.get("/api/favorites")
        fav_ids2 = [c["id"] for c in fav_resp2.json()["items"]]
        assert "conv-001-test" not in fav_ids2

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    async def test_export_single_conversation_markdown(self, client):
        response = await client.get("/api/conversations/conv-001-test/export?format=md")
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]
        rfc_header = response.headers.get("content-disposition", "")
        # RFC 5987 encoding: expect filename*=UTF-8''
        assert "filename*=UTF-8''" in rfc_header or "filename=" in rfc_header

    async def test_export_single_conversation_json(self, client):
        response = await client.get("/api/conversations/conv-001-test/export?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    async def test_export_batch(self, client):
        response = await client.get(
            "/api/export/batch?ids=conv-001-test,conv-002-test&format=json"
        )
        assert response.status_code == 200

    async def test_export_batch_exceeds_cap_returns_422(self, client):
        """Batch cap of 500 must be enforced (T007)."""
        big_ids = ",".join(f"conv-{i:04d}" for i in range(501))
        response = await client.get(f"/api/export/batch?ids={big_ids}&format=md")
        assert response.status_code == 422

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    async def test_settings_include_items_per_page(self, client):
        response = await client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "items_per_page" in data
        assert data["items_per_page"] == 50  # default

    async def test_update_items_per_page(self, client):
        resp = await client.put("/api/settings", json={"items_per_page": 25})
        assert resp.status_code == 200
        assert resp.json()["items_per_page"] == 25

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def test_delete_conversation(self, client):
        # Use conv-003 which is less likely to affect other tests
        response = await client.delete("/api/conversations/conv-003-test")
        assert response.status_code in (200, 204)

        # Verify it's gone
        get_resp = await client.get("/api/conversations/conv-003-test")
        assert get_resp.status_code == 404
