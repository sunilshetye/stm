from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import AnnouncementForm, LoginForm, SignUpForm
from .models import Announcement


def login(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page or a success page
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = SignUpForm()

    context = {
        'form': form,
    }

    return render(request, 'signup.html', context)


def teacher_page(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'teacher_success.html')  # Render a success page or redirect as needed
    else:
        form = AnnouncementForm()

    return render(request, 'teacher_page.html', {'form': form})


def student_page(request):
    announcements = Announcement.objects.all()
    return render(request, 'student_page.html', {'announcements': announcements})


def homepage(request):
    return render(request, 'homepage.html')


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
    notifications = Announcement.objects.all()
    data = []
    for notification in notifications:
        data.append({
            'teacher_name': notification.teacher.name,
            'message': notification.message,
            'student_username': notification.student_username
        })
    return JsonResponse(data, safe=False)


def fetch_viewed_messages(request):
    if request.method == 'GET':
        # Fetch notifications associated with liked messages
        notifications = Announcement.objects.all()

        # Create a list to store the viewed messages with the associated student name
        viewed_messages = []
        for notification in notifications:
            viewed_messages.append(f"{notification.student_username}: {notification.message}")

        return JsonResponse(viewed_messages, safe=False)
