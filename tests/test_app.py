import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import app as application
import app as application


client = TestClient(application.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "not-ready"]


def test_metrics_endpoint():
    response = client.get("/metrics")

    assert response.status_code == 200

    data = response.json()

    assert data["student_id"] == "FA23-BDS-044"
    assert isinstance(data["accuracy"], (int, float))
    assert isinstance(data["training_rows"], int)
    assert "model_version" in data
    assert "git_sha" in data


def test_prediction_endpoint():
    metrics = client.get("/metrics")

    assert metrics.status_code == 200

    from pathlib import Path
    import json

    config = json.loads(Path("config.json").read_text())
    features = config["features"]

    records = [
        {feature: 1 for feature in features}
    ]

    response = client.post(
        "/predict",
        json={"records": records}
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result["predictions"]) == 1
    assert len(result["probabilities"]) == 1
    assert result["predictions"][0] in [0, 1]


def test_prediction_rejects_empty_records():
    response = client.post(
        "/predict",
        json={"records": []}
    )

    assert response.status_code == 422
