from rest_framework import serializers
from .models import Position, City, Category, Event, Employee, Registration, Result, RegistrationAttempt
from datetime import timedelta, date
from .exceptions import (
    EmployeeNotFoundError, PositionNotAllowedError, CityNotAllowedError,
    CategoryNotFoundError, RegistrationsClosedError,
    DuplicateRegistrationError, CapacityExceededError,
)
class RegistrationCreateSerializer(serializers.Serializer):
    """POST /api/registrations/create/

    Args:
        serializers (_type_): _description_

    Raises:
        EmployeeNotFoundError: _description_
        CategoryNotFoundError: _description_
        PositionNotAllowedError: _description_
        CityNotAllowedError: _description_
        RegistrationsClosedError: _description_
        DuplicateRegistrationError: _description_
        CapacityExceededError: _description_

    Returns:
        _type_: _description_
    """
    employee_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    def validate_employee_id(self, value):
        if not Employee.objects.filter(id=value).exists():
            raise EmployeeNotFoundError()
        return value

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value).exists():
            raise CategoryNotFoundError()
        return value

    def validate(self, data):
        employee = Employee.objects.select_related('position', 'city').get(
            id=data['employee_id']
        )

        if employee.position.name != 'Asesor':
            raise PositionNotAllowedError()

        if not employee.city.is_contest_enabled:
            raise CityNotAllowedError()

        event = Event.objects.first()
        closing_date = event.date - timedelta(days=3)
        if date.today() > closing_date:
            raise RegistrationsClosedError(
                f'Registrations closed on {closing_date.isoformat()} '
                f'(3 days before the event).'
            )

        if Registration.objects.filter(
            employee_id=data['employee_id'], category_id=data['category_id']
        ).exists():
            raise DuplicateRegistrationError()

        category = Category.objects.get(id=data['category_id'])
        current_registrations = Registration.objects.filter(
            category_id=data['category_id']
        ).count()
        if current_registrations >= category.max_capacity:
            raise CapacityExceededError()

        return data

    def create(self, validated_data):
        return Registration.objects.create(
            employee_id=validated_data['employee_id'],
            category_id=validated_data['category_id'],
        )
class RegistrationSerializer(serializers.ModelSerializer):
    """GET /api/registrations/ with filters

    Args:
        serializers (_type_): _description_
    """
    employee = serializers.CharField(source='employee.name', read_only=True)
    city = serializers.CharField(source='employee.city.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'employee', 'city', 'category', 'registration_date']
class EventDateSerializer(serializers.Serializer):
    """ 'Extra mile': modify date.

    Args:
        serializers (_type_): _description_
    """
    date = serializers.DateField()
