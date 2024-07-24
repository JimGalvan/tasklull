from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django import forms


class TaskLullUser(AbstractUser):

    def save(self, *args, **kwargs):
        if TaskLullUser.objects.filter(username__exact=self.username).exclude(pk=self.pk).exists():
            raise ValidationError(f"The username {self.username} is already taken.")

        if TaskLullUser.objects.filter(email__exact=self.email).exclude(pk=self.pk).exists():
            raise forms.ValidationError(f"The email {self.email} is already in use.")

        super().save(*args, **kwargs)


class ToDoList(models.Model):
    user = models.ForeignKey(TaskLullUser, on_delete=models.CASCADE, related_name='todolists')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ToDoTask(models.Model):
    TODO = 'TODO'
    TO_COMPLETE = 'TO_COMPLETE'
    COMPLETE = 'COMPLETE'
    STATUS_CHOICES = [
        (TODO, 'To Do'),
        (TO_COMPLETE, 'To Complete'),
        (COMPLETE, 'Complete'),
    ]

    list = models.ForeignKey(ToDoList, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    sort_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        update_sort_timestamp = kwargs.pop('update_sort_timestamp', True)

        # Call the superclass's save method first to update updated_at
        super(ToDoTask, self).save(*args, **kwargs)

        if update_sort_timestamp:
            # Directly update sort_timestamp in the database to match updated_at
            # without triggering another save operation
            ToDoTask.objects.filter(pk=self.pk).update(sort_timestamp=F('updated_at'))
