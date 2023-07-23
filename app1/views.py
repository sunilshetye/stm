from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.http import JsonResponse
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



# from django.shortcuts import render, redirect
# from .forms import SignupForm

# from django.shortcuts import render, redirect

def signup(request):
    # Assuming you have a SignUpForm defined in forms.py for user registration
    from .forms import SignUpForm

    # Check if the user has already signed up (you need to replace this with your actual logic)
    user_already_signed_up = False  # Replace this with your actual logic to check if the user has signed up

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Process the form data and save the user (replace this with your actual user registration logic)
            form.save()
            return redirect('login')  # Redirect to the login page after successful sign up
    else:
        form = SignUpForm()

    context = {
        'form': form,
        'user_already_signed_up': user_already_signed_up,
    }

    return render(request, 'signup.html', context)




#announcement......>

from .forms import AnnouncementForm

def teacher_page(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'teacher_success.html')  # Render a success page or redirect as needed
    else:
        form = AnnouncementForm()

    return render(request, 'teacher_page.html', {'form': form})


#student page....>




def student_page(request):
    announcements = Announcement.objects.all()
    return render(request, 'student_page.html', {'announcements': announcements})


def homepage(request):
    return render(request,'homepage.html')



def record_action(request):
    if request.method == 'POST':
        announcement_text = request.POST.get('announcement')
        student_username = request.POST.get('username')
        try:
            announcement = Announcement.objects.get(message=announcement_text)
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

# Other views ...

def fetch_viewed_messages(request):
    if request.method == 'GET':
        # Fetch notifications associated with liked messages
        notifications = Notification.objects.all()

        # Create a list to store the viewed messages with the associated student name
        viewed_messages = []
        for notification in notifications:
            viewed_messages.append(f"{notification.student_username}: {notification.message}")

        return JsonResponse(viewed_messages, safe=False)
