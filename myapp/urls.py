from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .import views
from .views import mark_attendance
from .views import pdf_test_page, pdf_preview, get_attendance_by_date


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
    path('mark-attendance/', views.mark_attendance, name='mark-attendance'),
    path('pdf-test-page/', pdf_test_page, name='pdf_test_page'),
    path('pdf-preview/', pdf_preview, name='pdf_preview'),
    path('get_attendance_by_date/', get_attendance_by_date, name='get_attendance_by_date'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)