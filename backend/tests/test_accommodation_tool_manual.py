import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

from langgraph_app.tools.accommodation_tool import get_accommodation_options


def main():
    result = get_accommodation_options.invoke(
        {
            "destination": "Goa",
            "check_in_date": "2026-06-03",
            "check_out_date": "2026-06-05",
            "adults": 3,
        }
    )

    print("status:", result.get("status"))
    print("message:", result.get("message"))
    print("destination:", result.get("destination"))
    print("check_in_date:", result.get("check_in_date"))
    print("check_out_date:", result.get("check_out_date"))
    print("adults:", result.get("adults"))

    suggestions = result.get("hotel_suggestions", [])
    print("hotel_count:", len(suggestions))

    for index, hotel in enumerate(suggestions[:5], start=1):
        print(f"\nHotel {index}")
        print("name:", hotel.get("name"))
        print("category:", hotel.get("category"))
        print("address:", hotel.get("address"))
        print("latitude:", hotel.get("latitude"))
        print("longitude:", hotel.get("longitude"))
        print("source:", hotel.get("source"))


if __name__ == "__main__":
    main()
