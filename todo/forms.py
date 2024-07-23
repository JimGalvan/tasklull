from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ToDoList, TaskLullUser


class RegisterForm(UserCreationForm):
    class Meta:
        model = TaskLullUser
        fields = ["username", "email", "password1", "password2"]

        def clean_username(self):
            username = self.cleaned_data['username']
            if TaskLullUser.objects.filter(username__exact=username).exists():
                raise forms.ValidationError(f"The username {username} is already taken.")
            return username


class CreateListForm(forms.ModelForm):
    class Meta:
        model = ToDoList
        fields = ['name']
