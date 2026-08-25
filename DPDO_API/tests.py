import os
from datetime import date, timedelta

from django.db.utils import ConnectionHandler
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, City, Employee, Event, Position, Registration, RegistrationAttempt, Result


class RegistrationCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse('registrations-create')
        self.position_asesor = Position.objects.create(name='Asesor')
        self.position_coordinador = Position.objects.create(name='Coordinador')
        self.city_enabled = City.objects.create(name='Medellin', is_contest_enabled=True)
        self.city_disabled = City.objects.create(name='Cali', is_contest_enabled=False)
        self.category = Category.objects.create(name='Canto', max_capacity=2)
        self.event = Event.objects.create(name='Concurso DPDO', date=date.today() + timedelta(days=10))
        self.employee = Employee.objects.create(
            name='Ana Torres', position=self.position_asesor, city=self.city_enabled
        )

    def test_successful_registration_returns_201(self):
        response = self.client.post(
            self.url, {'employee_id': self.employee.id, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Registration.objects.filter(employee=self.employee, category=self.category).exists()
        )

    def test_employee_not_found_returns_404(self):
        response = self.client.post(
            self.url, {'employee_id': 9999, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_position_not_allowed_returns_403(self):
        employee = Employee.objects.create(
            name='Sofia Rojas', position=self.position_coordinador, city=self.city_enabled
        )
        response = self.client.post(
            self.url, {'employee_id': employee.id, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_city_not_allowed_returns_400(self):
        employee = Employee.objects.create(
            name='Laura Mendez', position=self.position_asesor, city=self.city_disabled
        )
        response = self.client.post(
            self.url, {'employee_id': employee.id, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_category_not_found_returns_404(self):
        response = self.client.post(
            self.url, {'employee_id': self.employee.id, 'category_id': 9999}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_registration_returns_409(self):
        Registration.objects.create(employee=self.employee, category=self.category)
        response = self.client.post(
            self.url, {'employee_id': self.employee.id, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_capacity_exceeded_returns_409(self):
        first = Employee.objects.create(
            name='Luis Gomez', position=self.position_asesor, city=self.city_enabled
        )
        second = Employee.objects.create(
            name='Marta Ruiz', position=self.position_asesor, city=self.city_enabled
        )
        Registration.objects.create(employee=first, category=self.category)
        Registration.objects.create(employee=second, category=self.category)  # max_capacity=2 reached

        response = self.client.post(
            self.url, {'employee_id': self.employee.id, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_registrations_closed_returns_409(self):
        self.event.date = date.today() + timedelta(days=1)  # closes 3 days before -> already closed
        self.event.save()
        response = self.client.post(
            self.url, {'employee_id': self.employee.id, 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_employee_id_returns_400(self):
        response = self.client.post(
            self.url, {'employee_id': 'abc', 'category_id': self.category.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegistrationListTests(APITestCase):
    def setUp(self):
        self.url = reverse('registrations-list')
        position = Position.objects.create(name='Asesor')
        city_a = City.objects.create(name='Medellin', is_contest_enabled=True)
        city_b = City.objects.create(name='Bogota', is_contest_enabled=True)
        self.category_a = Category.objects.create(name='Canto', max_capacity=10)
        self.category_b = Category.objects.create(name='Baile', max_capacity=10)
        self.employee_a = Employee.objects.create(name='Ana Torres', position=position, city=city_a)
        self.employee_b = Employee.objects.create(name='Diana Rios', position=position, city=city_b)
        self.city_b = city_b
        self.registration_a = Registration.objects.create(
            employee=self.employee_a, category=self.category_a
        )
        self.registration_b = Registration.objects.create(
            employee=self.employee_b, category=self.category_b
        )

    def test_filter_by_employee(self):
        response = self.client.get(self.url, {'employee': self.employee_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.data], [self.registration_a.id])

    def test_filter_by_city(self):
        response = self.client.get(self.url, {'city': self.city_b.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.data], [self.registration_b.id])

    def test_filter_by_category(self):
        response = self.client.get(self.url, {'category': self.category_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.data], [self.registration_a.id])

    def test_filter_by_date(self):
        response = self.client.get(self.url, {'date': date.today().isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class CategoryWinnersTests(APITestCase):
    """Hits the real sp_GetCategoryWinners stored procedure, created in the
    disposable SQL Server test database by DPDO_API/test_runner.py."""

    def setUp(self):
        self.url = reverse('winners')
        position = Position.objects.create(name='Asesor')
        city = City.objects.create(name='Medellin', is_contest_enabled=True)
        self.category = Category.objects.create(name='Canto', max_capacity=10)

        for index, score in enumerate([88.5, 95.0, 91.2, 93.4]):
            employee = Employee.objects.create(name=f'Employee {index}', position=position, city=city)
            registration = Registration.objects.create(employee=employee, category=self.category)
            Result.objects.create(registration=registration, score=score)

    def test_returns_results_in_descending_score_order(self):
        response = self.client.get(self.url, {'category': self.category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scores = [float(row['Score']) for row in response.data]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(scores[0], 95.0)
        self.assertEqual(response.data[0]['Position'], 1)
        self.assertTrue(response.data[0]['is_podium'])

    def test_missing_category_param_returns_400(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StatisticsTests(APITestCase):
    """Hits the real sp_GetRegistrationStatistics stored procedure, created
    in the disposable SQL Server test database by DPDO_API/test_runner.py."""

    def setUp(self):
        self.url = reverse('statistics')
        position_asesor = Position.objects.create(name='Asesor')
        city = City.objects.create(name='Medellin', is_contest_enabled=True)
        category = Category.objects.create(name='Canto', max_capacity=10)

        self.employee = Employee.objects.create(name='Ana Torres', position=position_asesor, city=city)
        Registration.objects.create(employee=self.employee, category=category)

        RegistrationAttempt.objects.create(
            attempted_employee_id=901, category=category, rejection_reason='POSITION_NOT_ALLOWED'
        )
        RegistrationAttempt.objects.create(
            attempted_employee_id=902, category=category, rejection_reason='POSITION_NOT_ALLOWED'
        )
        RegistrationAttempt.objects.create(
            attempted_employee_id=self.employee.id, category=category, rejection_reason='DUPLICATE'
        )

    def test_returns_three_expected_metrics(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        advisor_row = next(
            row for row in response.data['registrations_by_advisor']
            if row['EmployeeName'] == 'Ana Torres'
        )
        self.assertEqual(advisor_row['TotalRegistrations'], 1)
        self.assertEqual(response.data['unauthorized_attempts'], 2)
        self.assertEqual(response.data['duplicate_attempts'], 1)


class EventDateUpdateTests(APITestCase):
    def setUp(self):
        self.url = reverse('event-date')
        self.event = Event.objects.create(name='Concurso DPDO', date=date.today() + timedelta(days=10))

    def test_patch_without_director_header_returns_403(self):
        new_date = (date.today() + timedelta(days=20)).isoformat()
        response = self.client.patch(self.url, {'date': new_date}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_as_director_returns_200(self):
        new_date = (date.today() + timedelta(days=20)).isoformat()
        response = self.client.patch(
            self.url, {'date': new_date}, format='json', HTTP_X_REQUESTER_POSITION='Director'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.date.isoformat(), new_date)


class DatabaseConnectionTest(SimpleTestCase):
    """Direct sanity check that the app can reach the SQL Server instance
    configured in .env, independent of Django's test database machinery.
    Every other test in this file already runs against a real, disposable
    SQL Server database (test_dpdo, see DPDO_API/test_runner.py); this one
    instead opens its own connection using the exact DB_NAME from .env (the
    real 'dpdo' database), to confirm the driver/host/credentials used by
    'runserver' are reachable."""

    allow_database_queries = True
    databases = {'default'}

    def test_can_connect_to_configured_sql_server(self):
        handler = ConnectionHandler({
            'default': {
                'ENGINE': 'mssql',
                'NAME': os.getenv('DB_NAME'),
                'USER': os.getenv('DB_USER'),
                'PASSWORD': os.getenv('DB_PASSWORD'),
                'HOST': os.getenv('DB_HOST'),
                'PORT': os.getenv('DB_PORT'),
                'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
            }
        })
        try:
            with handler['default'].cursor() as cursor:
                cursor.execute('SELECT 1')
                self.assertEqual(cursor.fetchone()[0], 1)
        finally:
            handler['default'].close()
