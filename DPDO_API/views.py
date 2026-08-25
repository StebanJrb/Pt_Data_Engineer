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
    
    - select_related brings Employee, City and Category in a same query, 
    avoiding N+1 queris when serializer try to serch them

    Args:
        APIView (_type_): _description_
    """

    def get(self, request):
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
    """GET /api/statistics/ 
    - Call SP sp_GetRegistrationStatistics.

    Args:
        APIView (_type_): _description_
    """

    def get(self, request):
        return Response(procedures.get_registration_statistics(), status=status.HTTP_200_OK)


class IsDirector(permissions.BasePermission):
    """Custom DRF permission. Without a full authentication system set up,
    we simplify by reading the role from a header -- the FORM (apermission_class declared in the view) 
    is the same as you would use with real authentication (JWT/session + request.user.position).

    Args:
        permissions (_type_): _description_
    """
    def has_permission(self, request, view):
        return request.headers.get('X-Requester-Position') == 'Director'


class EventDateUpdateView(APIView):
    """PATCH /api/event/date/ 
    'extra mile', Director restringed.
    
    Args:
        APIView (_type_): _description_

    Returns:
        _type_: _description_
    """
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