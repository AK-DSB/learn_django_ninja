from ninja import NinjaAPI, Schema, ModelSchema

api = NinjaAPI()


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
