# webhook_server.py
from fastapi import FastAPI, Request
from utils import logger
from graph import build_graph, AgentState
import uvicorn

app = FastAPI()
graph = build_graph()  # Initialize LangGraph

@app.post("/hubspot-webhook")
async def hubspot_webhook(request: Request):
    data = await request.json()
    logger.info(f"Webhook received: {data}")
    # Example: Trigger graph if contact created
    event_type = data.get('subscriptionType', '')
    if event_type == 'contact.creation':
        object_id = data.get('objectId')
        query = f"Process new contact with ID {object_id}"
        initial_state = {"query": query, "messages": []}
        try:
            for event in graph.stream(initial_state, {"configurable": {"thread_id": f"webhook-{object_id}"}}):
                logger.info(f"Graph event: {event}")
            final_state = graph.get_state({"configurable": {"thread_id": f"webhook-{object_id}"}}).values
            logger.info(f"Graph result: {final_state}")
            return {"status": "success", "result": final_state}
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    return {"status": "ignored", "message": f"Event {event_type} not handled"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)