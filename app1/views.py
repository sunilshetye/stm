from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import defaultfilters
from django.utils import timezone
from .forms import AnnouncementForm, LoginForm, SignUpForm
from .models import Announcement, Notification


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
    user = request.user
    if not hasattr(user, 'student'):
        raise PermissionError('not a student')
    student = user.student
    id = request.GET['announcement']
    announcement = Announcement.objects.get(id=id)
    teacher = announcement.teacher
    notification = Notification.objects.get(student=student, announcement=announcement)
    notification.acknowledgement = 1 if notification.acknowledgement == 0 else 0
    notification.timestamp = timezone.now()
    notification.save()
    channel_layer = get_channel_layer()
    send_message = {
        'type': 'announcement_message',
        'message_type': 'acknowledgement',
        'announcement': announcement.id,
        'student': student.id,
        'student_name': student.name,
        'acknowledgement': notification.acknowledgement,
    }
    if channel_layer is not None:
        group_name = f'announcement_{student.username}'
        async_to_sync(channel_layer.group_send)(group_name, send_message)
        group_name = f'announcement_{teacher.username}'
        async_to_sync(channel_layer.group_send)(group_name, send_message)
    return JsonResponse({'success': True,
                         'acknowledgement': notification.acknowledgement})


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
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
    return render(request, 'administrator.html', {'announcements': announcements, 'administrator': user.administrator})


@login_required
def student_page(request):
    user = request.user
    if not hasattr(user, 'student'):
        raise PermissionError('not a student')
    announcements = Announcement.objects.filter(notification__student=user).order_by('-timestamp').values('id', 'message', 'timestamp', 'teacher__name', 'notification__acknowledgement')
    return render(request, 'student.html', {'announcements': announcements, 'student': user.student})


@login_required
def teacher_page(request):
    user = request.user
    if not hasattr(user, 'teacher'):
        raise PermissionError('not a teacher')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request=request)
        if form.is_valid():
            (announcement, user_names) = form.save()
            channel_layer = get_channel_layer()
            timestamp = defaultfilters.date(timezone.localtime(announcement.timestamp), "M. j, Y, g:i a")
            send_message = {
                'type': 'announcement_message',
                'message_type': 'announcement_add',
                'announcement': announcement.id,
                'announcement_teacher': announcement.teacher.name,
                'announcement_message': announcement.message,
                'announcement_timestamp': timestamp,
            }
            if channel_layer is not None:
                group_name = f'announcement_{user.username}'
                async_to_sync(channel_layer.group_send)(group_name, send_message)
                for user_name in user_names:
                    group_name = f'announcement_{user_name}'
                    async_to_sync(channel_layer.group_send)(group_name, send_message)

            return JsonResponse({'success': True, 'announcement': announcement.id})
        return JsonResponse({'success': False})

    form = AnnouncementForm(request=request)
    data = fetch_data(request)
    return render(request, 'teacher.html', {'form': form, 'teacher': user.teacher, 'announcements': data})


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


@login_required
def fetch_data(request):
    user = request.user
    if not hasattr(user, 'teacher'):
        raise PermissionError('not a teacher')
    teacher = user.teacher

    # Fetch announcements where the teacher is the currently logged-in user
    announcements = Announcement.objects.filter(teacher=teacher).order_by('-timestamp')

    # Fetch notifications where the announcement is from the teacher and acknowledgement is true
    data = []

    for announcement in announcements:
        notifications = Notification.objects.filter(announcement=announcement, acknowledgement=True).order_by('-timestamp')
        students = []
        for notification in notifications:
            students.append({'id': notification.student.id, 'name': notification.student.name})
        data.append({
            'id': announcement.id,
            'message': announcement.message,
            'timestamp': announcement.timestamp,
            'students': students,
        })

    return data
