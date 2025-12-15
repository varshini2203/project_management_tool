from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Project, TaskList, Task, Comment

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("project_list")
    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("project_list")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, "project_list.html", {"projects": projects})

@login_required
def project_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        if name:
            project = Project.objects.create(
                name=name,
                description=description,
                owner=request.user,
            )
            # create default lists
            TaskList.objects.create(project=project, title="To Do")
            TaskList.objects.create(project=project, title="Doing")
            TaskList.objects.create(project=project, title="Done")
            return redirect("project_list")
    return render(request, "project_create.html")

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    tasklists = TaskList.objects.filter(project=project).order_by("id")
    if request.method == "POST":
        title = request.POST.get("title")
        list_id = request.POST.get("task_list_id")
        if title and list_id:
            task_list = get_object_or_404(TaskList, pk=list_id, project=project)
            Task.objects.create(title=title, task_list=task_list)
    tasklists = TaskList.objects.filter(project=project).order_by("id")
    return render(request, "project_detail.html", {"project": project, "tasklists": tasklists})
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, task_list__project__owner=request.user)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Comment.objects.create(task=task, author=request.user, text=text)
    comments = task.comments.order_by("-created_at")
    return render(request, "task_detail.html", {"task": task, "comments": comments})
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        project.name = request.POST.get("name", project.name)
        project.description = request.POST.get("description", project.description)
        project.save()
        return redirect("project_detail", pk=project.pk)
    return render(request, "project_edit.html", {"project": project})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        project.delete()
        return redirect("project_list")
    return render(request, "project_delete.html", {"project": project})
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, task_list__project__owner=request.user)
    if request.method == "POST":
        if "save_task" in request.POST:
            task.title = request.POST.get("title", task.title)
            task.description = request.POST.get("description", task.description)
            due = request.POST.get("due_date")
            if due:
                task.due_date = due
            task.save()
        elif "add_comment" in request.POST:
            text = request.POST.get("text")
            if text:
                Comment.objects.create(task=task, author=request.user, text=text)
    comments = task.comments.order_by("-created_at")
    return render(request, "task_detail.html", {"task": task, "comments": comments})
@login_required
def move_task(request, task_id, direction):
    task = get_object_or_404(Task, id=task_id, task_list__project__owner=request.user)
    lists = list(TaskList.objects.filter(project=task.task_list.project).order_by("id"))
    current_index = lists.index(task.task_list)

    if direction == "left" and current_index > 0:
        task.task_list = lists[current_index - 1]
        task.save()
    elif direction == "right" and current_index < len(lists) - 1:
        task.task_list = lists[current_index + 1]
        task.save()

    return redirect("project_detail", pk=task.task_list.project.id)
