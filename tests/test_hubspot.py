# tests/test_hubspot.py
import pytest
from unittest.mock import patch
from agents.hubspot_agent import HubSpotAgent
from utils import load_config

@pytest.fixture
def config():
    return load_config()

@pytest.fixture
def hubspot(config):
    return HubSpotAgent(config)

@patch('hubspot.crm.contacts.basic_api.BasicApi.create')
def test_create_contact(mock_create, hubspot):
    mock_create.return_value = type('obj', (object,), {'id': '123', 'properties': {}})()
    result = hubspot.run('create_contact', {'properties': {'firstname': 'Test'}})
    assert result['success'] is True
    assert result['id'] == '123'

@patch('hubspot.crm.contacts.basic_api.BasicApi.update')
def test_update_contact(mock_update, hubspot):
    mock_update.return_value = type('obj', (object,), {'id': '123', 'properties': {}})()
    result = hubspot.run('update_contact', {'id': '123', 'properties': {'phone': '123-456-7890'}})
    assert result['success'] is True
    assert result['id'] == '123'

@patch('hubspot.crm.deals.basic_api.BasicApi.create')
def test_create_deal(mock_create, hubspot):
    mock_create.return_value = type('obj', (object,), {'id': '456', 'properties': {}})()
    result = hubspot.run('create_deal', {'properties': {'dealname': 'Test Deal', 'amount': '1000'}})
    assert result['success'] is True
    assert result['id'] == '456'

@patch('hubspot.crm.deals.basic_api.BasicApi.update')
def test_update_deal(mock_update, hubspot):
    mock_update.return_value = type('obj', (object,), {'id': '456', 'properties': {}})()
    result = hubspot.run('update_deal', {'id': '456', 'properties': {'dealstage': 'appointmentscheduled'}})
    assert result['success'] is True
    assert result['id'] == '456'

@patch('hubspot.crm.companies.basic_api.BasicApi.create')
def test_create_company(mock_create, hubspot):
    mock_create.return_value = type('obj', (object,), {'id': '789', 'properties': {}})()
    result = hubspot.run('create_company', {'properties': {'name': 'Test Company', 'domain': 'test.com'}})
    assert result['success'] is True
    assert result['id'] == '789'

def test_hubspot_error():
    with pytest.raises(Exception):
        # Create a HubSpotAgent with invalid config to trigger an error
        invalid_config = {}
        hubspot = HubSpotAgent(invalid_config)
        hubspot.run('invalid_intent', {})

        