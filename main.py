# webhook_server.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import logger
from graph import build_graph, AgentState
import uvicorn
import os
import hmac
import hashlib
import base64
from typing import Optional

app = FastAPI()

# Configure CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to initialize graph; if failure keep running but mark graph None
try:
    graph = build_graph()
except Exception as e:
    logger.error(f"Graph initialization failed: {e}")
    graph = None

def _get_hubspot_client_secret() -> Optional[str]:
    # Prefer environment variable (Vercel). Fallback to config.json if present.
    return os.getenv("HUBSPOT_CLIENT_SECRET")

async def verify_hubspot_signature(request: Request, secret: str) -> bool:
    """
    Verify HubSpot webhook signature.
    HubSpot sends header 'X-HubSpot-Signature' which is HMAC-SHA256 of the raw body, base64-encoded.
    """
    try:
        body = await request.body()  # bytes
        signature_header = request.headers.get("X-HubSpot-Signature") or request.headers.get("x-hubspot-signature")
        if not signature_header:
            logger.warning("Missing HubSpot signature header")
            return False
        # Compute expected signature: base64(hmac_sha256(secret, body))
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
        expected_sig = base64.b64encode(digest).decode()
        # Use compare_digest to avoid timing attacks
        return hmac.compare_digest(expected_sig, signature_header)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False

@app.get("/")
async def root():
    return {"status": "healthy", "service": "hubspot-automation"}

# Keep existing /hubspot-webhook for backward compatibility
@app.post("/hubspot-webhook")
async def hubspot_webhook(request: Request):
    # Delegates to common handler without signature enforcement (keeps old behavior)
    data = await request.json()
    logger.info(f"/hubspot-webhook received: {data}")
    event_type = data.get('subscriptionType', '')
    if event_type == 'contact.creation':
        object_id = data.get('objectId')
        query = f"Process new contact with ID {object_id}"
        initial_state = {"query": query, "messages": []}
        try:
            if not graph:
                raise RuntimeError("Graph not initialized")
            for event in graph.stream(initial_state, {"configurable": {"thread_id": f"webhook-{object_id}"}}):
                logger.info(f"Graph event: {event}")
            final_state = graph.get_state({"configurable": {"thread_id": f"webhook-{object_id}"}}).values
            logger.info(f"Graph result: {final_state}")
            return {"status": "success", "result": final_state}
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    return {"status": "ignored", "message": f"Event {event_type} not handled"}

# New preferred /webhook route with signature verification
@app.post("/webhook")
async def hubspot_webhook_secure(request: Request):
    secret = _get_hubspot_client_secret()
    if not secret:
        logger.error("HUBSPOT_CLIENT_SECRET not configured in environment")
        raise HTTPException(status_code=500, detail="Webhook verification not configured")
    # Verify signature first
    if not await verify_hubspot_signature(request, secret):
        logger.warning("Invalid HubSpot webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    # Parse JSON after verification
    data = await request.json()
    logger.info(f"Verified webhook received: {data}")
    event_type = data.get('subscriptionType', '')
    if event_type == 'contact.creation':
        object_id = data.get('objectId')
        query = f"Process new contact with ID {object_id}"
        initial_state = {"query": query, "messages": []}
        try:
            if not graph:
                raise RuntimeError("Graph not initialized")
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
        logger.info("Running on Vercel")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
