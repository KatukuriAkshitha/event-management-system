from django.urls import path
from . import views

urlpatterns = [
    # FIRST PAGE (Student / Club Head Login)
    path('', views.login_view, name='login'),

    # Admin login separate
    path('admin-login/', views.admin_login_view, name='admin_login'),

    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-club/', views.add_club, name='add_club'),
    path('assign-clubhead/', views.assign_clubhead, name='assign_clubhead'),

    path('clubhead-dashboard/', views.clubhead_dashboard, name='clubhead_dashboard'),
    path('clubhead-add-event/', views.clubhead_add_event, name='clubhead_add_event'),

    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-events/', views.student_events, name='student_events'),

    path('admin-add-event/', views.admin_add_event, name='admin_add_event'),
    path('update-club/<int:club_id>/', views.update_club, name='update_club'),
    path('delete-club/<int:club_id>/', views.delete_club, name='delete_club'),
    path('update-event/<int:event_id>/', views.update_event, name='update_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('register-event/<int:event_id>/', views.register_event, name='register_event'),
]