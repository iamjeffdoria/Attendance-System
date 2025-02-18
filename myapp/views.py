from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher, Subject, Student
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import SubjectSerializer
from django.http import JsonResponse,HttpResponseRedirect



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
                request.session['teacher_username'] = teacher.username
                request.session['teacher_name'] = teacher.full_name
                messages.success(request, "You are logged in!")
                return redirect('teacher-dashboard')
            else:
                messages.warning(request, "Invalid Username or Password.")
        except Teacher.DoesNotExist:
            messages.warning(request,"Invalid username or password")     

    content = {'exclude_layout': True, }
    return render(request, 'myapp/teacher_login.html', content)

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
        'subject': subject
    })

def add_students_to_subject(request, subject_id):
    if request.method == "POST":
        student_ids = request.POST.getlist("student_ids[]")
        subject = get_object_or_404(Subject, id=subject_id)

        for student_id in student_ids:
            student = get_object_or_404(Student, id=student_id)
            subject.students.add(student)
            messages.success(request, "Student added successfully!")

        return JsonResponse({"message": "Students successfully added!", "status":"success"})

    return JsonResponse({"error": "Invalid request"}, status=400)


def envelope_view(request):
    content = {'exclude_layout': True, }
    return render(request, 'myapp/envelope.html',content)


