# agents/email_agent.py
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.tools import create_openai_tools_agent
from langchain.agents import AgentExecutor

import smtplib
import ssl
from email.message import EmailMessage
import requests
import os
from utils import logger, load_config
from tenacity import retry, stop_after_attempt, wait_exponential

class EmailAgent:
    """Email Agent: Sends notifications via configurable provider (smtp or mailgun)."""
    
    def __init__(self, config: Dict[str, str]):
        # Use Gemini (ChatGoogleGenerativeAI) for all agent LLM calls
        self.llm = ChatGoogleGenerativeAI(
            model=config.get("gemini_model", "gemini-2.5-flash"),
            google_api_key=config['gemini_api_key'],
            temperature=float(config.get("gemini_temperature", 0.0))
        )
        self.provider = config.get("email_provider", "smtp").lower()  # "smtp" or "mailgun"
        self.config = config
        self.sender = config.get('sender_email')
        self.tools = self._define_tools()
        self.agent = self._build_agent()
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email using SMTP. Expects SMTP creds in config:
           smtp_host, smtp_port (int), smtp_username, smtp_password, smtp_use_tls (bool)
        """
        try:
            msg = EmailMessage()
            msg["From"] = self.sender
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)
            msg.add_alternative(body, subtype="html")

            host = self.config.get("smtp_host")
            port = int(self.config.get("smtp_port", 587))
            username = self.config.get("smtp_username")
            password = self.config.get("smtp_password")
            use_tls = self.config.get("smtp_use_tls", "true").lower() in ("1", "true", "yes")

            if use_tls:
                context = ssl.create_default_context()
                with smtplib.SMTP(host, port, timeout=30) as server:
                    server.starttls(context=context)
                    if username and password:
                        server.login(username, password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(host, port, timeout=30) as server:
                    if username and password:
                        server.login(username, password)
                    server.send_message(msg)

            logger.info(f"SMTP: Email sent to {to_email}")
            return {"success": True}
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_via_mailgun(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email using Mailgun HTTP API. Expects mailgun_domain and mailgun_api_key in config."""
        try:
            api_key = self.config.get("mailgun_api_key")
            domain = self.config.get("mailgun_domain")
            if not api_key or not domain:
                raise ValueError("Mailgun config missing (mailgun_api_key/mailgun_domain).")
            resp = requests.post(
                f"https://api.mailgun.net/v3/{domain}/messages",
                auth=("api", api_key),
                data={
                    "from": self.sender,
                    "to": to_email,
                    "subject": subject,
                    "html": body
                },
                timeout=30
            )
            if resp.status_code in (200, 202):
                logger.info(f"Mailgun: Email sent to {to_email}")
                return {"success": True}
            else:
                raise ValueError(f"Mailgun error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Mailgun send failed: {e}")
            return {"success": False, "error": str(e)}

    def _define_tools(self) -> List:
        @tool
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def send_notification(to_email: str, subject: str, body: str) -> Dict[str, Any]:
            """Send email notification (tool wrapper)."""
            if self.provider == "mailgun":
                return self._send_via_mailgun(to_email, subject, body)
            else:
                return self._send_via_smtp(to_email, subject, body)
        
        return [send_notification]
    
    def _build_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an email agent. Use tools to send notifications based on action results."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
    
    def run(self, to_email: str, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run email agent to send confirmation."""
        try:
            subject = "HubSpot Action Confirmation"
            body = f"<pre>Action completed: {action_result}</pre>"
            input_data = f"Send email to {to_email} with subject '{subject}' and body '{body}'"
            result = self.agent.invoke({"input": input_data})
            logger.info(f"Email result: {result}")
            return result.get('output', {})
        except Exception as e:
            logger.error(f"Email run failed: {str(e)}")
            raise