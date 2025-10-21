from typing import TypedDict, Annotated, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver  # Use Neon PostgreSQL
from utils import logger, load_config
from agents.orchestrator import OrchestratorAgent
from agents.hubspot_agent import HubSpotAgent
from agents.email_agent import EmailAgent

# State Schema
class AgentState(TypedDict):
    """Shared state for the multi-agent workflow."""
    query: str
    parsed_data: Dict[str, Any]
    hubspot_result: Dict[str, Any]
    email_result: Dict[str, Any]
    messages: Annotated[list, add_messages]
    error: str

# Node Functions and Router
config = load_config()
orchestrator = OrchestratorAgent(config)
hubspot = HubSpotAgent(config)
email_agent = EmailAgent(config)

def orchestrator_node(state: AgentState) -> AgentState:
    """Run Orchestrator to parse query."""
    try:
        parsed = orchestrator.run(state['query'])
        logger.info(f"Parsed data: {parsed}")
        return {"parsed_data": parsed, "messages": state['messages'] + [{"role": "orchestrator", "content": parsed}]}
    except Exception as e:
        logger.error(f"Orchestrator node error: {str(e)}")
        return {"error": str(e)}

def hubspot_node(state: AgentState) -> AgentState:
    """Run HubSpot based on parsed intent/payload."""
    if not state.get('parsed_data'):
        return {"error": "No parsed data available"}
    try:
        intent = state['parsed_data'].get('intent')
        payload = state['parsed_data'].get('payload', {})
        result = hubspot.run(intent, payload)
        logger.info(f"HubSpot node result: {result}")
        return {"hubspot_result": result, "messages": state['messages'] + [{"role": "hubspot", "content": result}]}
    except Exception as e:
        logger.error(f"HubSpot node error: {str(e)}")
        return {"error": str(e)}

def email_node(state: AgentState) -> AgentState:
    """Run Email if HubSpot succeeded."""
    if not state.get('hubspot_result', {}).get('success'):
        return {"error": "HubSpot failed, skipping email"}
    try:
        # Extract email from the payload or use a default from config
        to_email = state['parsed_data'].get('payload', {}).get('properties', {}).get('email')
        if not to_email:
            # Fallback to a default email from config or use a generic one
            to_email = "user@example.com"  # In a real app, this should come from config
        result = email_agent.run(to_email, state['hubspot_result'])
        logger.info(f"Email node result: {result}")
        return {"email_result": result, "messages": state['messages'] + [{"role": "email", "content": result}]}
    except Exception as e:
        logger.error(f"Email node error: {str(e)}")
        return {"error": str(e)}

def error_handler_node(state: AgentState) -> AgentState:
    """Handle errors gracefully."""
    error_msg = state.get('error', "Unknown error")
    logger.warning(f"Error handled: {error_msg}")
    return {"messages": state['messages'] + [{"role": "error", "content": error_msg}]}

def router(state: AgentState) -> str:
    """Decide next node based on state."""
    if state.get('error'):
        return "error_handler"
    if state.get('parsed_data'):
        intent = state['parsed_data'].get('intent', '')
        if intent in ["create_contact", "update_contact", "create_deal", "update_deal", "create_company"]:
            return "hubspot"
        else:
            return END
    if state.get('hubspot_result', {}).get('success'):
        return "email"
    if state.get('email_result'):
        return END
    return "error_handler"

# Build Graph with Neon PostgreSQL
def build_graph() -> StateGraph:
    """Build and compile the LangGraph workflow with Neon PostgreSQL persistence."""
    graph_builder = StateGraph(state_schema=AgentState)
    
    # Add nodes
    graph_builder.add_node("orchestrator", orchestrator_node)
    graph_builder.add_node("hubspot", hubspot_node)
    graph_builder.add_node("email", email_node)
    graph_builder.add_node("error_handler", error_handler_node)
    
    # Edges
    graph_builder.add_edge(START, "orchestrator")
    
    # Conditional edges from orchestrator
    graph_builder.add_conditional_edges(
        "orchestrator",
        router,
        {"hubspot": "hubspot", "error_handler": "error_handler", END: END}
    )
    
    # From hubspot
    graph_builder.add_conditional_edges(
        "hubspot",
        router,
        {"email": "email", "error_handler": "error_handler", END: END}
    )
    
    # From email to end
    graph_builder.add_conditional_edges(
        "email",
        router,
        {END: END, "error_handler": "error_handler"}
    )
    
    # From error to end
    graph_builder.add_edge("error_handler", END)
    
    # Persistence with Neon PostgreSQL
    config = load_config()
    db_uri = config.get('neon_db_uri')
    if not db_uri:
        raise ValueError("Neon DB URI not found in config. Add 'neon_db_uri' to config.json.")
    
    with PostgresSaver.from_conn_string(db_uri, pipeline=True) as checkpointer:
        checkpointer.setup()  # Creates tables if needed
        graph = graph_builder.compile(checkpointer=checkpointer)
    
    logger.info("Graph compiled with Neon PostgreSQL persistence.")
    return graph