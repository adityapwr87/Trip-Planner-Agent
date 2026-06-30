import os
import sys
import json

# Ensure python can find the 'core' module and others
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_app.agents.accommodation_agent import accommodation_node

def main():
    print("Testing MCP Accommodation Agent...")
    
    # Create a dummy trip state
    mock_state = {
        "destination": "Paris",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
        "travelers": 2
    }
    
    print(f"Destination: {mock_state['destination']}")
    print(f"Dates: {mock_state['start_date']} to {mock_state['end_date']}")
    print(f"Travelers: {mock_state['travelers']}")
    print("-" * 40)
    print("Calling MCP Server (This may take 10-30 seconds)...\n")
    
    try:
        # Call the node function synchronously
        result = accommodation_node(mock_state)
        
        print("--- RESULTS ---")
        print("\n[Accommodation Message]")
        print(result.get("accommodation_message", "No message returned"))
        
        print("\n[Hotel Suggestions]")
        print(json.dumps(result.get("hotel_suggestions", []), indent=2))
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    main()
