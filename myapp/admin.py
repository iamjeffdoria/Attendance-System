from django.contrib import admin
from .models import Teacher,Subject,Student, Attendance


admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Attendance)
# Register your models here.
