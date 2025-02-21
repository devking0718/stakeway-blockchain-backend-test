import pytest
from fastapi.testclient import TestClient
from app.main import app
import re

client = TestClient(app)

# Test constants
TEST_FEE_RECIPIENT = "0x1234567890abcdef1234567890abcdef12345678"

def test_create_validator_request():
    response = client.post("/validators", json={
        "num_validators": 2,
        "fee_recipient": TEST_FEE_RECIPIENT
    })
    assert response.status_code == 200
    assert "request_id" in response.json()
    assert "message" in response.json()

def test_invalid_eth_address():
    response = client.post("/validators", json={
        "num_validators": 2,
        "fee_recipient": "invalid_address"
    })
    assert response.status_code == 422

def test_invalid_num_validators():
    response = client.post("/validators", json={
        "num_validators": 0,
        "fee_recipient": TEST_FEE_RECIPIENT
    })
    assert response.status_code == 422

def test_get_validator_request():
    num_validators = 2
    # First create a validator request
    create_response = client.post("/validators", json={
        "num_validators": num_validators,
        "fee_recipient": TEST_FEE_RECIPIENT
    })
    assert create_response.status_code == 200
    request_id = create_response.json()["request_id"]
    
    # Then get the validator request using the request_id
    get_response = client.get(f"/validators/{request_id}")
    assert get_response.status_code == 200
    
    # Check response structure
    response_data = get_response.json()
    assert "status" in response_data
    assert "keys" in response_data
    
    # Check status value is valid
    assert response_data["status"] in ["started", "successful", "failed"]
    
    # If status is successful, check keys is a list with correct number of validators
    if response_data["status"] == "successful":
        assert isinstance(response_data["keys"], list)
        assert len(response_data["keys"]) == num_validators

def test_get_nonexistent_validator_request():
    # Test with a non-existent request_id
    response = client.get("/validators/nonexistent_id")
    assert response.status_code == 404 
    
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "unhealthy"]