import os
import sys
import json

# Ensure python can find the 'core' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_app.tools.accommodation_tool import get_accommodation_options

def main():
    destination = "Goa"
    check_in = "2026-08-15"
    check_out = "2026-08-18"
    adults = 2
    
    print(f"Testing Makcorps API...")
    print(f"Destination: {destination}")
    print(f"Dates: {check_in} to {check_out}")
    print(f"Adults: {adults}")
    print("-" * 40)
    
    # We call .invoke() because get_accommodation_options is a LangChain @tool
    result = get_accommodation_options.invoke({
        "destination": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": adults
    })
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
