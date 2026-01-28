from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Club, Event



# Signup Form

class SignupForm(UserCreationForm):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STUDENT', 'Student'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists. Please use another email.")
        return email

    def clean_role(self):
        role = self.cleaned_data.get('role')

        
        if role == 'ADMIN':
            if User.objects.filter(role='ADMIN').exists():
                raise forms.ValidationError(
                    "Only one Admin is allowed. An Admin is already registered."
                )
        return role


# Login Form (Email + Password)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


# Club Form (Admin)

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description']


# Assign Club Head Form (Admin)

class AssignClubHeadForm(forms.Form):
    club = forms.ModelChoiceField(queryset=Club.objects.all())
    club_head = forms.ModelChoiceField(
        queryset=User.objects.filter(role='STUDENT'),
        label="Select Student to Make Club Head"
    )



# Event Form (Admin & Club Head)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['club', 'title', 'description', 'date']
        
class AssignClubHeadForm(forms.Form):
    club = forms.ModelChoiceField(queryset=Club.objects.all())
    club_head = forms.ModelChoiceField(
        queryset=User.objects.filter(role='STUDENT'),
        label="Select New Club Head"
    )
