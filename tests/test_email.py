# tests/test_email.py
import pytest
from unittest.mock import patch, MagicMock
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
            "metaisolpak@gmail.com",
            {"success": True, "id": "123", "details": {"firstname": "John", "lastname": "Doe"}}
        )

def test_email_agent_initialization_error():
    with pytest.raises(Exception):
        # Create an EmailAgent with invalid config to trigger an error
        invalid_config = {}
        email_agent = EmailAgent(invalid_config)

def get_contact_by_email(self, email: str):
    # call search API; return contact id if exists
    pass

def upsert_contact(self, payload):
    email = payload.get('properties', {}).get('email')
    existing = self.get_contact_by_email(email)
    if existing:
        return self.update_contact({'id': existing, 'properties': payload['properties']})
    else:
        return self.create_contact(payload)

@pytest.fixture
def mailjet_config():
    return {
        "email_provider": "mailjet",
        "mailjet_api_key": "test_key",
        "mailjet_api_secret": "test_secret",
        "sender_email": "metaisolpak@gmail.com",
        "gemini_api_key": "test_gemini_key"
    }

@patch('agents.email_agent.Client')
def test_mailjet_send_success(mock_mailjet, mailjet_config):
    # Setup mock
    mock_client = MagicMock()
    mock_client.send.create.return_value.status_code = 200
    mock_client.send.create.return_value.json.return_value = {"Messages": [{"Status": "success"}]}
    mock_mailjet.return_value = mock_client
    
    # Create agent and send email
    agent = EmailAgent(mailjet_config)
    result = agent.run(
        "test@example.com",
        {"success": True, "details": "Test message"}
    )
    
    # Verify
    assert result.get("success") is True
    mock_client.send.create.assert_called_once()