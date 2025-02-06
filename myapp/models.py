from django.db import models


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
