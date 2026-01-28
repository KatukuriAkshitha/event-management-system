from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Custom User Manager

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, role='STUDENT'):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            role='ADMIN'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CLUBHEAD', 'Club Head'),
        ('STUDENT', 'Student'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
# Club Model

class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    # Only ONE club head per club
    club_head = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'CLUBHEAD'}
    )

    def __str__(self):
        return self.name
# Event Model
class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CLUBHEAD'}
    )

    def __str__(self):
        return f"{self.title} - {self.club.name}"

# Event Registration Model

class EventRegistration(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'event')  # One student cannot register twice

    def __str__(self):
        return f"{self.student.email} -> {self.event.title}"
