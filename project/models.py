from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'project'


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    completed = models.BooleanField()

    class Meta:
        db_table = 'task'
