import argparse
import pprint
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput
from utils import load_config, logger
from agents.email_agent import EmailAgent

def create_contact(client: HubSpot, properties: dict):
    input_obj = SimplePublicObjectInput(properties=properties)
    resp = client.crm.contacts.basic_api.create(input_obj)
    return resp

def update_contact(client: HubSpot, contact_id: str, properties: dict):
    resp = client.crm.contacts.basic_api.update(contact_id, {"properties": properties})
    return resp

def main():
    parser = argparse.ArgumentParser(description="Run real HubSpot workflow test (create -> update -> optional email).")
    parser.add_argument("--email", required=True, help="Email to use for the contact (e.g. metaisolpak@gmail.com)")
    parser.add_argument("--confirm", action="store_true", help="Actually perform API calls (default: dry-run).")
    parser.add_argument("--send-email", action="store_true", help="Send confirmation email after success.")
    args = parser.parse_args()

    config = load_config()  # reads config.json or env
    hubspot_key = config.get("hubspot_api_key")
    if not hubspot_key:
        logger.error("HubSpot API key missing (set HUBSPOT_API_KEY or in config.json).")
        return

    client = HubSpot(api_key=hubspot_key)

    # build properties using real data
    properties = {
        "email": args.email,
        "firstname": "Test",
        "lastname": "User",
        "phone": "000-000-0000"
    }

    logger.info("DRY RUN: Showing what would be sent to HubSpot:")
    pprint.pprint(properties)

    if not args.confirm:
        logger.info("No --confirm flag provided. Exiting (dry-run). To run for real, re-run with --confirm.")
        return

    try:
        logger.info("Creating contact in HubSpot...")
        created = create_contact(client, properties)
        contact_id = getattr(created, "id", None)
        logger.info(f"Created contact id={contact_id}")
        logger.info("Created contact details:")
        pprint.pprint(getattr(created, "properties", {}))

        # Update contact: change phone and add a test tag/custom property
        update_props = {"phone": "111-222-3333", "jobtitle": "Workflow Test"}
        logger.info(f"Updating contact {contact_id} with: {update_props}")
        updated = update_contact(client, contact_id, update_props)
        logger.info("Updated contact details:")
        pprint.pprint(getattr(updated, "properties", {}))

        # Optionally send email using EmailAgent
        if args.send_email:
            email_agent = EmailAgent(config)
            subject = "Test: HubSpot contact created/updated"
            body = f"Contact {args.email} created (id={contact_id}) and updated with {update_props}."
            logger.info("Sending confirmation email...")
            email_result = email_agent.run(args.email, {"success": True, "id": contact_id})
            logger.info(f"Email result: {email_result}")

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise

if __name__ == "__main__":
    main()