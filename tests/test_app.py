import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = copy.deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"] == activities["Chess Club"]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new.student@mergington.edu for Chess Club"
    }
    assert "new.student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_rejects_participant_not_signed_up(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "not.signed.up@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_remove_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
