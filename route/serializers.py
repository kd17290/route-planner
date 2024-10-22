from rest_framework import serializers

from .models.fuel_station import FuelStation


class RouteInputSerializer(serializers.Serializer):
    start = serializers.CharField(max_length=255)
    finish = serializers.CharField(max_length=255)
    current_fuel_level = serializers.FloatField(default=100, min_value=0, max_value=100)

    def validate_current_fuel_level(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError(
                "Current fuel level must be between 0 and 100"
            )
        return value


class FuelStopSerializer(serializers.ModelSerializer):
    gallons_to_fill = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )
    total_cost = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    price_per_gallon = serializers.DecimalField(
        source="retail_price", max_digits=6, decimal_places=3, read_only=True
    )

    class Meta:
        model = FuelStation
        fields = [
            "name",
            "address",
            "city",
            "state",
            "latitude",
            "longitude",
            "price_per_gallon",
            "gallons_to_fill",
            "total_cost",
        ]


class RouteResponseSerializer(serializers.Serializer):
    route_polyline = serializers.ListField(child=serializers.FloatField())
    total_distance = serializers.FloatField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    fuel_stops = FuelStopSerializer(many=True)
    estimated_time = serializers.CharField()
    route_summary = serializers.DictField(read_only=True)
