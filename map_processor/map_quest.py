from logging import Logger

import requests
from django.conf import settings
from django.core.cache import cache

from map_processor.base import MapProcessor


class MapQuestClient(MapProcessor):
    def __init__(self, logger: Logger):
        super().__init__(logger)
        self.api_key = settings.MAPQUEST_API_KEY
        self.geocode_url = "http://www.mapquestapi.com/geocoding/v1/address"
        self.directions_url = "http://www.mapquestapi.com/directions/v2/route"

    def get_coordinates(self, location: str) -> tuple[float, float]:
        """Get coordinates for a location with caching"""
        cache_key = f"coordinates_{location}"
        coords = cache.get(cache_key)

        if coords is None:
            params = {"key": self.api_key, "location": location}
            try:
                response = requests.get(self.geocode_url, params=params)
                response.raise_for_status()
                result = response.json()
                coords = (
                    result["results"][0]["locations"][0]["latLng"]["lat"],
                    result["results"][0]["locations"][0]["latLng"]["lng"],
                )
                cache.set(cache_key, coords, 86400)  # Cache for 24 hours
            except Exception as e:
                self.logger.error(f"Geocoding error for {location}: {str(e)}")
                raise

        return coords

    def get_route(self, start: str, finish: str) -> dict:
        """Get route information with caching"""
        cache_key = f"route_{start}_{finish}"
        route_data = cache.get(cache_key)

        if route_data is None:
            params = {
                "key": self.api_key,
                "from": start,
                "to": finish,
                "fullShape": True,
            }
            try:
                response = requests.get(self.directions_url, params=params)
                response.raise_for_status()
                route_data = response.json()
                cache.set(cache_key, route_data, 3600)  # Cache for 1 hour
            except Exception as e:
                self.logger.error(f"Routing error for {start} to {finish}: {str(e)}")
                raise

        return route_data
