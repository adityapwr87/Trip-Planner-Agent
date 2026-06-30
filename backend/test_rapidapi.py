import http.client
import json

conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "8d5cf707d0msh48027e394792531p1ffcb5jsn9054aa67d491",
    'x-rapidapi-host': "booking-com15.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("GET", "/api/v1/flights/searchFlights?fromId=BOM.AIRPORT&toId=DEL.AIRPORT&departDate=2026-10-10&stops=none&pageNo=1&adults=1&sort=BEST&cabinClass=ECONOMY&currency_code=INR", headers=headers)

res = conn.getresponse()
data = res.read()
json_data = json.loads(data.decode("utf-8"))

flight_offers = json_data.get("data", {}).get("flightOffers", [])
if flight_offers:
    f = flight_offers[0]
    segments = f.get("segments", [])
    print("Price breakdown:")
    print(json.dumps(f.get("priceBreakdown", {}).get("total", {}), indent=2))
    print("Segments count:", len(segments))
    if segments:
        print(json.dumps(segments[0], indent=2))
else:
    print("No flight offers found.")
