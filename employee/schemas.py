from datetime import date
from ninja import ModelSchema, Schema

from employee.models import Employee


class EmployeeIn(Schema):
    first_name: str
    last_name: str
    department_id: int = None
    birthdate: date = None


class EmployeeOut(Schema):
    id: int
    first_name: str
    last_name: str
    department_id: int = None
    birthdate: date = None


class EmployeeSchema(ModelSchema):
    class Config:
        model = Employee
        model_fields = '__all__'
