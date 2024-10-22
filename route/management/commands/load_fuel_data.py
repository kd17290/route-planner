import pandas as pd
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from route.models.fuel_station import FuelStation


class Command(BaseCommand):
    help = "Load fuel station data from CSV"

    def handle(self, *args, **options):
        # Clear existing data
        # FuelStation.objects.all().delete()

        fuel_prices = pd.read_csv("fuel-prices-for-be-assessment.csv")
        total_fuel_stations = FuelStation.objects.count()
        print(total_fuel_stations)
        for idx, row in fuel_prices.iterrows():
            print(idx)
            fuel_stations_count = FuelStation.objects.filter(
                station_id=row["OPIS Truckstop ID"],
                name=row["Truckstop Name"],
                address=row["Address"],
                city=row["City"],
                state=row["State"],
                rack_id=row["Rack ID"],
                retail_price=float(row["Retail Price"]),
            ).count()
            if fuel_stations_count > 0:
                print(fuel_stations_count)
                continue
            fuel_stations_obj = FuelStation.objects.filter(
                address=row["Address"],
                city=row["City"],
                state=row["State"],
            ).first()
            if fuel_stations_obj:
                lat = fuel_stations_obj.latitude
                lng = fuel_stations_obj.longitude
            else:
                # Get coordinates from MapQuest
                address = f"{row['Address']}, {row['City']}, {row['State']}"
                params = {"key": settings.MAPQUEST_API_KEY, "location": address}
                response = requests.get(
                    "http://www.mapquestapi.com/geocoding/v1/address", params=params
                )

                if response.status_code == 200:
                    result = response.json()
                    location = result["results"][0]["locations"][0]["latLng"]
                    lat, lng = location["lat"], location["lng"]
                else:
                    lat, lng = None, None

            # Create station
            fuel_station = FuelStation.objects.create(
                station_id=row["OPIS Truckstop ID"],
                name=row["Truckstop Name"],
                address=row["Address"],
                city=row["City"],
                state=row["State"],
                rack_id=row["Rack ID"],
                retail_price=float(row["Retail Price"]),
                latitude=lat,
                longitude=lng,
            )

            print(fuel_station, fuel_station.latitude, fuel_station.longitude)
