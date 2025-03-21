from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher, Subject, Student,Attendance
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import SubjectSerializer
from django.http import JsonResponse,HttpResponseRedirect
from django.utils.timezone import now
from django.utils.timezone import localtime
import pytz
from django.utils.dateparse import parse_date
from datetime import date
from datetime import datetime
from django.utils.timezone import make_aware
from collections import defaultdict
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io,os
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from django.conf import settings
from django.utils.timezone import localdate
from django.template.loader import render_to_string


def teacher_profile(request):
    return render(request, 'myapp/teacher-profile.html')
def print_attendance(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    assigned_students = subject.students.all()
    start_date = request.GET.get('start_date', localdate())
    end_date = request.GET.get('end_date', start_date)

    try:
        formatted_start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        formatted_start_date = None

    try:
        formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        formatted_end_date = formatted_start_date

    attendance_records = Attendance.objects.filter(
        student__in=assigned_students,
        subject=subject,
        date__range=(start_date, end_date)
    ).order_by('date')

    student_attendance_map = defaultdict(lambda: {'time_in': None, 'time_out': None})

    for att in attendance_records:
        student_data = student_attendance_map[att.student.id]
        if att.time_in and not student_data['time_in']:
            student_data['time_in'] = att.time_in
        if att.time_out and not student_data['time_out']:
            student_data['time_out'] = att.time_out

    for student in assigned_students:
        student.attendance = student_attendance_map.get(student.id, None)

    html_content = render_to_string('myapp/test_print.html', {
        'assigned_students': assigned_students,
        'subject': subject,
        'start_date': formatted_start_date,
        'end_date': formatted_end_date,
    })

    return HttpResponse(html_content)


def get_attendance_by_date(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Ensure it's an AJAX request
        subject_id = request.GET.get('subject_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if subject_id and start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else start_date_obj
                subject = get_object_or_404(Subject, id=subject_id)
                students = subject.students.all()

                # Use defaultdict to store attendance data for each student
                attendance_dict = defaultdict(lambda: {
                    "time_in": "--",
                    "time_out": "--",
                    "status": "Absent"
                })

                attendance_records = Attendance.objects.filter(
                    subject=subject, date__range=(start_date_obj, end_date_obj)  # Use date range
                ).order_by("time_in")
                # Populate defaultdict with attendance records
                for attendance in attendance_records:
                    student_id = attendance.student.id
                    if attendance.time_in:
                        attendance_dict[student_id]["time_in"] = attendance.time_in.strftime("%I:%M %p")
                    if attendance.time_out:
                        attendance_dict[student_id]["time_out"] = attendance.time_out.strftime("%I:%M %p")
                    attendance_dict[student_id]["status"] = attendance.status  # Update status

                # Build final response data
                attendance_data = [
                    {
                        "student_id": student.id,
                        "full_name": student.full_name,
                        "course": student.course,
                        "year_section": student.year_section,
                        **attendance_dict[student.id]  # Merge attendance details
                    }
                    for student in students
                ]

                return JsonResponse({"data": attendance_data}, status=200)
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def mark_attendance(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        subject_id = request.POST.get("subject_id")
        action = request.POST.get("action")  # "Time In" or "Time Out"

        if not student_id or not subject_id or not action:
            return JsonResponse({"status": "error", "message": "Invalid data received."}, status=400)

        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)

        teacher_id = request.session.get("teacher_id")
        if not teacher_id:
            return JsonResponse({"status": "error", "message": "Unauthorized. Please log in again."}, status=403)

        teacher = get_object_or_404(Teacher, id=teacher_id)

        # Convert time to Manila Time
        manila_tz = pytz.timezone("Asia/Manila")
        current_time = localtime(now(), timezone=manila_tz).strftime("%I:%M %p")  # 12-hour format
        today_date = now().date()

        # Check if an attendance record already exists for this student, subject, and date
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            subject=subject,
            date=today_date,
            defaults={'teacher': teacher, 'status': 'Present'}
        )

        # If both time_in and time_out exist, do not allow further modifications
        if attendance.time_in and attendance.time_out:
            return JsonResponse({"status": "error", "message": "Attendance already recorded for today."}, status=400)

        if action == "Time In":
            if attendance.time_in:
                return JsonResponse({"status": "error", "message": "Time In already recorded for today."}, status=400)
            attendance.time_in = localtime(now())
            attendance.teacher = teacher
            attendance.save()
            return JsonResponse({"status": "success", "message": f"{student.full_name} Time In recorded.", "time": current_time, "field": "time_in"})

        elif action == "Time Out":
            if not attendance.time_in:
                return JsonResponse({"status": "error", "message": "Time In must be recorded first."}, status=400)
            if attendance.time_out:
                return JsonResponse({"status": "error", "message": "Time Out already recorded for today."}, status=400)
            attendance.time_out = localtime(now())
            attendance.teacher = teacher
            attendance.save()
            return JsonResponse({"status": "success", "message": f"{student.full_name} Time Out recorded.", "time": current_time, "field": "time_out"})

        else:
            return JsonResponse({"status": "error", "message": "Invalid or duplicate action."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


def teacher_dashboard(request):
    if 'teacher_username' not in request.session:
        return redirect('teacher-login')
    return render(request, 'myapp/teacher_dashboard.html')


def teacher_login(request):
    if 'teacher_username' in request.session:
        return redirect('teacher-dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            teacher = Teacher.objects.get(username=username)

            if check_password(password, teacher.password):
                request.session['teacher_id'] = teacher.id
                request.session['teacher_username'] = teacher.username
                request.session['teacher_name'] = teacher.full_name
                request.session['teacher_email'] = teacher.email
                messages.success(request, "You are logged in!")
                return redirect('teacher-dashboard')
            else:
                messages.warning(request, "Invalid Username or Password.")
        except Teacher.DoesNotExist:
            messages.warning(request,"Invalid username or password")  

    content = {'exclude_layout': True, }
    return render(request, 'myapp/teacher_login.html', content)

    
def update_teacher_profile(request):
    if request.method == 'POST':
        teacher_id = request.session.get('teacher_id')
        if not teacher_id:
            messages.error(request, 'Unauthorized access.')
            return redirect('teacher-login')

        teacher = Teacher.objects.get(id=teacher_id)
        teacher.username = request.POST.get('username')
        teacher.full_name = request.POST.get('full_name')
        teacher.email = request.POST.get('email')
        teacher.save()

        # Update session data
        request.session['teacher_username'] = teacher.username
        request.session['teacher_name'] = teacher.full_name
        request.session['teacher_email'] = teacher.email

        messages.success(request, 'Profile updated successfully.')
        return redirect('teacher-profile')

    return redirect('teacher-profile')

def custom_logout(request):
    request.session.flush()
    messages.success(request, 'You are logged out successfully!')

    return redirect('/')


def teacher_registration(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        hashed_password = make_password(password)

        teacher = Teacher(
            username = username,
            full_name=full_name,
            email=email,
            password = hashed_password
        )
        teacher.save()
        return redirect('teacher-login')
    
    content = {'exclude_layout': True}
    return render(request, 'myapp/teacher_register.html', content)


def student_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        student_id = request.POST.get("student_id")
        full_name = request.POST.get("full_name")
        course = request.POST.get("course")
        year_section = request.POST.get("year_section")
        email = request.POST.get("email")
        password = request.POST.get("password")
        hassed_password = make_password(password)
        
        student = Student(
            username = username,
            student_id = student_id,
            full_name = full_name,
            course = course,
            year_section = year_section,
            email = email,
            password = hassed_password
        )
        student.save()
        return redirect("teacher-login")
    content = {'exclude_layout': True}
    return render(request, 'myapp/student_register.html',content)


@api_view(['POST'])

def add_subject(request):
    if request.method == 'POST':
       teacher_username = request.session.get('teacher_username')
       if not teacher_username:
           return JsonResponse({'status': 'error', 'message': 'Teacher not found.'}, status=status.HTTP_400_BAD_REQUEST)
       
       try:
           teacher = Teacher.objects.get(username=teacher_username)
       except Teacher.DoesNotExist:
           return JsonResponse({'status':'error', 'message': 'Teacher not found.'},status= status.HTTP_400_BAD_REQUEST)
       
       data = request.data.copy()
       data['teacher'] = teacher.id

       serializer = SubjectSerializer(data=data)
   
       
       if serializer.is_valid():
           subject = serializer.save()
           return JsonResponse({
            'status': 'success',
            'message': 'Subject added successfully!',
            'subject': {
                'name': subject.name,
                'course_year_section': subject.course_year_section,
                'description': subject.description or 'No description available.',
                'created_at': subject.created_at.strftime('%B %d, %Y')
            }
        }, status=201)
    
       return Response({'status': 'error', 'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

def student_list(request):
    students = Student.objects.all()
    return render(request, 'myapp/student_list.html',{'students':students})

def teacher_subjects(request):
    teacher_username = request.session.get('teacher_username')

    if not request.session.get('teacher_username'):
        return redirect('teacher-login')
    teacher = Teacher.objects.get(username= teacher_username)

    subjects = Subject.objects.filter(teacher=teacher).order_by('-created_at').values()

    return render(request, 'myapp/teacher_subjects.html', {'subjects': subjects})


def student_attendance(request, id):
    subject = get_object_or_404(Subject, id=id)
    
    # Fetch students who are already assigned to the subject
    assigned_students = subject.students.all()

    today = localdate()

    # Fetch all attendance records for assigned students in this subject
    attendance_records = Attendance.objects.filter(
        student__in=assigned_students,
        subject=subject,
        date= today
    ).order_by('date')

    # Group attendance records by student ID
    student_attendance_map = defaultdict(lambda: {'time_in': None, 'time_out': None})

    for att in attendance_records:
        student_data = student_attendance_map[att.student.id]
        if att.time_in and not student_data['time_in']:
            student_data['time_in'] = att.time_in
        if att.time_out and not student_data['time_out']:
            student_data['time_out'] = att.time_out

    # Assign the merged attendance data to each student
    for student in assigned_students:
        student.attendance = student_attendance_map.get(student.id, None)
        if student.attendance:
            print(f"Student: {student.full_name}, Time In: {student.attendance['time_in']}, Time Out: {student.attendance['time_out']}")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        attendance_data = [
            {
                'student_name': student.full_name,
                'cys': f"{student.course} {student.year_section}",
                'time_in': localtime(data['time_in']).strftime("%I:%M %p") if data['time_in'] else "--",
                'time_out': localtime(data['time_out']).strftime("%I:%M %p") if data['time_out'] else "--",
                'status': "Present" if data['time_in'] else "Absent",
            }
            for student, data in student_attendance_map.items()
        ]
        return JsonResponse({'attendance': attendance_data})

    # Fetch students who are NOT assigned to this subject (available students)
    available_students = Student.objects.exclude(id__in=assigned_students.values_list('id', flat=True))

    if request.method == "POST":
        student_ids = request.POST.getlist("student_ids[]")  # Get selected student IDs from the modal
        for student_id in student_ids:
            student = get_object_or_404(Student, id=student_id)
            subject.students.add(student)  # Add student to the subject

        return JsonResponse({"message": "Students successfully added!", "status": "success"})
    
    return render(request, 'myapp/student_attendance.html', {
        'assigned_students': assigned_students, 
        'available_students': available_students, 
        'subject': subject,
        'all_attendance_records': attendance_records,  # Pass all attendance records to the template
    })

def add_students_to_subject(request, subject_id):
    if request.method == "POST":
        student_ids = request.POST.getlist("student_ids[]")
        subject = get_object_or_404(Subject, id=subject_id)

        for student_id in student_ids:
            student = get_object_or_404(Student, id=student_id)
            subject.students.add(student)

        messages.success(request, f"{len(student_ids)} student(s) added successfully!")

        return JsonResponse({"message": "Students successfully added!", "status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)


def envelope_view(request):
    content = {'exclude_layout': True, }
    return render(request, 'myapp/envelope.html',content)




