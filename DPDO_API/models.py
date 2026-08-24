from django.db import models
# Create your models here.
class Position(models.Model):
    id = models.AutoField(primary_key= True, db_column= 'Id')
    name = models.CharField(max_length=50, unique=True, db_column='Name')

    class Meta:
        db_table = 'Position'
        managed = False

    def __str__(self):
        return self.name

class City(models.Model):
    id = models.AutoField(primary_key= True, db_column= 'Id')
    name = models.CharField(max_length=100, unique=True , db_column= 'Name')
    is_contest_enabled = models.BooleanField(db_column= 'IsContestenabled')

    class Meta:
        db_table = 'City'
        managed = False

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.AutoField(primary_key= True, db_column= 'Id')
    name = models.CharField(max_length=100 , unique=True, db_column= 'Name')
    max_capacity = models.IntegerField(db_column='MaxCapacity')

    class Meta:
        db_table = 'Category'
        managed = False

    def __str__(self):
        return self.name

class Event(models.Model):
    id = models.AutoField(primary_key= True, db_column= 'Id')
    name = models.CharField(max_length=150 , unique=True, db_column= 'Name')
    date = models.DateField(db_column='Date')

    class Meta:
        db_table = 'Event'
        managed = False

    def __str__(self):
        return self.name

class Employee(models.Model):
    id = models.AutoField(primary_key= True, db_column= 'Id')
    name = models.CharField(max_length= 150, db_column= 'Name')
    position = models.ForeignKey(Position, on_delete= models.DO_NOTHING, db_column='PositionId')
    city = models.ForeignKey(City, on_delete= models.DO_NOTHING, db_column= 'CityId')

    class Meta:
        db_table = 'Employee'
        managed = False

    def __str__(self):
        return self.name

class Registration(models.Model):
    id = models.AutoField(primary_key= True, db_column= 'Id')
    employee = models.ForeignKey(Employee, on_delete= models.DO_NOTHING, db_column= 'EmployeeId')
    category = models.ForeignKey(Category, on_delete= models.DO_NOTHING, db_column= 'CategotyId')
    registration_date = models.DateTimeField(db_column='RegistrationDate', auto_now_add=True)

    class Meta:
        db_table = 'Registration'
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'category'], name='uq_employee_category_orm'
            )
        ]


class Result(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    registration = models.OneToOneField(Registration, on_delete=models.DO_NOTHING, db_column='RegistrationId')
    score = models.DecimalField(max_digits=5, decimal_places=2, db_column='Score')

    class Meta:
        db_table = 'Result'
        managed = False


class RegistrationAttempt(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    attempted_employee_id = models.IntegerField(null=True, db_column='AttemptedEmployeeId')
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, db_column='CategoryId', null=True)
    rejection_reason = models.CharField(max_length=50, db_column='RejectionReason')
    attempt_date = models.DateTimeField(db_column='AttemptDate', auto_now_add=True)

    class Meta:
        db_table = 'RegistrationAttempt'
        managed = False
