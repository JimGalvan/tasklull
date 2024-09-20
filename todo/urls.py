from django.contrib.auth.views import logout_then_login
from django.urls import path

from .views import todo_list_views, todo_views, user_views

urlpatterns = [
    path('', user_views.index, name='index'),
    path('login/', user_views.Login.as_view(), name='login'),
    path('logout/', logout_then_login, {'login_url': '/'}, name='logout'),
    path("register/", user_views.RegisterView.as_view(), name="register"),
    path('accounts/profile/', user_views.profile_view, name='profile'),
]

todo_list_urlpatterns = [
    path('todo-lists-view/', todo_list_views.todo_list_view, name='todo_list_view'),
    path('todo-lists/', todo_list_views.todo_lists, name='todo_lists'),
    path('todo-lists/sort/', todo_list_views.sort_todo_lists, name='sort_todo_lists'),
    path('todo-lists/<int:list_id>/hide/', todo_list_views.hide_todo_list, name='hide_todo_list'),
    path('todo-lists/<int:list_id>/todos/', todo_list_views.todo_list_todos, name='todo_list_tasks'),
    path('todo-lists/<int:list_id>/set-main/', todo_list_views.set_main_todo_list, name='set_main_todo_list'),
    path('todo-lists/<int:list_id>/sort/', todo_list_views.sort_todos, name='sort'),
    path('todo-lists/<int:list_id>/delete/', todo_list_views.delete_todo_list, name='delete_todo_list'),
    path('todo-lists/<int:list_id>/edit/', todo_list_views.edit_todo_list, name='edit_todo_list'),
    path('todo-lists/add/', todo_list_views.add_todo_list, name='add_todo_list'),
    path('todo-lists/<int:list_id>/share/', todo_list_views.share_todo_list, name='share_todo_list'),
]

urlpatterns += todo_list_urlpatterns

todo_task_urlpatterns = [
    path('todo-lists/<int:list_id>/add_todo/', todo_views.add_todo, name='add_todo'),
    path('todo-lists/<int:list_id>/todo-task/<int:todo_id>/toggle/', todo_views.toggle_todo, name='toggle_todo'),
    path('todo-lists/<int:list_id>/todo-task/<int:todo_id>/delete/', todo_views.delete_todo, name='delete_todo'),
    path('todo-lists/<int:list_id>/todo-task/<int:todo_id>/edit/', todo_views.edit_todo, name='edit_todo'),
    path('todo-lists/<int:list_id>/todo-task/<int:todo_id>/flex-item/', todo_views.flex_item, name='flex_item'),
    path('todo-lists/<int:list_id>/todo-task/<int:todo_id>/add-sub-item/',
         todo_views.add_sub_item, name='add_sub_item'),
    path('delete_sub_item/<int:list_id>/<int:todo_id>/<int:sub_item_id>/', todo_views.delete_sub_item, name='delete_sub_item'),
]

urlpatterns += todo_task_urlpatterns
