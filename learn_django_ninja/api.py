import datetime
from typing import Any, List, Generic, TypeVar, Optional
from django.http import HttpRequest

from django.shortcuts import get_object_or_404
from ninja import ModelSchema, NinjaAPI, Schema, UploadedFile, File, Path, Query, Form, FilterSchema, pagination
from ninja.security import HttpBearer, APIKeyQuery, HttpBasicAuth
from pydantic import Field
from pydantic.fields import ModelField
from django.db.models import Q, Case, When

from employee.models import Department, Employee
from employee.schemas import EmployeeSchema, EmployeeIn, EmployeeOut

api = NinjaAPI()
__all__ = ['api']


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Any | None:
        if token == 'supersecret':
            return token


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


weapons = ["Ninjato", "Shuriken", "Katana",
           "Kama", "Kunai", "Naginata", "Yari"]


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


class Item(Schema):
    name: str
    description: str = None
    price: float
    quantity: int


@api.post("/items")
def create(request, item: Item):
    return item


@api.post("/items/{item_id}")
def update(request, item_id: int, item: Item, q: str):
    return {"item_id": item_id, "item": item.dict(), "q": q}


@api.post('/login')
def login(request, username: str = Form(...), password: str = Form(...)):
    return {'username': username, 'password': f'{password}****'}


@api.post('/form_items')
def create_items_with_form(request, item: Item = Form(...)):
    return item


@api.put("/form_items/{item_id}")
def update_item_with_form(request, item_id: int, q: str, item: Item = Form(...)):
    return {"item_id": item_id, "item": item.dict(), "q": q}


PydanticField = TypeVar('PydanticField')


class EmptyStrToDefault(Generic[PydanticField]):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: PydanticField, field: ModelField):
        if value == '':
            return field.default
        return value


class Item(Schema):
    name: str
    description: str = None
    price: EmptyStrToDefault[float] = 0.0
    quantity: EmptyStrToDefault[int] = 0
    in_stock: EmptyStrToDefault[bool] = True


@api.post("/items-blank-default")
def update_with_form_default(request, item: Item = Form(...)):
    return item.dict()


@api.post('/upload')
def upload(request, file: UploadedFile = File(...)):
    data = file.read()
    print(data)
    return {'name': file.name, 'len': len(data)}


@api.post('/upload-many')
def upload_many(request, files: List[UploadedFile] = File(...)):
    return [f.name for f in files]


class UserDetails(Schema):
    first_name: str
    last_name: str
    birthdate: datetime.date


@api.post('/user')
def create_user(request, details: UserDetails = Form(...), file: UploadedFile = File(...)):
    return [details.dict(), file.name]


@api.post('/user-json')
def create_user_with_json(request, details: UserDetails, file: UploadedFile = File(...)):
    return [details.dict(), file.name]


class EmployeeFilterSchema(FilterSchema):
    first_name: Optional[str] = Field(q='first_name__icontains')
    last_name: Optional[str] = Field(q='last_name__icontains')
    birthdate: Optional[datetime.date]


class EmployeeSearchSchema(FilterSchema):
    # 在一个字段级别的查询是 OR 的关系
    # 字段级别的查询是 AND 的关系
    search: Optional[str] = Field(
        q=['first_name__icontains', 'last_name__icontains'])
    birthdate: Optional[datetime.date]


class EmployeeOrSearchSchema(FilterSchema):
    search: Optional[str] = Field(
        q=['first_name__icontains', 'last_name__icontains'],
        expression_connector='AND'
    )
    birthdate: Optional[datetime.date]

    class Config:
        expression_connector = 'OR'


@api.get('/list_employees', response=List[EmployeeSchema])
def list_filter_employees(request, filters: EmployeeFilterSchema = Query(...)):
    q = Q(cv__isnull=False) & Q(Case(When(cv='', then=False), default=True))
    employees = Employee.objects.all()
    employees = filters.filter(employees)
    print(employees)
    q &= filters.get_filter_expression()
    print(q)
    queryset = Employee.objects.filter(q)
    print(queryset.query)
    for qs in queryset:
        print(qs.cv == '')
    return queryset


@api.get('/list_search_employees', response=List[EmployeeSchema])
def list_search_employees(request, filters: EmployeeSearchSchema = Query(...)):
    employees = Employee.objects.all()
    employees = filters.filter(employees)
    return employees


