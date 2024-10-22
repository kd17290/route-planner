import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from map_processor.base import MapProcessor
from map_processor.enum import MapProcessorType
from map_processor.factory import MapProcessorFactory
from services.route_optimizer_service import RouteOptimizerService
from exceptions.no_fuel_stations_found import NoFuelStationsFound
from .serializers import RouteInputSerializer, RouteResponseSerializer

logger = logging.getLogger(__name__)


class OptimizeRouteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RouteInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            map_quest: MapProcessor = MapProcessorFactory.create_processor(
                MapProcessorType.map_quest, logger
            )
            optimizer_service = RouteOptimizerService(logger, map_quest)
            result = optimizer_service.optimize_route(
                serializer.validated_data["start"],
                serializer.validated_data["finish"],
                serializer.validated_data["current_fuel_level"],
            )

            response_serializer = RouteResponseSerializer(result)
            return Response(response_serializer.data)
        except NoFuelStationsFound as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Route optimization error: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
