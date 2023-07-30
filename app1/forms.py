from django import forms
from django.core.validators import validate_slug
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Administrator, Student, Teacher, Announcement, Notification


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class SignUpForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), max_length=32, validators=[validate_slug])
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), min_length=2, max_length=32)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), min_length=2, max_length=32)
    role = forms.ChoiceField(choices=[('', 'Select Role'), ('administrator', 'Administrator'), ('student', 'Student'), ('teacher', 'Teacher')])

    class Meta:
        model = User
        fields = ['username', 'name', 'password']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password', '')
        confirm_password = self.cleaned_data.get('confirm_password', '')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        role = self.cleaned_data.get('role', '')
        if commit:
            user.save()
            if role == 'administrator':
                administrator = Administrator(user_ptr=user)
                administrator.save_base(raw=True)
            elif role == 'student':
                student = Student(user_ptr=user)
                student.save_base(raw=True)
            elif role == 'teacher':
                teacher = Teacher(user_ptr=user)
                teacher.save_base(raw=True)
        return user


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['message']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(AnnouncementForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        announcement = super().save(commit=False)
        announcement.teacher = self.request.user.teacher
        if commit:
            announcement.save()
            students = Student.objects.all()
            for student in students:
                notification = Notification(student=student, announcement=announcement)
                notification.save()
        return announcement
