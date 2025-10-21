# AI Agent HubSpot Automation — Run & Setup Guide
In this project we implements an AI-driven multi-agent workflow that parses natural language, performs HubSpot CRM operations, and sends email notifications. All agents use Gemini (ChatGoogleGenerativeAI) as the single LLM. Email sending supports SMTP or Mailgun.





AI Agent HubSpot Automation - Workflow Architecture
graph LR
    A[User Query] --> B[Orchestrator Agent]
    B --> C[HubSpot Agent]
    C --> D[Email Agent]
    D --> E[End]

Detailed Component Flow
1. Graph Building (LangGraph)
def build_graph():
    """Builds the workflow graph with LangGraph."""
    nodes = {
        "orchestrator": orchestrator_node,
        "hubspot": hubspot_node,
        "email": email_node,
        "error_handler": error_handler_node
    }
    
    # Create state graph
    graph = StateGraph(nodes=nodes)
    
    # Define routing logic
    graph.add_edge("orchestrator", "hubspot")
    graph.add_conditional_edges(
        "hubspot",
        lambda x: "email" if x.get("success") else "error_handler",
        {"email": email_node, "error_handler": error_handler_node}
    )
    
    # Set entry/exit
    graph.set_entry_point("orchestrator")
    graph.add_terminal_node("email")
    graph.add_terminal_node("error_handler")
    
    return graph.compile()


 2. Agent Components
Orchestrator Agent

Parses natural language queries
Uses Gemini to extract intent and payload
Example: "Create contact John Doe with email john@example.com"
Returns structured data for HubSpot operations
HubSpot Agent

Executes CRM operations via HubSpot API
Available tools:
create_contact
update_contact
create_deal
update_deal
create_company
Uses Gemini to select appropriate tool
Email Agent

Sends notifications after successful operations
Supports two providers:
SMTP (default)
Mailgun
Uses Gemini for email content generation




3. State Management
class AgentState(TypedDict):
    """State object passed between agents."""
    query: str                    # Original user query
    messages: List[str]           # Conversation history
    parsed_data: Dict[str, Any]   # Structured data from orchestrator
    hubspot_result: Dict[str, Any]  # Result from HubSpot operation
    email_result: Dict[str, Any]  # Email send status


4. Example Flow

User Input:
"Create a new contact for John Doe with email john@example.com"

Orchestrator Output:
{
    "intent": "create_contact",
    "payload": {
        "properties": {
            "firstname": "John",
            "lastname": "Doe",
            "email": "metaisolpak@gmail.com"
        }
    }
}


HubSpot Result:

{
    "success": true,
    "id": "51",
    "details": {
        "id": "51",
        "properties": {
            "firstname": "John",
            "lastname": "Doe",
            "email": "john@example.com"
        }
    }
}


Email Notification:
ends confirmation email using configured provider
Returns success/failure status
5. Error Handling
Each agent has retry logic (tenacity)
Failed states route to error_handler_node
Logging at each step (app.log)
6. Configuration
All agents use Gemini (ChatGoogleGenerativeAI)
Single config.json for all settings
Environment variables override config.json
This workflow design provides:

Modular agent components
Clear state management
Flexible routing
Consistent error handling
Easy configuration











---

## Table of contents

- Prerequisites
- Quick start (Windows)
- Detailed setup
  - Clone repository
  - Create & activate virtual environment (Windows)
  - Install dependencies
  - Create config
  - Environment variables (optional)
- Running the app
- Running tests
- CI
- Email provider options (SMTP vs Mailgun)
- Config examples
- Logs & troubleshooting
- Linting & pre-commit
- Security notes
- Where to modify behavior

---

## Prerequisites

- Python 3.10+ (CI uses 3.12)
- Git
- Gemini API key (set `gemini_api_key`)
- HubSpot API key (`hubspot_api_key`)
- SMTP credentials or Mailgun credentials if you will send email
- Recommended: virtual environment

---

## Quick start (Windows PowerShell)

1. Open PowerShell in repository root:
   e:\FastAPi\Langchain\ai-agent-hubspot-automation

2. Create and activate venv:
````powershell
python -m venv .\venv
   # PowerShell
# or for cmd:
# .\venv\Scripts\activate
pip install --upgrade pip
pip install -r
````

3. Copy and edit config:
copy  .\config.json
notepad .\config.json

4. Configuration:
Copy config.template.json to config.json and populate keys.
Required keys (must be set in config.json or via environment variables):
gemini_api_key
hubspot_api_key
sender_email
Email provider optional keys:
SMTP: smtp_host, smtp_port, smtp_username, smtp_password, smtp_use_tls
Mailgun: mailgun_api_key, mailgun_domain
You may alternatively set environment variables (recommended for secrets):
GEMINI_API_KEY, HUBSPOT_API_KEY, SENDER_EMAIL, SMTP_*, MAILGUN_*
The app uses utils.load_config which will prefer environment variables over config.json.

