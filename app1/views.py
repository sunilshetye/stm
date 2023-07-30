from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import AnnouncementForm, LoginForm, SignUpForm
from .models import Announcement


def signup_page(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def toggle_acknowledgement(request):
    id = request.GET['notification']
    notification = Notification.objects.get(id=id)
    notification.acknowledgement = 1 if notification.acknowledgement == 0 else 0
    notification.timestamp = timezone.now()
    notification.save()
    return JsonResponse({'success': True,
                         'acknowledgement': notification.acknowledgement})


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            print('user=', user, user.__dict__)
            if user is not None:
                login(request, user)
                if hasattr(user, 'administrator'):
                    page = 'administrator'
                elif hasattr(user, 'student'):
                    page = 'student'
                elif hasattr(user, 'teacher'):
                    page = 'teacher'
                else:
                    page = 'homepage'
                return redirect(page)
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def administrator_page(request):
    user = request.user
    if not hasattr(user, 'administrator'):
        raise PermissionError('not an administrator')
    announcements = Announcement.objects.all()
    return render(request, 'administrator.html', {'announcements': announcements})


@login_required
def student_page(request):
    user = request.user
    if not hasattr(user, 'student'):
        raise PermissionError('not a student')
    announcements = Announcement.objects.filter(notification__student=user).values('message', 'timestamp', 'teacher__name', 'notification__id', 'notification__acknowledgement')
    return render(request, 'student.html', {'announcements': announcements})


@login_required
def teacher_page(request):
    user = request.user
    if not hasattr(user, 'teacher'):
        raise PermissionError('not a teacher')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return render(request, 'teacher_success.html')  # Render a success page or redirect as needed
    else:
        form = AnnouncementForm(request=request)

    return render(request, 'teacher.html', {'form': form})


def homepage(request):
    return render(request, 'homepage.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('homepage')  # Replace 'homepage' with the URL name for your homepage view


def record_action(request):
    if request.method == 'POST':
        announcement_text = request.POST.get('announcement')
        try:
            Announcement.objects.create(message=announcement_text)
            return JsonResponse({'success': True})
        except Announcement.DoesNotExist:
            pass
    return JsonResponse({'success': False})


def fetch_notifications(request):
    notifications = Notification.objects.all()
    data = []
    for notification in notifications:
        data.append({
            'teacher_name': notification.teacher.name,
            'message': notification.message,
            'student_username': notification.student.username
        })
    return JsonResponse(data, safe=False)


def fetch_viewed_messages(request):
    if request.method == 'GET':
        notifications = Notification.objects.all()

        viewed_messages = []
        for notification in notifications:
            viewed_messages.append(f"{notification.student_username}: {notification.message}")

        return JsonResponse(viewed_messages, safe=False)
