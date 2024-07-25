from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import render, get_object_or_404, redirect

from todo.models import ToDoList


@login_required
def set_main_todo_list(request, list_id):
    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    if not todo_list.is_hidden:
        ToDoList.objects.filter(user=request.user).update(is_main=False)
        todo_list.is_main = True
        todo_list.save()
    return redirect('todo_list_view')


@login_required
def todo_list_todos(request, list_id):
    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    todos = todo_list.tasks.all()

    # sort by updated_at field in descending order
    todos = todos.order_by('-sort_timestamp')

    sorted_todos = sorted(todos, key=lambda x: x.order)

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }

    return render(request, 'todo/todo-list-todos.html', context)


@login_required
def hide_todo_list(request, list_id):
    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    if todo_list.is_default:
        todo_list.is_hidden = True
        todo_list.save()
    return redirect('todo_list_view')


@login_required
def sort_todos(request, list_id):
    todo_pks_order = request.POST.getlist('todo_order')
    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    todos = todo_list.tasks.all()

    sorted_todos = []

    for idx, todo_pk in enumerate(todo_pks_order, start=1):
        todo = todos.get(pk=todo_pk)
        todo.order = idx
        todo.save()
        sorted_todos.append(todo)

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }

    # Return the rendered template with the context
    return render(request, 'todo/partials/todos.html', context)


@login_required
def delete_todo_list(request, list_id):
    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    todo_list.is_hidden = True
    todo_list.delete()
    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)
    return render(request, 'todo/todo-lists.html', {'todo_lists': todo_lists})


@login_required
def edit_todo_list(request, list_id):
    data = QueryDict(request.body)
    text = data.get('name')

    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    todo_list.name = text
    todo_list.save()

    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)
    return render(request, 'todo/todo-lists.html', {'todo_lists': todo_lists})


@login_required
def add_todo_list(request):
    list_name = request.POST.get('list_name')

    if list_name:
        ToDoList.objects.create(user=request.user, name=list_name)

    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)
    todo_lists.order_by('-created_at')
    todo_lists.order_by('order')
    return render(request, 'todo/todo-lists.html', {'todo_lists': todo_lists})


@login_required
def todo_lists(request):
    items = ToDoList.objects.filter(user=request.user, is_hidden=False)
    items = items.order_by('-created_at')
    items = items.order_by('order')
    return render(request, 'todo/todo-lists-view.html', {'todo_lists': items})


@login_required
def sort_todo_lists(request):
    todo_lists_pks_order = request.POST.getlist('todo_list_order')
    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)

    sorted_todo_lists = []

    for idx, todo_list_pk in enumerate(todo_lists_pks_order, start=1):
        todo_list = todo_lists.get(pk=todo_list_pk)
        todo_list.order = idx
        todo_list.save()
        sorted_todo_lists.append(todo_list)

    return render(request, 'todo/todo-lists.html', {'todo_lists': sorted_todo_lists})


@login_required
def todo_list_view(request):
    items = ToDoList.objects.filter(user=request.user, is_hidden=False)
    items = items.order_by('-created_at')
    items = items.order_by('order')
    return render(request, 'todo/todo-lists-view.html', {'todo_lists': items})