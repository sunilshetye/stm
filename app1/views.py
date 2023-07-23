from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse
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

    context = {
        'form': form,
    }

    return render(request, 'signup.html', context)


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
                    page = 'administrator_page'
                elif hasattr(user, 'student'):
                    page = 'student_page'
                elif hasattr(user, 'teacher'):
                    page = 'teacher_page'
                else:
                    page = 'homepage'
                return redirect(page)
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def administrator_page(request):
    announcements = Announcement.objects.all()
    return render(request, 'administrator_page.html', {'announcements': announcements})


def student_page(request):
    announcements = Announcement.objects.all()
    return render(request, 'student_page.html', {'announcements': announcements})


def teacher_page(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return render(request, 'teacher_success.html')  # Render a success page or redirect as needed
    else:
        form = AnnouncementForm(request=request)

    return render(request, 'teacher_page.html', {'form': form})


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
        notifications = Announcement.objects.all()

        viewed_messages = []
        for notification in notifications:
            viewed_messages.append(f"{notification.student_username}: {notification.message}")

        return JsonResponse(viewed_messages, safe=False)
