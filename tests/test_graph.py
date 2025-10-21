# tests/test_graph.py
import pytest
from unittest.mock import patch, MagicMock
from graph import build_graph, AgentState, router

def test_router_orchestrator_to_hubspot():
    """Test router when orchestrator has parsed data with HubSpot intent."""
    state: AgentState = {
        "query": "",
        "parsed_data": {"intent": "create_contact", "payload": {}},
        "hubspot_result": {},
        "email_result": {},
        "messages": [],
        "error": ""
    }
    assert router(state) == "hubspot"

def test_router_hubspot_to_email():
    """Test router when HubSpot operation succeeded."""
    state: AgentState = {
        "query": "",
        "parsed_data": {},
        "hubspot_result": {"success": True},
        "email_result": {},
        "messages": [],
        "error": ""
    }
    assert router(state) == "email"

def test_router_error_handling():
    """Test router when there's an error."""
    state: AgentState = {
        "query": "",
        "parsed_data": {},
        "hubspot_result": {},
        "email_result": {},
        "messages": [],
        "error": "Something went wrong"
    }
    assert router(state) == "error_handler"

def test_router_end_condition():
    """Test router when workflow should end."""
    state: AgentState = {
        "query": "",
        "parsed_data": {},
        "hubspot_result": {},
        "email_result": {"success": True},
        "messages": [],
        "error": ""
    }
    assert router(state) == "END"

@patch('graph.PostgresSaver')
def test_build_graph_success(mock_saver):
    """Test that graph builds successfully with mocked persistence."""
    # Mock the checkpointer
    mock_checkpointer = MagicMock()
    mock_saver.from_conn_string.return_value.__enter__.return_value = mock_checkpointer
    
    # This should not raise an exception
    graph = build_graph()
    assert graph is not None

@patch('graph.PostgresSaver')
def test_build_graph_missing_db_uri(mock_saver):
    """Test that graph building fails when DB URI is missing."""
    # Mock the checkpointer
    mock_checkpointer = MagicMock()
    mock_saver.from_conn_string.return_value.__enter__.return_value = mock_checkpointer
    
    with patch('utils.load_config') as mock_load_config:
        mock_load_config.return_value = {}  # Empty config without neon_db_uri
        
        with pytest.raises(ValueError, match="Neon DB URI not found in config"):
            build_graph()