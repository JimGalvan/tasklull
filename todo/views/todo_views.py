from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import render, get_object_or_404

from todo.models import ToDoList, ToDoTask


@login_required
def add_todo(request, list_id):
    # limit list size to 50
    user = request.user
    todo_list = get_object_or_404(ToDoList, id=list_id)
    todos = todo_list.tasks.all()

    # TODO: Add a message to the user that the list is full
    if todos.count() >= 50:
        return render(request, 'todo/partials/todos.html', {'todo_list_items': todos, 'todo_list': todo_list})

    text = request.POST.get('todo')
    todos = None
    todo_list = None

    if text:
        user = request.user
        todo_list = get_object_or_404(ToDoList, id=list_id)
        todo_list.tasks.create(list=list_id, title=text)
        todos = todo_list.tasks.all()

    # sort by updated_at field in descending order
    todos = todos.order_by('-sort_timestamp')

    sorted_todos = sorted(todos, key=lambda x: x.order)

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }

    return render(request, 'todo/partials/todos.html', context)


@login_required
def toggle_todo(request, list_id, todo_id):
    user = request.user
    todo_list = user.todolists.get(id=list_id)
    todo = todo_list.tasks.get(id=todo_id)

    if todo.status == ToDoTask.TODO:
        todo.status = ToDoTask.COMPLETE
        todo.save()
    else:
        todo.status = ToDoTask.TODO
        todo.save()

    todos = todo_list.tasks.all()
    todos = todos.order_by('-sort_timestamp')

    sorted_todos = sorted(todos, key=lambda x: x.order)

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }
    return render(request, 'todo/partials/todos.html', context)

@login_required
def delete_todo(request, list_id, todo_id):
    user = request.user
    todo_list = user.todolists.get(id=list_id)
    todo = todo_list.tasks.get(id=todo_id)

    todo.delete()
    todos = todo_list.tasks.all()

    # sort by updated_at field in descending order
    todos = todos.order_by('-sort_timestamp')

    sorted_todos = sorted(todos, key=lambda x: x.order)

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }

    return render(request, 'todo/partials/todos.html', context)


@login_required
def edit_todo(request, list_id, todo_id):
    data = QueryDict(request.body)
    text = data.get('todo')

    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)
    todos = todo_list.tasks.all()
    todo = todos.get(id=todo_id)

    todo.title = text
    todo.save(update_sort_timestamp=False)

    # sort by updated_at field in descending order
    todos = todos.order_by('-sort_timestamp')

    sorted_todos = sorted(todos, key=lambda x: x.order)

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }

    return render(request, 'todo/partials/todos.html', context)