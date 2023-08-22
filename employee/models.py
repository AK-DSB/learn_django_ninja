from django.db import models


# Create your models here.

class Department(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'Department', on_delete=models.CASCADE, db_constraint=False, related_name='children', null=True, blank=True)

    class Meta:
        db_table = 'department'


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, db_constraint=False, related_name='employees')
    birthdate = models.DateField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)

    class Meta:
        db_table = 'employee'
