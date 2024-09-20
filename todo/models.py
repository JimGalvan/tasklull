from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F


class TaskLullUser(AbstractUser):
    shared_lists = models.ManyToManyField('ToDoList', related_name='shared_with_users', blank=True)

    def save(self, *args, **kwargs):
        if TaskLullUser.objects.filter(username__exact=self.username).exclude(pk=self.pk).exists():
            raise ValidationError(f"The username {self.username} is already taken.")

        if TaskLullUser.objects.filter(email__exact=self.email).exclude(pk=self.pk).exists():
            raise ValidationError(f"The email {self.email} is already in use.")

        super().save(*args, **kwargs)


class FlexItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    sort_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        update_sort_timestamp = kwargs.pop('update_sort_timestamp', True)

        # Call the superclass's save method first to update updated_at
        super(FlexItem, self).save(*args, **kwargs)

        if update_sort_timestamp:
            # Directly update sort_timestamp in the database to match updated_at
            # without triggering another save operation
            FlexItem.objects.filter(pk=self.pk).update(sort_timestamp=F('updated_at'))

class ToDoList(models.Model):
    TODO_LIST = 'TODO_LIST'
    FLEX_LIST = 'FLEX_LIST'

    LIST_TYPE_CHOICES = [
        (TODO_LIST, 'To Do List'),
        (FLEX_LIST, 'Flex List'),
    ]

    type = models.CharField(max_length=20, choices=LIST_TYPE_CHOICES, default='TODO_LIST')
    user = models.ForeignKey(TaskLullUser, on_delete=models.CASCADE, related_name='todolists')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_shared = models.BooleanField(default=False)
    shared_list = models.ForeignKey('SharedList', on_delete=models.CASCADE, blank=True, null=True)

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

    FLEX_ITEM = 'FLEX_ITEM'
    TODO_ITEM = 'TODO_ITEM'

    TYPE_CHOICES = [
        (FLEX_ITEM, 'Flex Item'),
        (TODO_ITEM, 'To Do Item'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TODO_ITEM)
    list = models.ForeignKey(ToDoList, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    sort_timestamp = models.DateTimeField(auto_now_add=True)
    sub_items = models.ManyToManyField(FlexItem, blank=True)

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


class SharedList(models.Model):
    todo_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE, null=True)
    shared_with = models.ForeignKey(TaskLullUser, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(TaskLullUser, related_name='shared_by', on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    sort_timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.todo_list} shared with {self.shared_with}"

    def save(self, *args, **kwargs):
        update_sort_timestamp = kwargs.pop('update_sort_timestamp', True)
        super(SharedList, self).save(*args, **kwargs)
        if update_sort_timestamp:
            SharedList.objects.filter(pk=self.pk).update(sort_timestamp=models.F('shared_at'))
