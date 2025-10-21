# tests/test_orchestrator.py
import pytest
from unittest.mock import patch
from agents.orchestrator import OrchestratorAgent
from utils import load_config

@pytest.fixture
def config():
    return load_config()

@pytest.fixture
def orchestrator(config):
    return OrchestratorAgent(config)

@patch('langchain.agents.AgentExecutor.invoke')
def test_orchestrator_create_contact(mock_invoke, orchestrator):
    mock_invoke.return_value = {'output': {'intent': 'create_contact', 'payload': {'properties': {'firstname': 'John', 'lastname': 'Doe', 'email': 'john@example.com'}}}}
    result = orchestrator.run("Create a new contact for John Doe with email john@example.com")
    assert result['intent'] == 'create_contact'
    assert 'properties' in result['payload']

@patch('langchain.agents.AgentExecutor.invoke')
def test_orchestrator_update_contact(mock_invoke, orchestrator):
    mock_invoke.return_value = {'output': {'intent': 'update_contact', 'payload': {'id': '123', 'properties': {'phone': '123-456-7890'}}}}
    result = orchestrator.run("Update contact with ID 123 to have phone number 123-456-7890")
    assert result['intent'] == 'update_contact'
    assert 'id' in result['payload']

@patch('langchain.agents.AgentExecutor.invoke')
def test_orchestrator_create_deal(mock_invoke, orchestrator):
    mock_invoke.return_value = {'output': {'intent': 'create_deal', 'payload': {'properties': {'dealname': 'New Deal', 'amount': '1000'}}}}
    result = orchestrator.run("Create a new deal named New Deal with amount 1000")
    assert result['intent'] == 'create_deal'
    assert 'properties' in result['payload']

@patch('langchain.agents.AgentExecutor.invoke')
def test_orchestrator_update_deal(mock_invoke, orchestrator):
    mock_invoke.return_value = {'output': {'intent': 'update_deal', 'payload': {'id': '456', 'properties': {'dealstage': 'appointmentscheduled'}}}}
    result = orchestrator.run("Update deal with ID 456 to stage appointmentscheduled")
    assert result['intent'] == 'update_deal'
    assert 'id' in result['payload']

@patch('langchain.agents.AgentExecutor.invoke')
def test_orchestrator_create_company(mock_invoke, orchestrator):
    mock_invoke.return_value = {'output': {'intent': 'create_company', 'payload': {'properties': {'name': 'New Company', 'domain': 'example.com'}}}}
    result = orchestrator.run("Create a new company named New Company with domain example.com")
    assert result['intent'] == 'create_company'
    assert 'properties' in result['payload']

def test_orchestrator_error(orchestrator):
    with pytest.raises(Exception):
        orchestrator.run("")  # Empty query