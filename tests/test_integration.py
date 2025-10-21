# tests/test_integration.py
import pytest
from unittest.mock import patch, MagicMock
from graph import build_graph, AgentState

def test_integration_success():
    """Test successful integration flow."""
    with patch('graph.PostgresSaver') as mock_saver:
        # Mock the checkpointer
        mock_checkpointer = MagicMock()
        mock_saver.from_conn_string.return_value.__enter__.return_value = mock_checkpointer
        
        # Build graph with mocked persistence
        graph = build_graph()
        
        # Test state with a create contact query
        initial_state: AgentState = {
            "query": "Create a new contact for John Doe with email john@example.com", 
            "messages": []
        }
        
        # Mock the graph execution
        with patch('agents.orchestrator.OrchestratorAgent.run') as mock_orchestrator, \
             patch('agents.hubspot_agent.HubSpotAgent.run') as mock_hubspot, \
             patch('agents.email_agent.EmailAgent.run') as mock_email:
            
            # Set up mock returns
            mock_orchestrator.return_value = {
                'intent': 'create_contact',
                'payload': {
                    'properties': {
                        'firstname': 'John',
                        'lastname': 'Doe',
                        'email': 'john@example.com'
                    }
                }
            }
            mock_hubspot.return_value = {
                'success': True,
                'id': '12345',
                'details': {'firstname': 'John', 'lastname': 'Doe', 'email': 'john@example.com'}
            }
            mock_email.return_value = {'success': True}
            
            # Execute the graph
            final_state = graph.invoke(initial_state, {"configurable": {"thread_id": "test"}})
            
            # Assertions
            assert 'hubspot_result' in final_state
            assert final_state['hubspot_result'].get('success') is True
            assert 'email_result' in final_state
            assert final_state['email_result'].get('success') is True
            assert 'error' not in final_state or not final_state['error']

def test_integration_hubspot_failure():
    """Test integration flow when HubSpot operation fails."""
    with patch('graph.PostgresSaver') as mock_saver:
        # Mock the checkpointer
        mock_checkpointer = MagicMock()
        mock_saver.from_conn_string.return_value.__enter__.return_value = mock_checkpointer
        
        # Build graph with mocked persistence
        graph = build_graph()
        
        # Test state with a create contact query
        initial_state: AgentState = {
            "query": "Create a new contact for John Doe with email john@example.com", 
            "messages": []
        }
        
        # Mock the graph execution
        with patch('agents.orchestrator.OrchestratorAgent.run') as mock_orchestrator, \
             patch('agents.hubspot_agent.HubSpotAgent.run') as mock_hubspot:
            
            # Set up mock returns
            mock_orchestrator.return_value = {
                'intent': 'create_contact',
                'payload': {
                    'properties': {
                        'firstname': 'John',
                        'lastname': 'Doe',
                        'email': 'john@example.com'
                    }
                }
            }
            mock_hubspot.return_value = {
                'success': False,
                'error': 'HubSpot API error'
            }
            
            # Execute the graph
            final_state = graph.invoke(initial_state, {"configurable": {"thread_id": "test"}})
            
            # Assertions
            assert 'hubspot_result' in final_state
            assert final_state['hubspot_result'].get('success') is False
            # Email should not be sent if HubSpot fails
            assert 'email_result' not in final_state or not final_state.get('email_result', {}).get('success')
            assert 'error' in final_state

def test_integration_orchestrator_failure():
    """Test integration flow when orchestrator fails."""
    with patch('graph.PostgresSaver') as mock_saver:
        # Mock the checkpointer
        mock_checkpointer = MagicMock()
        mock_saver.from_conn_string.return_value.__enter__.return_value = mock_checkpointer
        
        # Build graph with mocked persistence
        graph = build_graph()
        
        # Test state with an invalid query
        initial_state: AgentState = {
            "query": "", 
            "messages": []
        }
        
        # Mock the graph execution
        with patch('agents.orchestrator.OrchestratorAgent.run') as mock_orchestrator:
            
            # Set up mock to raise an exception
            mock_orchestrator.side_effect = Exception("Invalid query")
            
            # Execute the graph
            final_state = graph.invoke(initial_state, {"configurable": {"thread_id": "test"}})
            
            # Assertions
            assert 'error' in final_state
            assert 'hubspot_result' not in final_state or not final_state.get('hubspot_result', {}).get('success')