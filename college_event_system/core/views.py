from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Club, Event, EventRegistration
from .forms import SignupForm, LoginForm, ClubForm, AssignClubHeadForm, EventForm
from .forms import EventForm
from django.contrib import messages
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Only one admin allowed
            if user.role == 'ADMIN':
                if User.objects.filter(role='ADMIN').exists():
                    messages.error(request, "Only one Admin can be registered.")
                    return render(request, 'signup.html', {'form': form})
                user.is_staff = True

            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
        # else:
        #     messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.role == 'STUDENT':
                    return redirect('student_dashboard')
                elif user.role == 'CLUBHEAD':
                    return redirect('clubhead_dashboard')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    return render(request, 'login.html', {'form': form})
# ADMIN LOGIN
def admin_login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user and user.role == 'ADMIN':
                login(request, user)
                return redirect('admin_dashboard')
            else:
                return render(request, 'admin_login.html', {'form': form, 'error': 'Invalid Admin credentials'})
    return render(request, 'admin_login.html', {'form': form})

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')
# ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('login')

    clubs = Club.objects.all()
    students = User.objects.filter(role='STUDENT')
    registrations = EventRegistration.objects.all()
    events = Event.objects.all()

    return render(request, 'admin_dashboard.html', {
        'clubs': clubs,
        'students': students,
        'registrations': registrations,
        'events': events
    })



# ADD CLUB

@login_required
def add_club(request):
    if request.method == 'POST':
        form = ClubForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ClubForm()
    return render(request, 'add_club.html', {'form': form})

# ASSIGN CLUB HEAD (One per Club)

@login_required
def assign_clubhead(request):
    if request.method == 'POST':
        form = AssignClubHeadForm(request.POST)
        if form.is_valid():
            club = form.cleaned_data['club']
            student = form.cleaned_data['club_head']
            if club.club_head:
                return render(request, 'assign_clubhead.html', {
                    'form': form,
                    'error': 'This club already has a Club Head!'
                })

            # Update student role
            student.role = 'CLUBHEAD'
            student.save()

            # Assign club head
            club.club_head = student
            club.save()

            return redirect('admin_dashboard')
    else:
        form = AssignClubHeadForm()
    return render(request, 'assign_clubhead.html', {'form': form})


# CLUB HEAD DASHBOARD

@login_required
def clubhead_dashboard(request):
    club = Club.objects.get(club_head=request.user)
    events = Event.objects.filter(club=club)
    return render(request, 'clubhead_dashboard.html', {'club': club, 'events': events})

# CLUB HEAD ADD EVENT (Only Own Club)

@login_required
def clubhead_add_event(request):
    club = Club.objects.get(club_head=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            return redirect('clubhead_dashboard')
    else:
        form = EventForm(initial={'club': club})

    return render(request, 'clubhead_add_event.html', {'form': form})


# STUDENT DASHBOARD
@login_required
def student_dashboard(request):
    if request.user.role != 'STUDENT':
        return redirect('login')

    clubs = Club.objects.all()
    return render(request, 'student_dashboard.html', {'clubs': clubs})
@login_required
def student_events(request):
    if request.user.role != 'STUDENT':
        return redirect('login')

    events = Event.objects.all()
    registered_events = EventRegistration.objects.filter(
        student=request.user
    ).values_list('event_id', flat=True)

    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        EventRegistration.objects.get_or_create(
            student=request.user,
            event=event
        )

        return redirect('student_events')

    return render(request, 'student_events.html', {
        'events': events,
        'registered_events': registered_events
    })


# STUDENT VIEW EVENTS & REGISTER

@login_required
def student_events(request):
    if request.user.role != 'STUDENT':
        return redirect('login')

    events = Event.objects.all()

    registered_events = EventRegistration.objects.filter(
        student=request.user
    ).values_list('event_id', flat=True)

    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        obj, created = EventRegistration.objects.get_or_create(
            student=request.user,
            event=event
        )

        if created:
            messages.success(request, "You have successfully registered for the event.")
        else:
            messages.warning(request, "You are already registered for this event.")

        return redirect('student_events')

    return render(request, 'student_events.html', {
        'events': events,
        'registered_events': registered_events
    })

@login_required
def admin_add_event(request):
    if request.user.role != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect('admin_dashboard')
    else:
        form = EventForm()

    return render(request, 'add_event.html', {'form': form})


# UPDATE CLUB

@login_required
def update_club(request, club_id):
    if request.user.role != 'ADMIN':
        return redirect('login')

    club = get_object_or_404(Club, id=club_id)

    if request.method == 'POST':
        form = ClubForm(request.POST, instance=club)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ClubForm(instance=club)

    return render(request, 'update_club.html', {'form': form})



# DELETE CLUB
@login_required
def delete_club(request, club_id):
    if request.user.role != 'ADMIN':
        return redirect('login')

    club = get_object_or_404(Club, id=club_id)
    club.delete()
    return redirect('admin_dashboard')

# UPDATE EVENT

@login_required
def update_event(request, event_id):
    if request.user.role != 'ADMIN':
        return redirect('login')

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = EventForm(instance=event)

    return render(request, 'update_event.html', {'form': form})

@login_required
def delete_club(request, club_id):
    if request.user.role != 'ADMIN':
        return redirect('login')

    club = get_object_or_404(Club, id=club_id)

    if request.method == "POST":
     
        if club.club_head:
            club_head_user = club.club_head
            club_head_user.role = 'STUDENT'
            club_head_user.save()
        club.delete()
        return redirect('admin_dashboard')

    return render(request, 'delete_club.html', {'club': club})

# DELETE EVENT

@login_required
def delete_event(request, event_id):
    if request.user.role != 'ADMIN':
        return redirect('login')

    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('admin_dashboard')
@login_required
def assign_clubhead(request):
    if request.user.role != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':
        form = AssignClubHeadForm(request.POST)
        if form.is_valid():
            club = form.cleaned_data['club']
            new_head = form.cleaned_data['club_head']

            # If club already has a head, revert old head to STUDENT
            if club.club_head:
                old_head = club.club_head
                old_head.role = 'STUDENT'
                old_head.save()

            # Assign new club head
            new_head.role = 'CLUBHEAD'
            new_head.save()

            club.club_head = new_head
            club.save()

            return redirect('admin_dashboard')
    else:
        form = AssignClubHeadForm()

    return render(request, 'assign_clubhead.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def register_event(request, event_id):
    # your logic here
    return render(request, 'register_event.html')