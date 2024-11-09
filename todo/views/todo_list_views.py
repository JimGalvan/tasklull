from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import QueryDict
from django.shortcuts import render, get_object_or_404, redirect

from todo.models import ToDoList, SharedList, TaskLullUser


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
    todo_list = get_object_or_404(ToDoList, id=list_id)

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
    todo_list = get_object_or_404(ToDoList, id=list_id)
    todos = todo_list.tasks.filter(pk__in=todo_pks_order)

    # Prepare the todos with new order values
    with transaction.atomic():
        for idx, todo_pk in enumerate(todo_pks_order, start=1):
            todo = todos.get(pk=todo_pk)
            todo.order = idx
            todo.save(update_fields=['order'])

    # Refetch sorted todos only once for rendering
    sorted_todos = todo_list.tasks.order_by('order')

    context = {
        'todo_list_items': sorted_todos,
        'todo_list': todo_list,
    }

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
    # limit the number of todo lists to 5
    # TODO - add a message to the user
    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)
    todo_lists.order_by('-created_at')
    todo_lists.order_by('order')

    if todo_lists.count() >= 10:
        return render(request, 'todo/todo-lists.html', {'todo_lists': todo_lists})

    list_name = request.POST.get('list_name')
    list_type = request.POST.get('list_type')

    if list_name:
        if list_type == "ToDoList":
            ToDoList.objects.create(user=request.user, name=list_name, type=ToDoList.TODO_LIST)
        elif list_type == "FlexList":
            ToDoList.objects.create(user=request.user, name=list_name, type=ToDoList.FLEX_LIST)
        else:
            ToDoList.objects.create(user=request.user, name=list_name)

    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)
    todo_lists.order_by('-created_at')
    todo_lists.order_by('order')

    # add shared lists
    todo_lists = add_shared_lists(request, todo_lists)

    return render(request, 'todo/todo-lists.html', {'todo_lists': todo_lists})


def add_shared_lists(request, todo_lists):
    shared_lists = SharedList.objects.filter(shared_with=request.user)
    for shared_list in shared_lists:
        todo_lists = todo_lists | ToDoList.objects.filter(pk=shared_list.todo_list.pk)
    return todo_lists


@login_required
def todo_lists(request):
    items = ToDoList.objects.filter(user=request.user, is_hidden=False)
    items = items.order_by('-created_at')
    items = items.order_by('order')
    items = add_shared_lists(request, items)
    return render(request, 'todo/todo-lists-view.html', {'todo_lists': items})


@login_required
def sort_todo_lists(request):
    todo_lists_pks_order = request.POST.getlist('todo_list_order')
    shared_lists_pks_order = request.POST.getlist('shared_list_order')
    todo_lists = ToDoList.objects.filter(user=request.user, is_hidden=False)

    sorted_todo_lists = []

    for idx, todo_list_pk in enumerate(todo_lists_pks_order, start=1):
        todo_list = todo_lists.get(pk=todo_list_pk)
        todo_list.order = idx
        todo_list.save()
        sorted_todo_lists.append(todo_list)

    # sort shared lists
    shared_sorted_todo_lists = []

    user = TaskLullUser.objects.get(username=request.user)
    user_shared_lists = SharedList.objects.filter(shared_with=user)

    for idx, shared_todo_list_pk in enumerate(shared_lists_pks_order, start=1):
        try:
            shared_todo_list = user_shared_lists.get(pk=shared_todo_list_pk)
            shared_todo_list.order = idx
            shared_todo_list.save()
            shared_sorted_todo_lists.append(shared_todo_list)
        except SharedList.DoesNotExist:
            pass

    sorted_todo_lists = add_shared_lists(request, shared_sorted_todo_lists)
    return render(request, 'todo/todo-lists.html', {'todo_lists': sorted_todo_lists})


@login_required
def todo_list_view(request):
    items = ToDoList.objects.filter(user=request.user, is_hidden=False)
    items = items.order_by('-created_at')
    items = items.order_by('order')
    items = add_shared_lists(request, items)
    return render(request, 'todo/todo-lists-view.html', {'todo_lists': items})


@login_required
def share_todo_list(request, list_id):
    user_to_share_with = request.POST.get('user_to_share_with')
    todo_list = get_object_or_404(ToDoList, id=list_id, user=request.user)

    second_user = get_object_or_404(TaskLullUser, username=user_to_share_with)
    if not second_user:
        return None

    shared_list = SharedList.objects.create(todo_list=todo_list, shared_with=second_user, shared_by=request.user)
    todo_list.shared_list = shared_list
    todo_list.is_shared = True
    todo_list.save()

    second_user.shared_lists.add(todo_list)
    items = ToDoList.objects.filter(user=request.user, is_hidden=False)
    items = add_shared_lists(request, items)
    return render(request, 'todo/todo-lists.html', {'todo_lists': items})
