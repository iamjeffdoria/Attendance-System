from django.db import models
from django.utils.timezone import now

class Teacher(models.Model):
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) 
   


    def __str__(self):
        return self.full_name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    course_year_section = models.CharField(max_length=100, default="default_course_year_section")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="subjects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    username = models.CharField(max_length=255, unique=True, default="default_username")
    student_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    course = models.CharField(max_length=100)  
    year_section = models.CharField(max_length=50, blank=True, null=True) 
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=255) 
    subjects = models.ManyToManyField(Subject, related_name="students") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late',)
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendance_records")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="attendance_records")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateField(default=now)  # Ensure date is set explicitly
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.status} ({self.date})"

