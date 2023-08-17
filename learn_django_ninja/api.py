import datetime
from typing import List

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema, UploadedFile, File, Path, Query
from pydantic import Field

from employee.models import Employee
from employee.schemas import EmployeeSchema, EmployeeIn, EmployeeOut

api = NinjaAPI()
__all__ = ['api']


class HelloSchema(Schema):
    name: str = 'world'


class UserSchema(Schema):
    username: str
    is_authenticated: bool
    # Unauthenticated users don't have the following fields, so provide defaults.
    email: str = None
    first_name: str = None
    last_name: str = None


class Error(Schema):
    message: str


@api.post('/hello')
def hello(request, data: HelloSchema):
    return f'Helo {data.name}'


@api.get('/math')
def math(request, a: int, b: int):
    return {'add': a + b, 'multiply': a * b}


@api.get('/math/{a}and{b}')
def math(request, a: int, b: int):
    return {'add': a + b, 'multiply': a * b}


@api.get('/me', response={200: UserSchema, 403: Error})
def me(request):
    if not request.user.is_authenticated:
        return 403, {'message': 'Please sign in first'}
    return request.user


@api.post('/employees', response=EmployeeSchema)
def create_employee(request, payload: EmployeeIn, cv: UploadedFile = File(...)):
    print(cv.file)
    employee = Employee(**payload.dict())
    employee.cv.save(cv.name, cv)
    return employee


@api.get('/employees/{employee_id}', response=EmployeeOut)
def get_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    return employee


@api.get('/employees', response=List[EmployeeOut])
def list_employees(request):
    return Employee.objects.all()


@api.put('/employees/{employee_id}')
def update_employee(request, employee_id: int, payload: EmployeeIn):
    employee = get_object_or_404(Employee, id=employee_id)
    for attr, value in payload.dict().items():
        setattr(employee, attr, value)
    employee.save()
    return {'success': True}


@api.delete("/employees/{employee_id}")
def delete_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return {"success": True}


@api.get("/items/{int:item_id}")
def read_item(request, item_id):
    # item_id 仍是 '3' 不是 int类型
    return {"item_id": item_id}


@api.get('/dir/{path:value}')
def someview(request, value: str):
    return value


@api.get("/events/{year}/{month}/{day}")
def events(request, year: int, month: int, day: int):
    return {"date": [year, month, day]}


class PathDate(Schema):
    year: int
    month: int
    day: int

    def value(self):
        return datetime.date(self.year, self.month, self.day)


@api.get('/event/{year}/{month}/{day}')
def event(request, date: PathDate = Path(...)):
    return {'date': date.value()}


@api.get('/even')
def even(request, date: PathDate = Query(...)):
    return {'date': date.value()}


weapons = ["Ninjato", "Shuriken", "Katana", "Kama", "Kunai", "Naginata", "Yari"]


@api.get('/weapons')
def list_weapons(request, q: str, limit: int = 10, offset: int = 0):
    results = [w for w in weapons if q in w.lower()]
    print(q, results)
    return results[offset: offset + limit]


@api.get("/example")
def example(request, s: str = None, b: bool = None, d: datetime.date = None, i: int = None):
    return [s, b, d, i]


class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(None, alias='categories')


@api.get('/filter')
def filter_events(request, filters: Filters = Query(...)):
    return {'filters': filters.dict()}
