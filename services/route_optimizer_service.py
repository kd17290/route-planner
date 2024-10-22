from decimal import Decimal
from logging import Logger

from geopy.distance import geodesic

from exceptions.no_fuel_stations_found import NoFuelStationsFound
from map_processor.map_quest import MapProcessor
from route.models.fuel_station import FuelStation


class RouteOptimizerService:
    def __init__(self, logger: Logger, map_quest: MapProcessor):
        self.logger = logger
        self.mapquest = map_quest
        self.max_range = 500  # miles
        self.tank_size = 50  # gallons
        self.mpg = 10  # miles per gallon
        self.safety_margin = 100  # miles

    def find_nearest_stations(
        self,
        current_location: tuple[float, float],
        route_points: list[tuple[float, float]],
        max_distance: float = 10,
    ) -> list:
        """Find fuel stations near the route with spatial query"""
        lat, lng = current_location

        # Get stations within bounding box
        stations = FuelStation.objects.filter(
            latitude__range=(lat - 0.5, lat + 0.5),
            longitude__range=(lng - 0.5, lng + 0.5),
        ).order_by("retail_price")

        stations_with_distance: list = []
        for station in stations:
            distance = geodesic(current_location, station.location).miles

            if distance <= max_distance:
                # Check distance to route
                min_route_distance = min(
                    geodesic(station.location, point).miles for point in route_points
                )

                if min_route_distance <= max_distance:
                    stations_with_distance.append(
                        {
                            "station": station,
                            "distance": distance,
                            "detour_distance": min_route_distance,
                        }
                    )

        return sorted(
            stations_with_distance,
            key=lambda x: (x["station"].retail_price, x["detour_distance"]),
        )

    def optimize_route(
        self, start: str, finish: str, current_fuel_level: float
    ) -> dict:
        """Optimize route with fuel stops"""
        route_data = self.mapquest.get_route(start, finish)
        shape_points = route_data["route"]["shape"]["shapePoints"]
        route_points = [
            (shape_points[i], shape_points[i + 1])
            for i in range(0, len(shape_points), 2)
        ]

        total_distance = route_data["route"]["distance"]
        current_fuel = current_fuel_level / 100 * self.tank_size

        fuel_stops = []
        distance_covered = 0
        remaining_range = current_fuel * self.mpg

        while distance_covered < total_distance:
            if remaining_range < self.safety_margin:
                current_point_index = int(
                    distance_covered / total_distance * len(route_points)
                )
                current_location = route_points[current_point_index]

                nearest_stations = self.find_nearest_stations(
                    current_location, route_points[current_point_index:]
                )

                if not nearest_stations:
                    raise NoFuelStationsFound(
                        f"No fuel stations found near location {current_location}"
                    )

                best_station_data = nearest_stations[0]
                best_station = best_station_data["station"]

                gallons_to_fill = self.tank_size - remaining_range / self.mpg
                total_cost = Decimal(gallons_to_fill) * best_station.retail_price

                # Add computed fields to a station object
                best_station.gallons_to_fill = Decimal(format(gallons_to_fill, ".2f"))
                best_station.total_cost = Decimal(format(total_cost, ".2f"))
                fuel_stops.append(best_station)

                # Add detour distance to total
                distance_covered += best_station_data["detour_distance"] * 2
                remaining_range = self.max_range

            next_segment = min(remaining_range, 50)
            distance_covered += next_segment
            remaining_range -= next_segment

        # Create route summary
        route_summary = {
            "total_stops": len(fuel_stops),
            "average_price": sum(stop.retail_price for stop in fuel_stops)
            / len(fuel_stops)
            if fuel_stops
            else 0,
            "states_crossed": set(stop.state for stop in fuel_stops),
        }

        return {
            "route_polyline": shape_points,
            "total_distance": total_distance,
            "total_cost": sum(stop.total_cost for stop in fuel_stops),
            "fuel_stops": fuel_stops,
            "estimated_time": route_data["route"]["formattedTime"],
            "route_summary": route_summary,
        }
