from typing import List
from ninja import Router

router = Router()


@router.get('/project/{project_id}/tasks/')
def task_list(request):
    user_project = request.user.project_set
    return {}
