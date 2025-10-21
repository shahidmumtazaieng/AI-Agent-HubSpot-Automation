# AI Agent HubSpot Automation — Run & Setup Guide
In this project we implements an AI-driven multi-agent workflow that parses natural language, performs HubSpot CRM operations, and sends email notifications. All agents use Gemini (ChatGoogleGenerativeAI) as the single LLM. Email sending supports SMTP or Mailgun.





![Workflow: AI Agent HubSpot Automation](assets/workflow.svg)
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 220" width="1000" height="220" role="img" aria-label="AI Agent HubSpot Automation workflow">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
      <path d="M0 0 L10 5 L0 10 z" fill="#2b6cb0"/>
    </marker>
    <style>
      .box { fill:#edf2ff; stroke:#2b6cb0; stroke-width:2; rx:8; ry:8; }
      .label { font: 16px/1.2 Inter, Arial, sans-serif; fill:#0f172a; font-weight:600; }
      .sub { font: 12px/1.2 Inter, Arial, sans-serif; fill:#334155; }
      .arrow { stroke:#2b6cb0; stroke-width:2.5; fill:none; marker-end:url(#arrow); }
    </style>
  </defs>

  <!-- Boxes -->
  <rect class="box" x="40"  y="40" width="180" height="90" />
  <text class="label" x="130" y="68" text-anchor="middle">User Query</text>
  <text class="sub" x="130" y="90" text-anchor="middle">Natural language</text>

  <rect class="box" x="260" y="40" width="200" height="90" />
  <text class="label" x="360" y="68" text-anchor="middle">Orchestrator Agent</text>
  <text class="sub" x="360" y="90" text-anchor="middle">Parse intent & payload</text>

  <rect class="box" x="490" y="40" width="200" height="90" />
  <text class="label" x="590" y="68" text-anchor="middle">HubSpot Agent</text>
  <text class="sub" x="590" y="90" text-anchor="middle">Perform CRM ops</text>

  <rect class="box" x="720" y="40" width="180" height="90" />
  <text class="label" x="810" y="68" text-anchor="middle">Email Agent</text>
  <text class="sub" x="810" y="90" text-anchor="middle">Send notification</text>

  <rect class="box" x="880" y="40" width="60" height="90" />
  <text class="label" x="910" y="68" text-anchor="middle">End</text>

  <!-- Arrows -->
  <path class="arrow" d="M220 85 L260 85" />
  <path class="arrow" d="M460 85 L490 85" />
  <path class="arrow" d="M690 85 L720 85" />
  <path class="arrow" d="M900 85 L880 85" transform="translate(0,0)"/>

  <!-- Optional notes -->
  <text class="sub" x="360" y="135" text-anchor="middle">Single LLM (Gemini) drives each agent</text>
</svg>

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
    orchestrator_node, hubspot_node, email_node, error_handler_node
    
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


 3. Agent Components
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


