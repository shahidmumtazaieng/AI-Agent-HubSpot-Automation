# agents/orchestrator.py
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI  # New import
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor  # Works with Gemini too
from utils import logger, load_config

class OrchestratorAgent:
    """Global Orchestrator: Parses queries and delegates tasks."""
    
    def __init__(self, config: Dict[str, str]):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Or "gemini-1.5-pro" for better reasoning
            google_api_key=config['gemini_api_key'],
            temperature=0.2
        )
        self.tools = self._define_tools()
        self.agent = self._build_agent()
    
    def _define_tools(self) -> List:
        @tool
        def parse_query(query: str) -> Dict[str, Any]:
            """Parse user query to extract intent and payload."""
            # This is a placeholder; in reality, LLM calls this to generate structured output
            # For industry: Use structured output mode for reliability
            try:
                # Simulate parsing (expand with actual logic or sub-LLM call)
                if "create contact" in query.lower():
                    intent = "create_contact"
                    payload = {"properties": {"firstname": "John", "lastname": "Doe", "email": "john@example.com"}}  # Extract dynamically
                elif "update contact" in query.lower():
                    intent = "update_contact"
                    payload = {"id": "123", "properties": {"phone": "123-456-7890"}}
                elif "create deal" in query.lower():
                    intent = "create_deal"
                    payload = {"properties": {"dealname": "New Deal", "amount": "1000"}}  # Extract dynamically
                elif "update deal" in query.lower():
                    intent = "update_deal"
                    payload = {"id": "456", "properties": {"dealstage": "appointmentscheduled"}}
                elif "create company" in query.lower():
                    intent = "create_company"
                    payload = {"properties": {"name": "New Company", "domain": "metaisol.com"}}
                else:
                    raise ValueError("Unknown intent")
                return {"intent": intent, "payload": payload}
            except Exception as e:
                logger.error(f"Query parse error: {str(e)}")
                raise
        
        return [parse_query]
    
    def _build_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an orchestrator. Parse the query and use tools to prepare payload. Delegate to HubSpot for CRM, then Email for notification."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run orchestrator on query."""
        try:
            result = self.agent.invoke({"input": query})
            logger.info(f"Orchestrator result: {result}")
            return result['output']  # Returns {'intent': ..., 'payload': ...}
        except Exception as e:
            logger.error(f"Orchestrator run failed: {str(e)}")
            raise