import stat

import pytest

from conftest import OPENAKADEMEIA_REPO
from plato.client import PlatoClient, PlatoError

app = pytest.importorskip("app", reason="openakademeia server not found; set OPENAKADEMEIA_REPO")
testclient = pytest.importorskip("fastapi.testclient")

COURSE = ("mathematics", "algebra", "linear-algebra")


@pytest.fixture
def http(tmp_path):
    """The real server, in-process, on a throwaway database."""
    return testclient.TestClient(app.create_app(OPENAKADEMEIA_REPO / "content", f"sqlite:///{tmp_path / 'db.sqlite'}"))


@pytest.fixture
def token_path(tmp_path):
    return tmp_path / "token"


@pytest.fixture
def plato(http, token_path):
    return PlatoClient(http, token_path)


def test_first_use_signs_up_and_persists_the_token(http, token_path):
    plato = PlatoClient(http, token_path)

    progress = plato.progress()

    assert progress["plan"] == "free"
    assert token_path.read_text().strip() == plato.token
    assert PlatoClient(http, token_path).token == plato.token


def test_token_file_and_directory_are_private_to_the_user(http, token_path):
    PlatoClient(http, token_path)

    assert stat.S_IMODE(token_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(token_path.parent.stat().st_mode) == 0o700


def test_list_courses_flattens_the_catalog(plato):
    courses = plato.list_courses()

    assert {"field": "mathematics", "subfield": "algebra", "course": "linear-algebra", "title": "Linear Algebra", "tier": "free"} in [
        {k: c[k] for k in ("field", "subfield", "course", "title", "tier")} for c in courses
    ]


def test_start_course_enrolls_and_returns_the_first_lesson(plato):
    started = plato.start_course(*COURSE)

    assert started["enrollment_id"] == 1
    assert started["done"] is False
    assert started["lesson"]["id"] == "01-two-numbers-one-arrow"
    assert started["lesson"]["text"].startswith("# Two numbers, one arrow")
    assert started["lesson"]["reading"].startswith("### Vectors are displacements")


def test_start_course_twice_resumes_the_same_enrollment(plato):
    first = plato.start_course(*COURSE)
    plato.record_attempt(first["enrollment_id"], "01-two-numbers-one-arrow", "guess", 2, "wrong")

    resumed = plato.start_course(*COURSE)

    assert resumed["enrollment_id"] == first["enrollment_id"]
    assert resumed["lesson"]["id"] == "02-tip-to-tail"


def test_record_attempt_then_next_lesson_advances(plato):
    enrollment_id = plato.start_course(*COURSE)["enrollment_id"]

    attempt = plato.record_attempt(enrollment_id, "01-two-numbers-one-arrow", "lands at (2,1)", 3, "correct", assisted=False)
    following = plato.next_lesson(enrollment_id)

    assert attempt["lesson_id"] == "01-two-numbers-one-arrow"
    assert following["lesson"]["id"] == "02-tip-to-tail"


def test_progress_reports_streak_and_enrollments(plato):
    enrollment_id = plato.start_course(*COURSE)["enrollment_id"]
    plato.record_attempt(enrollment_id, "01-two-numbers-one-arrow", "x", 1, "wrong")

    progress = plato.progress()

    assert progress["streak_weeks"] == 1
    assert progress["enrollments"][0]["completed"] == 1


def test_server_errors_surface_as_plato_errors(plato):
    with pytest.raises(PlatoError, match="course not found"):
        plato.start_course("mathematics", "algebra", "topology")
