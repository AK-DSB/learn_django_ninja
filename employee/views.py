from employee.models import Employee, Department
from employee.schemas import EmployeeIn, EmployeeSchema
from learn_django_ninja.api import api


@api.post('/employees')
def create_employee(request, payload: EmployeeIn):
    employee = Employee.objects.create(**payload.dict())
    return EmployeeSchema(**payload.dict(), id=employee.id)
