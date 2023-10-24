import requests
from dotenv import load_dotenv
import os
import sys
import argparse
from database import Venue, Session, engine, create_db_and_tables


def get_foursquare_data(address, lat_long, limit, radius, api_key):
    url = "https://api.foursquare.com/v3/places/search"

    if address:
        params = {"near": address, "limit": limit}
    else:
        params = {"ll": lat_long, "radius": radius, "limit": limit}

    headers = {"accept": "application/json", "Authorization": api_key}

    response = requests.get(url, params=params, headers=headers)
    resp = response.json()

    return resp.get("results", [])


def extract_venue_info(results):
    venues_data = []

    for item in results:
        venue_dict = {
            "name": item["name"],
            "category": item["categories"][0]["name"],
            "address": item["location"]["formatted_address"],
            "region": item["location"].get("region", None),
            "country": item["location"]["country"],
            "latitude": item["geocodes"]["main"]["latitude"],
            "longitude": item["geocodes"]["main"]["longitude"],
            "distance": item["distance"],
        }
        venues_data.append(venue_dict)

    return venues_data


def main():
    parser = argparse.ArgumentParser(description="Foursquare data extraction")
    # either address or geolocation coodinates has to be set not both
    address = parser.add_mutually_exclusive_group(required=True)
    address.add_argument("-a", "--address", help="Address around which to retrieve place information")
    address.add_argument("-ll", "--lat_long", help="The latitude/longitude around which to retrieve place information. e.g. 36.808,10.184")
    parser.add_argument("-l", "--limit", help="Number of venues to be returned", required=True)
    parser.add_argument("-r", "--radius", help="radius distance (in meters) ", required=False)

    args = parser.parse_args()
    load_dotenv()
    # get Foursquare API KEY
    API_KEY = os.getenv("API_KEY")

    results = get_foursquare_data(args.address, args.lat_long, args.limit, args.radius, API_KEY)
    if not results:
        print("No results have been found according to the provided params!")
        sys.exit(1)
      
    # get Venues data from Foursquare API result
    venues_data = extract_venue_info(results)
    print(venues_data)

    # create database
    # create_db_and_tables()

    # insert data into database
    new_items = [Venue(**data) for data in venues_data]

    session = Session(engine)
    session.add_all(new_items)
    session.commit()


if __name__ == "__main__":
    main()
