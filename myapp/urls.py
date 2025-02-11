from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .import views

urlpatterns = [
    path('', views.teacher_login, name="teacher-login"),
    path("teacher-dashboard/", views.teacher_dashboard, name="teacher-dashboard"),
    path("teacher-register/", views.teacher_registration, name="teacher-register"),
    path("custom-logout/", views.custom_logout, name="custom-logout"),
    path("student-list/", views.student_list, name="student-list"),
    path("teacher-subjects/", views.teacher_subjects, name="teacher-subjects"),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('subjects/', views.teacher_subjects, name='subject-list'),
    path('student-attendance/<int:id>/', views.student_attendance, name='student-attendance'),
    path("attendance/<int:subject_id>/add-students/", views.add_students_to_subject, name="add-students-to-subject"),
    path('student-register/', views.student_register, name='student-register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)