# agents/hubspot_agent.py
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.companies import SimplePublicObjectInputForCreate as CompanyInputForCreate
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInputForCreate
from utils import logger, load_config
from tenacity import retry, stop_after_attempt, wait_exponential

class HubSpotAgent:
    """HubSpot Agent: Performs CRM operations via tools."""
    
    def __init__(self, config: Dict[str, str]):
        # Use Gemini for HubSpot agent as well
        self.llm = ChatGoogleGenerativeAI(
            model=config.get("gemini_model", "gemini-2.5-flash"),
            google_api_key=config['gemini_api_key'],
            temperature=float(config.get("gemini_temperature", 0.0))
        )
        self.client = HubSpot(api_key=config['hubspot_api_key'])
        self.tools = self._define_tools()
        self.agent = self._build_agent()
    
    def _define_tools(self) -> List:
        @tool
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def create_contact(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new contact in HubSpot."""
            try:
                properties = payload.get('properties', {})
                contact_input = SimplePublicObjectInputForCreate(properties=properties)
                response = self.client.crm.contacts.basic_api.create(contact_input)
                logger.info(f"Contact created: {response.id}")
                return {"success": True, "id": response.id, "details": response.properties}
            except Exception as e:
                logger.error(f"Create contact failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        @tool
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def update_contact(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Update an existing contact."""
            try:
                contact_id = payload.get('id')
                properties = payload.get('properties', {})
                response = self.client.crm.contacts.basic_api.update(contact_id, {"properties": properties})
                logger.info(f"Contact updated: {contact_id}")
                return {"success": True, "id": contact_id, "details": response.properties}
            except Exception as e:
                logger.error(f"Update contact failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        @tool
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def create_deal(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new deal."""
            try:
                properties = payload.get('properties', {})
                deal_input = DealInputForCreate(properties=properties)
                response = self.client.crm.deals.basic_api.create(deal_input)
                logger.info(f"Deal created: {response.id}")
                return {"success": True, "id": response.id, "details": response.properties}
            except Exception as e:
                logger.error(f"Create deal failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        @tool
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def update_deal(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Update an existing deal."""
            try:
                deal_id = payload.get('id')
                properties = payload.get('properties', {})
                response = self.client.crm.deals.basic_api.update(deal_id, {"properties": properties})
                logger.info(f"Deal updated: {deal_id}")
                return {"success": True, "id": deal_id, "details": response.properties}
            except Exception as e:
                logger.error(f"Update deal failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        @tool
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def create_company(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new company."""
            try:
                properties = payload.get('properties', {})
                company_input = CompanyInputForCreate(properties=properties)
                response = self.client.crm.companies.basic_api.create(company_input)
                logger.info(f"Company created: {response.id}")
                return {"success": True, "id": response.id, "details": response.properties}
            except Exception as e:
                logger.error(f"Create company failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        # Add more tools for edit_deal, etc., similarly
        
        return [create_contact, update_contact, create_deal, update_deal, create_company]
    
    def _build_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a HubSpot CRM agent. Use tools to perform operations based on intent and payload."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
    
    def run(self, intent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run HubSpot agent with intent and payload."""
        try:
            input_data = f"Perform {intent} with payload: {payload}"
            result = self.agent.invoke({"input": input_data})
            logger.info(f"HubSpot result: {result}")
            return result['output']
        except Exception as e:
            logger.error(f"HubSpot run failed: {str(e)}")
            raise