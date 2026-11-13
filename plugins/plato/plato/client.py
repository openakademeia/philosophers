"""HTTP client for the openakademeia Plato API; owns the learner token."""

import os
from pathlib import Path

import httpx

DEFAULT_URL = "http://localhost:8080"
DEFAULT_TOKEN_DIR = Path.home() / ".openakademeia"


class PlatoError(Exception):
    """The server refused a request; the message is the server's detail."""


def default_token_path(url: str) -> Path:
    host = httpx.URL(url).host or "local"
    return DEFAULT_TOKEN_DIR / f"{host}.token"


class PlatoClient:
    def __init__(self, http: httpx.Client, token_path: Path):
        self.http = http
        self.token_path = token_path
        self.token = os.environ.get("OPENAKADEMEIA_TOKEN") or self._load_or_create_token()

    def _load_or_create_token(self) -> str:
        if self.token_path.exists():
            self.token_path.chmod(0o600)
            return self.token_path.read_text().strip()
        token = self._call("POST", "/api/v1/learners", auth=False)["token"]
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.parent.chmod(0o700)
        fd = os.open(self.token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(token + "\n")
        return token

    def _call(self, method: str, path: str, auth: bool = True, **kwargs) -> dict | list:
        headers = {"Authorization": f"Bearer {self.token}"} if auth else {}
        response = self.http.request(method, path, headers=headers, **kwargs)
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise PlatoError(f"{response.status_code}: {detail}")
        return response.json()

    def list_courses(self) -> list[dict]:
        return [
            {
                "field": field["id"],
                "subfield": subfield["id"],
                "course": course["id"],
                "title": course["title"],
                "summary": course.get("summary", ""),
                "tier": course["tier"],
                "status": course.get("status", ""),
            }
            for field in self._call("GET", "/api/v1/catalog", auth=False)
            for subfield in field["subfields"]
            for course in subfield["courses"]
        ]

    def start_course(self, field: str, subfield: str, course: str) -> dict:
        existing = next(
            (
                e
                for e in self._call("GET", "/api/v1/enrollments")
                if (e["field"], e["subfield"], e["course"]) == (field, subfield, course)
            ),
            None,
        )
        enrollment = existing or self._call(
            "POST", "/api/v1/enrollments", json={"field": field, "subfield": subfield, "course": course}
        )
        return self.next_lesson(enrollment["id"])

    def next_lesson(self, enrollment_id: int) -> dict:
        return {"enrollment_id": enrollment_id, **self._call("GET", f"/api/v1/enrollments/{enrollment_id}/next")}

    def record_attempt(
        self,
        enrollment_id: int,
        lesson_id: str,
        commit: str,
        confidence: int,
        outcome: str,
        assisted: bool = False,
        artifact_result: str | None = None,
    ) -> dict:
        return self._call(
            "POST",
            f"/api/v1/enrollments/{enrollment_id}/attempts",
            json={
                "lesson_id": lesson_id,
                "commit": commit,
                "confidence": confidence,
                "outcome": outcome,
                "assisted": assisted,
                "artifact_result": artifact_result,
            },
        )

    def progress(self) -> dict:
        return self._call("GET", "/api/v1/me")


def connect(url: str | None = None) -> PlatoClient:
    base = url or os.environ.get("OPENAKADEMEIA_URL", DEFAULT_URL)
    return PlatoClient(httpx.Client(base_url=base, timeout=30), default_token_path(base))