@api.get('/list_or_search_employees', response=List[EmployeeSchema])
def list_or_search_employees(request, filters: EmployeeOrSearchSchema = Query(...)):
    employees = Employee.objects.all()
    employees = filters.filter(employees)
    return employees


class EmployeeIgnoreNullSchema(FilterSchema):
    search: Optional[str] = Field(
        q=['first_name__icontains', 'last_name__icontains'],
        expression_connector='OR'
    )
    cv: Optional[str] = Field(q='cv__icontains', ignore_one=False)

    class Config:
        ignore_none = True
        expression_connector = 'OR'


@api.get('list_ignore_null_employees', response=List[EmployeeSchema])
def list_ignore_null_employees(request, filters: EmployeeIgnoreNullSchema = Query(...)):
    employees = Employee.objects.all()
    print(employees)
    employees = filters.filter(employees)
    print(employees.query)
    print(Employee.objects.all().filter(cv__icontains=filters.cv).query)
    return employees


class EmployeeCustomFilterSchema(FilterSchema):
    search: Optional[str] = Field(
        q=['first_name__icontains', 'last_name__icontains'],
        expression_connector='OR'
    )
    cv: Optional[str]

    def filter_cv(self, cv: str) -> Q:
        q = Q()
        if cv:
            q = Q(cv__icontains=cv) | Q(
                Case(When(cv='', then=True), default=False))
        print('filter_cv')
        return q

    def custom_expression(self) -> Q:
        q = super().custom_expression()
        print(q)
        return q


@api.get('/list_custom_sechma_employees', response=List[EmployeeSchema])
def list_cstom_scema_employees(request, filters: EmployeeCustomFilterSchema = Query(...)):
    employees = Employee.objects.all()
    employees = filters.filter(employees)
    return employees


class DepartmentEmployeeSchema(Schema):
    id: int
    title: str
    employees: List[EmployeeSchema]


@api.get("/list_department_with_employees", response=List[DepartmentEmployeeSchema])
def list_department_with_employees(request):
    queryset = Department.objects.prefetch_related('employees').all()
    return queryset


class DepartmentModelSchema(ModelSchema):
    employees: List[EmployeeSchema]

    class Config:
        model = Department
        model_fields = '__all__'


class EmployeeDepartmentModelSchema(ModelSchema):
    department: DepartmentModelSchema

    class Config:
        model = Employee
        model_fields = '__all__'


@api.get('/list_employee_with_department', response=List[EmployeeDepartmentModelSchema])
def list_employee_with_department(request):
    # queryset = Employee.objects.select_related('department').all()
    queryset = Employee.objects.filter(
        id__in=(1, 3)).prefetch_related('department__employees').select_related('department').all()
    print(queryset)
    print(queryset.query)
    return queryset


class DepartmentParentSchema(ModelSchema):
    class Config:
        model = Department
        model_fields = '__all__'


class DepartmentChildrenSchema(DepartmentParentSchema):
    children: List[DepartmentParentSchema]

    class Config(DepartmentParentSchema.Config):
        pass


@api.get('/list_department_with_children', response=List[DepartmentChildrenSchema])
def list_department_with_children(request):
    queryset = Department.objects.prefetch_related('children').all()
    print(queryset)
    print(queryset.query)
    return queryset


@api.get("/list_employees_with_page", response=List[EmployeeSchema])
@pagination.paginate(pagination.PageNumberPagination, pass_parameter='pagination_info')
def list_employees_with_page(request, **kwargs):
    page = kwargs['pagination_info'].page
    print(page)
    return Employee.objects.all()


@api.get('/bearer', auth=AuthBearer())
def bearer(request):
    return {'token': request.auth}


class ApiKey(APIKeyQuery):
    param_name = 'api_key'

    def authenticate(self, request: HttpRequest, key: str | None) -> Any | None:
        try:
            print(key)
            return True
        except Exception as e:
            pass


@api.get('/apikey', auth=ApiKey())
def apikey(request):
    print(request.auth)
    return f'Hello {request.auth}'


class ServiceUnavailableError(Exception):
    pass


# initializing handler

@api.exception_handler(ServiceUnavailableError)
def service_unavailable(request, exc):
    return api.create_response(
        request,
        {"message": "Please retry later"},
        status=503,
    )
