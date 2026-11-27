import copy

import pytest


def test_root_redirects_to_web_app(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_list_activities(client, activity_data):
    # Arrange
    expected = copy.deepcopy(activity_data)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_normalizes_email_and_updates_listing(client):
    # Arrange
    email = "  Student@MERGINGTON.EDU  "

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@mergington.edu for Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "existing@mergington.edu", "student@mergington.edu"
    ]


def test_unregister_matches_normalized_existing_email_and_updates_listing(client, activity_data):
    # Arrange
    activity_data["Chess Club"]["participants"] = [" Existing@MERGINGTON.EDU "]

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": "existing@mergington.edu"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered existing@mergington.edu from Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


@pytest.mark.parametrize("method", ["post", "delete"])
@pytest.mark.parametrize("email", ["student@mergington.edu", "not-an-email"])
def test_unknown_activity_takes_precedence_over_supplied_email(client, activity_data, method, email):
    # Arrange
    original = copy.deepcopy(activity_data)

    # Act
    response = client.request(method, "/activities/Missing/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_data == original


@pytest.mark.parametrize("method", ["post", "delete"])
@pytest.mark.parametrize("activity", ["Chess Club", "Missing"])
def test_missing_email_is_rejected(client, activity_data, method, activity):
    # Arrange
    original = copy.deepcopy(activity_data)

    # Act
    response = client.request(method, f"/activities/{activity}/signup")

    # Assert
    assert response.status_code == 422
    assert activity_data == original


@pytest.mark.parametrize("method", ["post", "delete"])
@pytest.mark.parametrize("email", [
    "",
    "not-an-email",
    "student@example.com",
    "student@sub.mergington.edu",
    "student@mergington.edu.example.com",
])
def test_invalid_or_non_school_email_is_rejected(client, activity_data, method, email):
    # Arrange
    original = copy.deepcopy(activity_data)

    # Act
    response = client.request(method, "/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert activity_data == original


def test_duplicate_signup_matches_normalized_existing_email(client, activity_data):
    # Arrange
    activity_data["Chess Club"]["participants"] = [" Existing@MERGINGTON.EDU "]
    original = copy.deepcopy(activity_data)

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": "existing@mergington.edu"}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activity_data == original


def test_unregister_nonparticipant(client, activity_data):
    # Arrange
    original = copy.deepcopy(activity_data)

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": "other@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert activity_data == original


def test_signup_rejects_full_activity(client, activity_data):
    # Arrange
    activity_data["Art Club"]["participants"] = ["existing@mergington.edu"]
    original = copy.deepcopy(activity_data)

    # Act
    response = client.post("/activities/Art Club/signup", params={"email": "new@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert activity_data == original


def test_duplicate_error_takes_precedence_when_activity_is_full(client, activity_data):
    # Arrange
    activity_data["Art Club"]["participants"] = ["existing@mergington.edu"]
    original = copy.deepcopy(activity_data)

    # Act
    response = client.post(
        "/activities/Art Club/signup", params={"email": " EXISTING@mergington.edu "}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activity_data == original
