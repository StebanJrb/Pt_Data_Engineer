from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Registration, Event
from .serializers import RegistrationCreateSerializer, RegistrationCreateSerializer, RegistrationSerializer, EventDateSerializer
from . import procedures
class RegistrationCreateView(APIView):
    """POST /api/registrations/create/

    Args:
        APIView (_type_): _description_
    """
    def post(self, request):
        serializer = RegistrationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(
            {'id': registration.id, 'message': 'Registration successful.'},
            status=status.HTTP_201_CREATED,
        )

class RegistrationListView(APIView):
    """GET /api/registrations/?employee=&city=&category=&date=

    Args:
        APIView (_type_): _description_
    """

    def get(self, request):
        # select_related trae Employee, City y Category en el mismo query
        # (JOIN), evitando N+1 queries cuando el serializer acceda a
        # registration.employee.name, registration.employee.city.name, etc.
        queryset = Registration.objects.select_related(
            'employee', 'employee__city', 'category'
        ).all()

        employee_id = request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(employee__city__name=city)

        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        date_param = request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(registration_date__date=date_param)

        serializer = RegistrationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryWinnersView(APIView):
    """GET /api/winners/?category=<id> -- delega al SP sp_GetCategoryWinners."""

    def get(self, request):
        category_id = request.query_params.get('category')
        if not category_id or not category_id.isdigit():
            return Response(
                {'error': 'Missing or invalid "category" parameter.'}, status=400
            )
        winners = procedures.get_category_winners(int(category_id))
        return Response(winners, status=status.HTTP_200_OK)


class StatisticsView(APIView):
    """GET /api/statistics/ -- delega al SP sp_GetRegistrationStatistics."""

    def get(self, request):
        return Response(procedures.get_registration_statistics(), status=status.HTTP_200_OK)


class IsDirector(permissions.BasePermission):
    """
    Permiso custom de DRF. Sin un sistema de autenticación completo montado,
    simplificamos leyendo el rol de un header -- la FORMA (una
    permission_class declarada en la vista) es la misma que usarías con
    autenticación real (JWT/sesión + request.user.position).
    """
    def has_permission(self, request, view):
        return request.headers.get('X-Requester-Position') == 'Director'


class EventDateUpdateView(APIView):
    """PATCH /api/event/date/ -- 'extra mile', restringido a Director."""
    permission_classes = [IsDirector]

    def patch(self, request):
        serializer = EventDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = Event.objects.first()
        event.date = serializer.validated_data['date']
        event.save()
        return Response(
            {'message': f'Event date updated to {event.date.isoformat()}.'},
            status=status.HTTP_200_OK,
        )