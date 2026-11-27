import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data(monkeypatch):
    activities = copy.deepcopy({
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["existing@mergington.edu"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Mondays",
            "max_participants": 1,
            "participants": [],
        },
    })
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client
