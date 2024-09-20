from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import render, get_object_or_404

from todo.models import ToDoList, ToDoTask, FlexItem


@login_required
def add_todo(request, list_id):
    # limit list size to 50
    user = request.user
    todo_list = get_object_or_404(ToDoList, id=list_id)
    todos = todo_list.tasks.all()

    # TODO: Add a message to the user that the list is full
    if todos.count() >= 100:
        return render(request, 'todo/partials/todos.html', {'todo_list_items': todos, 'todo_list': todo_list})

    text = request.POST.get('todo')
    item_type = request.POST.get('item_type')
    todos = None
    todo_list = None

    if text:
        user = request.user
        todo_list = get_object_or_404(ToDoList, id=list_id)
        if item_type == 'FLEX_ITEM':
            todo_list.tasks.create(list=list_id, title=text, type=ToDoTask.FLEX_ITEM)
        else:
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
    todo_list = ToDoList.objects.get(id=list_id)
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
    todo_list = ToDoList.objects.get(id=list_id)
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

    todo_list = get_object_or_404(ToDoList, id=list_id)
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


def flex_item(request, list_id, todo_id):
    item = ToDoTask.objects.get(id=todo_id)
    list = ToDoList.objects.get(id=list_id)
    context = {
        'item': item,
        'list': list,
    }
    return render(request, 'todo/partials/flex-item.html', context)


def add_sub_item(request, list_id, todo_id):
    data = QueryDict(request.body)
    text = data.get('title')
    list = ToDoList.objects.get(id=list_id)
    item = ToDoTask.objects.get(id=todo_id, list=list_id)
    sub_item = FlexItem.objects.create(title=text)
    item.sub_items.add(sub_item)
    context = {
        'item': item,
        'list': list,
    }
    return render(request, 'todo/partials/flex-item.html', context)


def delete_sub_item(request, list_id, todo_id, sub_item_id):
    item = ToDoTask.objects.get(id=todo_id, list_id=list_id)
    sub_item = item.sub_items.get(id=sub_item_id)
    sub_item.delete()
    context = {
        'item': item,
        'list': ToDoList.objects.get(id=list_id),
    }
    return render(request, 'todo/partials/flex-item.html', context)
