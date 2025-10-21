# AI Agent HubSpot Automation

An AI-driven multi-agent workflow that automates HubSpot CRM operations using natural language processing, with integrated email notifications. Built with LangGraph and Gemini LLM.

## 🚀 Features

- Natural language processing for CRM operations
- HubSpot API integration for contact/deal management
- Email notifications via Mailjet
- State persistence with Neon PostgreSQL
- Webhook support for HubSpot events

## 📊 Architecture

![Workflow Architecture](assets/workflow.svg)

### Component Flow

1. **Orchestrator Agent**
   - Processes natural language queries
   - Extracts intent and payload
   - Uses Gemini for understanding

2. **HubSpot Agent**
   - Executes CRM operations
   - Manages contacts, deals, companies
   - Tools:
     - create_contact
     - update_contact
     - create_deal
     - update_deal
     - create_company

3. **Email Agent**
   - Sends operation confirmations
   - Supports Mailjet integration
   - Template-based notifications

## 🛠 Prerequisites

- Python 3.10+
- Gemini API key
- HubSpot API key
- Mailjet credentials
- PostgreSQL database (optional)

## 📦 Installation

```powershell
# Clone repository
git clone <repo-url>
cd ai-agent-hubspot-automation

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure
copy config.template.json config.json
# Edit config.json with your API keys
```

## ⚙️ Configuration

Create `config.json` with your credentials:

```json
{
    "gemini_api_key": "your-gemini-key",
    "hubspot_api_key": "your-hubspot-key",
    "email_provider": "mailjet",
    "mailjet_api_key": "your-mailjet-key",
    "mailjet_api_secret": "your-mailjet-secret",
    "sender_email": "your-verified@email.com",
    "gemini_model": "gemini-2.5-flash",
    "gemini_temperature": 0.0
}
```

## 🚀 Usage

### Running the Application

```powershell
# Start the FastAPI server
python main.py
```

### Example Operations

1. Create Contact:
```python
"Create a contact named John Doe with email metaisolpak@gmail.com"
```

2. Update Deal:
```python
"Update deal 123 status to closed won"
```

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_email.py -v

# Run with coverage
pytest --cov=agents tests/
```

## 📝 State Management

```python
class AgentState(TypedDict):
    query: str                    # Original query
    messages: List[str]          # Conversation history
    parsed_data: Dict[str, Any]  # Structured data
    hubspot_result: Dict[str, Any]  # Operation result
    email_result: Dict[str, Any]  # Email status
```

## 🔄 Workflow Example

1. **User Query**:
```json
"Create a new contact for John Doe with email metaisolpak@gmail.com"
```

2. **Orchestrator Output**:
```json
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
```

3. **HubSpot Result**:
```json
{
    "success": true,
    "id": "51",
    "details": {
        "properties": {
            "firstname": "John",
            "lastname": "Doe",
            "email": "metaisolpak@gmail.com"
        }
    }
}
```

## 🔒 Security

- Never commit API keys
- Use environment variables in production
- Rotate keys regularly
- Set up webhook authentication

## 📊 Monitoring

- Check `app.log` for detailed logs
- Configure error notifications
- Monitor HubSpot API quota
- Track email delivery rates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- LangGraph team
- HubSpot API
- Mailjet team
- Google Gemini

## 📞 Support

- Open an issue
- Email: metaisolpak@gmail.com
- Documentation: [Wiki](wiki)

