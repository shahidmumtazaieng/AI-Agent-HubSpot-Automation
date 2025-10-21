from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from utils import logger
from graph import build_graph, AgentState
import uvicorn
import os

app = FastAPI()

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph
try:
    graph = build_graph()
except Exception as e:
    logger.error(f"Graph initialization failed: {e}")
    graph = None

@app.get("/")
async def root():
    return {"status": "healthy", "service": "hubspot-automation"}

@app.post("/hubspot-webhook")
async def hubspot_webhook(request: Request):
    if not graph:
        return {"status": "error", "message": "Graph not initialized"}
    
    data = await request.json()
    logger.info(f"Webhook received: {data}")
    
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

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    if os.getenv('VERCEL_ENV'):
        # Running on Vercel
        logger.info("Running on Vercel")
    else:
        # Local development
        uvicorn.run(app, host="0.0.0.0", port=8000)
