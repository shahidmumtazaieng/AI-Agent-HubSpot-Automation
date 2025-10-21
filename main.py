# main.py
from graph import build_graph
from utils import logger

def main():
    graph = build_graph()  # <--- Uses build_graph() from graph.py
    initial_state = {"query": "Create a new contact for John Doe with email john@example.com", "messages": []}
    try:
        for event in graph.stream(initial_state, {"configurable": {"thread_id": "1"}}):
            logger.info(f"Event: {event}")
        final_state = graph.get_state({"configurable": {"thread_id": "1"}})
        print("Final State:", final_state.values)
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")

if __name__ == "__main__":
    main()