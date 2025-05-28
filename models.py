from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
class Personnel(models.Model):
    name = models.CharField(max_length=255)
    birthdate = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=255, null=True, blank=True)
    present_address = models.TextField(null=True, blank=True)
    provincial_address = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=7, choices=[('Single', 'Single'), ('Married', 'Married')])
    spouse_name = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

class Position(models.Model):
    position_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.position_name

class EmploymentDetails(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=11, choices=[('Contractual', 'Contractual'), ('Regular', 'Regular')])
    date_hired = models.DateField(null=True, blank=True)
    latest_evaluation = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)

class Dependent(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    age = models.IntegerField()

class Parent(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    parent_type = models.CharField(max_length=6, choices=[('Mother', 'Mother'), ('Father', 'Father')])
    name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)

class Education(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    level = models.CharField(max_length=11, choices=[('Elementary', 'Elementary'), ('High School', 'High School'), ('College', 'College'), ('Other', 'Other')])
    school_name = models.CharField(max_length=255)
    other_skills = models.TextField(blank=True, null=True)

class EmploymentHistory(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)

class Identification(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    sss = models.CharField(max_length=20, null=True, blank=True)
    philhealth = models.CharField(max_length=20, null=True, blank=True)
    pag_ibig = models.CharField(max_length=20, null=True, blank=True)
    tin = models.CharField(max_length=20, null=True, blank=True)
    
class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=128)  # Password should be hashed
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'accounts'

class Attendance(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20)  # Example: "Present", "Absent", etc.

    def __str__(self):
        return f"{self.personnel} - {self.date} - {self.status}"
