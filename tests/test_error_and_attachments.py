"""Regression tests for rate-limit handling (429) and attachment URL resolution.

Covers two robustness gaps:

* NocoDB enforces ~5 requests/second per user and replies with HTTP 429; the
  client must raise :class:`RateLimitException` (honoring ``Retry-After``) rather
  than a generic error.
* Attachment objects expose ``signedPath`` only on local-storage backends; on
  S3-type backends only ``signedUrl`` is set. Downloads must work on both.
"""

from unittest.mock import Mock

import pytest

from nocodb_simple_client import NocoDBException, RateLimitException
from nocodb_simple_client.client import NocoDBClient


@pytest.fixture
def client(monkeypatch):
    session = Mock()
    monkeypatch.setattr("requests.Session", lambda *a, **k: session)
    c = NocoDBClient(base_url="https://test.nocodb.com", db_auth_token="test-token")
    return c


class TestRateLimitHandling:
    def _resp(self, status, json_body, headers=None):
        r = Mock()
        r.status_code = status
        r.headers = headers or {}
        if json_body is None:
            r.json.side_effect = ValueError("no json")
        else:
            r.json.return_value = json_body
        return r

    def test_429_json_raises_rate_limit_with_retry_after(self, client):
        resp = self._resp(429, {"msg": "Too Many Requests"}, headers={"Retry-After": "30"})
        with pytest.raises(RateLimitException) as exc:
            client._check_for_error(resp)
        assert exc.value.status_code == 429
        assert exc.value.retry_after == 30

    def test_429_without_retry_after_header(self, client):
        resp = self._resp(429, {"message": "slow down"})
        with pytest.raises(RateLimitException) as exc:
            client._check_for_error(resp)
        assert exc.value.retry_after is None

    def test_429_non_numeric_retry_after_is_ignored(self, client):
        resp = self._resp(429, {"message": "x"}, headers={"Retry-After": "Wed, 21 Oct"})
        with pytest.raises(RateLimitException) as exc:
            client._check_for_error(resp)
        assert exc.value.retry_after is None

    def test_429_non_json_body_still_rate_limit(self, client):
        resp = self._resp(429, None, headers={"Retry-After": "5"})
        with pytest.raises(RateLimitException) as exc:
            client._check_for_error(resp)
        assert exc.value.retry_after == 5

    def test_rate_limit_is_a_nocodb_exception(self, client):
        resp = self._resp(429, {"message": "x"})
        with pytest.raises(NocoDBException):
            client._check_for_error(resp)


class TestAttachmentUrlResolution:
    def test_local_backend_signed_path(self, client):
        info = {"title": "f.pdf", "signedPath": "dltemp/noco/x/f.pdf"}
        assert client._resolve_attachment_url(info) == (
            "https://test.nocodb.com/dltemp/noco/x/f.pdf"
        )

    def test_s3_backend_signed_url_absolute(self, client):
        info = {"title": "f.pdf", "signedUrl": "https://s3.amazonaws.com/b/f.pdf?sig=1"}
        assert client._resolve_attachment_url(info) == ("https://s3.amazonaws.com/b/f.pdf?sig=1")

    def test_signed_path_preferred_over_url(self, client):
        info = {"signedPath": "p/f.pdf", "signedUrl": "https://s3/f.pdf"}
        assert client._resolve_attachment_url(info).endswith("/p/f.pdf")

    def test_raw_url_fallback(self, client):
        info = {"title": "f", "url": "https://cdn/f.pdf"}
        assert client._resolve_attachment_url(info) == "https://cdn/f.pdf"

    def test_raw_path_fallback(self, client):
        info = {"title": "f", "path": "download/noco/f.pdf"}
        assert client._resolve_attachment_url(info).endswith("/download/noco/f.pdf")

    def test_no_usable_key_raises(self, client):
        with pytest.raises(NocoDBException) as exc:
            client._resolve_attachment_url({"title": "broken"})
        assert exc.value.error == "DOWNLOAD_ERROR"
        assert "broken" in exc.value.message


class TestV3AttachmentUploadUsesPerCellEndpoint:
    """v3 attachment upload POSTs a base64 JSON descriptor
    ({contentType, filename, file}) to the per-cell endpoint
    .../records/{recordId}/fields/{fieldId}/upload, which appends to the cell
    (verified live, releaseVersion 2026.05.2 — multipart bodies and the
    v2-storage + v3-record-PATCH flow do not persist)."""

    def test_v3_attach_posts_base64_descriptor_to_per_cell(self, monkeypatch, tmp_path):
        import base64

        get_resp = Mock()
        get_resp.status_code = 200
        # field-id resolution via the v2 table-meta endpoint
        get_resp.json.return_value = {"columns": [{"title": "File", "id": "fld_9"}]}
        percell_resp = Mock()
        percell_resp.status_code = 200
        percell_resp.json.return_value = {"id": 1, "fields": {"File": [{"title": "f.txt"}]}}

        session = Mock()
        session.get.return_value = get_resp
        session.post.return_value = percell_resp
        monkeypatch.setattr("requests.Session", lambda *a, **k: session)

        f = tmp_path / "f.txt"
        f.write_bytes(b"hello-bytes")

        client = NocoDBClient(
            base_url="https://test.nocodb.com",
            db_auth_token="test-token",
            api_version="v3",
            base_id="base1",
        )
        client.attach_file_to_record("tbl1", 1, "File", str(f))

        # Single POST to the per-cell endpoint with the base64 JSON descriptor.
        assert session.post.call_count == 1
        url = session.post.call_args.args[0]
        assert url.endswith("api/v3/data/base1/tbl1/records/1/fields/fld_9/upload")
        body = session.post.call_args.kwargs["json"]
        assert body["filename"] == "f.txt"
        assert body["contentType"] == "text/plain"
        assert base64.b64decode(body["file"]) == b"hello-bytes"
