import pandas as pd
from django.core.management.base import BaseCommand

from route.models.fuel_station import FuelStation


class Command(BaseCommand):
    help = "Create CSV for fuel data"

    def handle(self, *args, **options):
        fuel_prices = pd.read_csv("fuel-prices-for-be-assessment.csv")
        csv_dict = {
            "OPIS Truckstop ID": [],
            "Truckstop Name": [],
            "Address": [],
            "City": [],
            "State": [],
            "Rack ID": [],
            "Retail Price": [],
            "Latitude": [],
            "Longitude": [],
        }
        for idx, row in fuel_prices.iterrows():
            fuel_stations_obj = FuelStation.objects.filter(
                address=row["Address"],
                city=row["City"],
                state=row["State"],
            ).first()
            for csv_header in csv_dict.keys():
                if csv_header not in ["Latitude", "Longitude"]:
                    csv_dict[csv_header].append(row[csv_header])
            csv_dict["Latitude"].append(fuel_stations_obj.latitude)
            csv_dict["Longitude"].append(fuel_stations_obj.longitude)

        pd.DataFrame(csv_dict).to_csv("fuel-prices-for-be-assessment-processed.csv")
