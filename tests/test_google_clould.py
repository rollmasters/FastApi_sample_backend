import base64
import json
from unittest.mock import patch
from fastapi.testclient import TestClient


# Test data
mock_project_data = {
    "projects": [
        {
            "projectName": "Project1",
            "images": [
                {
                    "id": 0,
                    "image": "images/project1/360image1.jpg",
                    "coordinates": [
                        {
                            "x": 0.5,
                            "y": 1.0,
                            "z": -0.5,
                            "image": "images/project1/point1.jpg",
                            "description": "Clickable point 1"
                        }
                    ]
                }
            ]
        }
    ]
}

mock_image_data = b"image binary content"


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_coordinates_success(mock_get_file_from_gcs, test_client: TestClient):
    # Mock the GCS response
    mock_get_file_from_gcs.return_value = json.dumps(mock_project_data)

    response = test_client.get("api/v2/get-coordinates/Project1")
    assert response.status_code == 200
    assert response.json()["projectName"] == "Project1"
    assert len(response.json()["images"]) == 1


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_coordinates_not_found(mock_get_file_from_gcs, test_client: TestClient):
    mock_get_file_from_gcs.return_value = json.dumps(mock_project_data)

    response = test_client.get("api/v2/get-coordinates/UnknownProject")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'UnknownProject' not found."


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_image_success(mock_get_file_from_gcs, test_client: TestClient):
    # Mock the GCS response for the image
    mock_get_file_from_gcs.return_value = mock_image_data

    response = test_client.get("api/v2/get-image/images/project1/360image1.jpg")
    assert response.status_code == 200

    # Ensure the returned content is base64 encoded
    image_base64 = response.json()["image_base64"]
    decoded_image = base64.b64decode(image_base64)
    assert decoded_image == mock_image_data


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_image_not_found(mock_get_file_from_gcs, test_client: TestClient):
    mock_get_file_from_gcs.side_effect = FileNotFoundError("Image not found")

    response = test_client.get("api/v2/get-image/images/unknown.jpg")
    assert response.status_code == 404
    assert response.json()["detail"] == "Image not found"


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_image_success(mock_get_file_from_gcs, test_client: TestClient):
    # Mock the GCS response for the image
    mock_get_file_from_gcs.return_value = mock_image_data

    response = test_client.get("api/v2/get-image/images/project1/360image1.jpg")

    assert response.status_code == 200
    assert "image_base64" in response.json()

    # Ensure the returned content is base64 encoded
    image_base64 = response.json()["image_base64"]
    decoded_image = base64.b64decode(image_base64)
    assert decoded_image == mock_get_file_from_gcs.return_value


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_image_not_found(mock_get_file_from_gcs, test_client: TestClient):
    # Mock GCS to raise a FileNotFoundError
    mock_get_file_from_gcs.side_effect = FileNotFoundError("Image not found")

    response = test_client.get("api/v2/get-image/images/project1/unknown_image.jpg")

    assert response.status_code == 404
    assert response.json()["detail"] == "Image not found"


@patch("app.api.v2.endpoints.google_cloud.get_file_from_gcs")
def test_get_image_server_error(mock_get_file_from_gcs, test_client: TestClient):
    # Mock GCS to raise a general exception
    mock_get_file_from_gcs.side_effect = Exception("Unexpected error")

    response = test_client.get("api/v2/get-image/images/project1/error.jpg")

    assert response.status_code == 500
    assert response.json()["detail"] == "Error: Unexpected error"