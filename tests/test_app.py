import copy
from urllib.parse import quote


import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
DEFAULT_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))


def test_get_activities_returns_expected_structure():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_from_activity_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@student.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
