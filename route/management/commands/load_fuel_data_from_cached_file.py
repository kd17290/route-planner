import pandas as pd
from django.core.management.base import BaseCommand

from route.models.fuel_station import FuelStation


class Command(BaseCommand):
    help = "Load fuel station data from CSV"

    def handle(self, *args, **options):
        # Clear existing data
        FuelStation.objects.all().delete()

        fuel_prices = pd.read_csv("fuel-prices-for-be-assessment-processed.csv")
        for idx, row in fuel_prices.iterrows():
            fuel_station = FuelStation.objects.create(
                station_id=row["OPIS Truckstop ID"],
                name=row["Truckstop Name"].strip(),
                address=row["Address"].strip(),
                city=row["City"].strip(),
                state=row["State"].strip(),
                rack_id=row["Rack ID"],
                retail_price=float(row["Retail Price"]),
                latitude=row["Latitude"],
                longitude=row["Longitude"],
            )
            print(fuel_station)
