# tests/test_email.py
import pytest
from unittest.mock import patch
from agents.email_agent import EmailAgent
from utils import load_config

@pytest.fixture
def config():
    return load_config()

@pytest.fixture
def email_agent(config):
    return EmailAgent(config)

@patch('sendgrid.SendGridAPIClient.send')
def test_send_notification_success(mock_send, email_agent):
    # Mock the SendGrid response
    mock_response = type('obj', (object,), {'status_code': 202})()
    mock_send.return_value = mock_response
    
    result = email_agent.run(
        "user@example.com",
        {"success": True, "id": "123", "details": {"firstname": "John", "lastname": "Doe"}}
    )
    assert result['success'] is True

@patch('sendgrid.SendGridAPIClient.send')
def test_send_notification_failure(mock_send, email_agent):
    # Mock the SendGrid response with an error status code
    mock_response = type('obj', (object,), {'status_code': 400})()
    mock_send.return_value = mock_response
    
    with pytest.raises(Exception):
        email_agent.run(
            "user@example.com",
            {"success": True, "id": "123", "details": {"firstname": "John", "lastname": "Doe"}}
        )

def test_email_agent_initialization_error():
    with pytest.raises(Exception):
        # Create an EmailAgent with invalid config to trigger an error
        invalid_config = {}
        email_agent = EmailAgent(invalid_config)