from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# from django.contrib.auth.models import AbstractUser
# # Create your models here.

# class User(AbstractUser):
#     email = models.EmailField(unique=True)
    
#     def ___str___(self):
#         return self.email

from django.core.exceptions import ValidationError
def validate_file_size(file):
    max_size_mb = 1  # Set maximum file size to 1 MB
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError("File size cannot exceed 1 MB.")

class StudentInfo(models.Model):
    roll_no = models.CharField(max_length=255,primary_key=True)
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    joining_year = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=255)
    semester = models.IntegerField()
    contact_number = models.CharField(max_length=255)
    address = models.TextField()
    gender = models.CharField(max_length=255)
    email = models.EmailField()

    def  __str__(self):
        return self.roll_no

class FacultyInfo(models.Model):
    faculty_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)#associate
    designation = models.CharField(max_length=255) #hod
    email = models.EmailField()
    description = models.TextField()

    def  __str__(self):
        return self.name

class AdministrationInfo(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    email = models.EmailField()
    staff_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class CurrentCourses(models.Model):
    course_code = models.CharField(max_length=255)
    total_classes = models.IntegerField()
    faculty_name = models.CharField(max_length=255)
    semester = models.IntegerField()
    department = models.CharField(max_length=255,default='none')


    def __str__(self):
        return self.course_code+' '+self.faculty_name

class CourseList(models.Model):
    course_code = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)
    semester = models.IntegerField()
    department = models.CharField(max_length=255)
    course_type=models.CharField(max_length=255,default="",null=True)
    
    def __str__(self):
        return self.course_code+' '+self.course_name
    
class Result(models.Model):
    course_code = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255)
    ct_1 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    ct_2 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    assignments = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    end_sem = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    grade = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=255)

    def __str__(self):
        return self.course_code+' '+self.roll_no

class ClassInfo(models.Model):
    batch = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    class_coordinator = models.CharField(max_length=255)
    class_representative = models.CharField(max_length=255)

    def __str__(self):
        return self.batch+' '+self.department
    
class FeeDefaulters(models.Model):
    department = models.CharField(max_length=255)
    batch = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=255)

    def __str__(self):
        return self.department+' '+self.batch
    

class Absentees(models.Model):
    course_code = models.CharField(max_length=255)
    date = models.DateField()
    roll_no = models.CharField(max_length=255)
    time_slot = models.CharField(max_length=255)

    def __str__(self):
        return  str(self.date) + " "+self.roll_no+" "+self.course_code

class Todolist(models.Model):
    roll_no = models.CharField(max_length=255)
    task = models.CharField(max_length=255)
    id=models.CharField(max_length=100,primary_key=True)
    is_completed=models.BooleanField(default=False)
    
    

    def __str__(self):
        return self.roll_no+' '+self.task
    
class Login(models.Model):
    email = models.EmailField()
    type_of_user = models.CharField(max_length=255)

    def __str__(self):
        return self.email


class TimeTable(models.Model):
    
    semester = models.IntegerField(default=None)
    department = models.CharField(max_length=255,default=None)
    day = models.CharField(max_length=10,default=None)
    slot_1 = models.CharField(max_length=5, blank=True, null=True,default=None)
    slot_2 = models.CharField(max_length=5, blank=True, null=True,default=None)
    slot_3 = models.CharField(max_length=5, blank=True, null=True,default=None)
    slot_4 = models.CharField(max_length=5, blank=True, null=True,default=None)
    slot_5 = models.CharField(max_length=5, blank=True, null=True,default=None)
    slot_6 = models.CharField(max_length=5, blank=True, null=True,default=None)
    slot_7 = models.CharField(max_length=5, blank=True, null=True,default=None)
    # date_created = models.DateTimeField(default=timezone.now)
    # date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'sem'+str(self.semester) + ' ' + self.department + ' '+self.day
    

class WeeklyTimeTable(models.Model) :
    semester = models.IntegerField()
    department = models.CharField(max_length=255)
    day = models.CharField(max_length=10)
    slot_1 = models.CharField(max_length=5, blank=True, null=True)
    slot_2 = models.CharField(max_length=5, blank=True, null=True)
    slot_3 = models.CharField(max_length=5, blank=True, null=True)
    slot_4 = models.CharField(max_length=5, blank=True, null=True)
    slot_5 = models.CharField(max_length=5, blank=True, null=True)
    slot_6 = models.CharField(max_length=5, blank=True, null=True)
    slot_7 = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return 'sem'+str(self.semester) + ' ' + self.department + ' '+self.day
    


class Message(models.Model):
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    message_type = models.TextField()
    status = models.BooleanField(default=False)
    file = models.FileField(upload_to='uploaded_files/', blank=True, null=True, validators=[validate_file_size])

    def __str__(self):
        return f'{self.sender} to {self.recipient}: {self.message_type}'
    


class FacultyTimeTable(models.Model):
    name = models.CharField(max_length=255)
    day = models.CharField(max_length=10)
    slot_1 = models.CharField(max_length=5, blank=True, null=True)
    slot_2 = models.CharField(max_length=5, blank=True, null=True)
    slot_3 = models.CharField(max_length=5, blank=True, null=True)
    slot_4 = models.CharField(max_length=5, blank=True, null=True)
    slot_5 = models.CharField(max_length=5, blank=True, null=True)
    slot_6 = models.CharField(max_length=5, blank=True, null=True)
    slot_7 = models.CharField(max_length=5, blank=True, null=True) 
    def __str__(self):
        return str(self.name) + ' '+self.day
    

class LabResult(models.Model) :
    course_code=models.CharField(max_length=250)
    faculty=models.CharField(max_length=140)
    internal_marks=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(40)])
    end_lab=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(40)])
    roll_no=models.CharField(max_length=50)
    grade=models.CharField(max_length=150)

    def __str__(self):
        return self.course_code+' '+self.roll_no