import random
from django.core.management.base import BaseCommand
from faker import Faker
from myapp.models import Student, Subject  # Adjust based on your app name

fake = Faker()

class Command(BaseCommand):
    help = "Generate fake students"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="Number of students to create")

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        subjects = list(Subject.objects.all())

        if not subjects:
            self.stdout.write(self.style.ERROR("No subjects found. Add subjects first."))
            return

        for _ in range(count):
            student = Student.objects.create(
                username=fake.user_name(),
                student_id=fake.unique.numerify("STU####"),
                full_name=fake.name(),
                course=fake.word().capitalize(),
                year_section=f"{random.randint(1, 4)}-{random.choice(['A', 'B', 'C'])}",
                email=fake.unique.email(),
                password=fake.password(),
            )
            student.subjects.set(random.sample(subjects, random.randint(1, 3)))  # Assign random subjects
            student.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} students!"))
