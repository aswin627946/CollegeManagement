from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Absentees, CurrentCourses
from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Login
from .models import Todolist

class InsertAttendanceTestCase(TestCase):
    def setUp(self):
        # Set up initial data for tests
        self.client = APIClient()
        self.course_code = "CS101"
        self.date = str(date.today())
        self.time_slot = "10:00-12:00"
        self.department = "Computer Science"
        
        # Create a course for the department
        self.course = CurrentCourses.objects.create(
            course_code=self.course_code,
            total_classes=0,
            faculty_name="Dr. Smith",
            semester=1,
            department=self.department
        )
        
        self.url = reverse('insertAttendance')  # Adjust the URL name if needed
        self.absentees_list = ["A001", "A002", "A003"]

    def test_insert_new_attendance(self):
        # Test normal attendance insertion
        # Test case for inserting new data and then checking for total classes count and len of absentees list
        data = {
            "date": self.date,
            "course_id": self.course_code,
            "absentees_list": self.absentees_list,
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 0
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course = CurrentCourses.objects.get(course_code=self.course_code)
        self.assertEqual(course.total_classes, 1)
        absentees = Absentees.objects.filter(course_code=self.course_code, date=self.date, time_slot=self.time_slot)
        self.assertEqual(len(absentees), len(self.absentees_list))

    def test_update_existing_attendance(self):
        # Test updating attendance with new absentees list
        Absentees.objects.create(course_code=self.course_code, date=self.date, roll_no="A001", time_slot=self.time_slot)
        updated_absentees_list = ["A001", "A002"]
        data = {
            "date": self.date,
            "course_id": self.course_code,
            "absentees_list": updated_absentees_list,
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        absentees = Absentees.objects.filter(course_code=self.course_code, date=self.date, time_slot=self.time_slot)
        self.assertEqual(len(absentees), len(updated_absentees_list))

    def test_no_duplicate_attendance(self):
        # Test prevention of duplicate attendance entries
        data = {
            "date": self.date,
            "course_id": self.course_code,
            "absentees_list": self.absentees_list,
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 1
        }
        self.client.post(self.url, data, format='json')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        absentees = Absentees.objects.filter(course_code=self.course_code, date=self.date, time_slot=self.time_slot)
        self.assertEqual(len(absentees), len(self.absentees_list))

    def test_empty_absentees_list(self):
        # Test with an empty absentees list
        data = {
            "date": self.date,
            "course_id": self.course_code,
            "absentees_list": [],
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 0
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        absentees = Absentees.objects.filter(course_code=self.course_code, date=self.date, time_slot=self.time_slot)
        self.assertEqual(len(absentees), 0)


    def test_invalid_course_id(self):
        # Test with a course_id that does not exist
        data = {
            "date": self.date,
            "course_id": "INVALID_CODE",
            "absentees_list": self.absentees_list,
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 0
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_absentees_list_not_modified_on_same_input(self):
        # Test that absentees list remains the same if the input hasn't changed
        Absentees.objects.create(course_code=self.course_code, date=self.date, roll_no="A001", time_slot=self.time_slot)
        data = {
            "date": self.date,
            "course_id": self.course_code,
            "absentees_list": ["A001"],
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 1
        }
        response = self.client.post(self.url, data, format='json')
        absentees = Absentees.objects.filter(course_code=self.course_code, date=self.date, time_slot=self.time_slot)
        self.assertEqual(len(absentees), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_date_format(self):
        # Test with an invalid date format
        data = {
            "date": "invalid-date",
            "course_id": self.course_code,
            "absentees_list": self.absentees_list,
            "time_slot": self.time_slot,
            "department": self.department,
            "count": 0
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_invalid_time_slot_format(self):
        data = {
            "date": self.date,
            "course_id": self.course_code,
            "absentees_list": self.absentees_list,
            "time_slot": "invalid-time-slot",  # Invalid format
            "department": self.department,
            "count": 0
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthTests(TestCase):

    def setUp(self):
        # Setup test client and create a sample user
        self.client = APIClient()
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.login_url = reverse('loginUser')  # Use the name of the URL if defined
        self.logout_url = reverse('logoutUser')

    def test_login_success(self):
        # Test login with correct credentials
        response = self.client.post(self.login_url, {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])

    def test_login_failure_wrong_username(self):
        # Test login with incorrect credentials
        response = self.client.post(self.login_url, {'username': 'harsha', 'password': self.password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['authenticated'])

    def test_login_failure_wrong_password(self):
        # Test login with incorrect credentials
        response = self.client.post(self.login_url, {'username': self.username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['authenticated'])

    def test_login_missing_fields_password(self):
        # Test login with missing fields
        response = self.client.post(self.login_url, {'username': self.username})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields_username(self):
        # Test login with missing fields
        response = self.client.post(self.login_url, {'password': self.password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        # First, login to ensure a session is created
        self.client.login(username=self.username, password=self.password)
        
        # Then, test logout functionality
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['authenticated'])


class TodolistTests(TestCase):

    def setUp(self):
        # Initialize the test client and create sample data for testing
        self.client = APIClient()
        self.roll_no = "12345"
        self.task1 = "Complete assignment"
        self.task2 = "Prepare for exam"
        
        # Create Todolist objects for the user
        self.todo1 = Todolist.objects.create(roll_no=self.roll_no, task=self.task1, id="1", is_completed=False)
        self.todo2 = Todolist.objects.create(roll_no=self.roll_no, task=self.task2, id="2", is_completed=True)
        
        # URL for the API endpoint
        self.url = reverse('getTodosForUser')  # Use the name of the URL if defined in urls.py

    def test_get_todos_for_user_success(self):
        # Test retrieving todos for a specific roll number
        response = self.client.get(self.url, {'roll_no': self.roll_no})
        
        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['todos_details']), 2)
        
        # Check the contents of the todos
        todos_data = response.data['todos_details']
        self.assertEqual(todos_data[0]['roll_no'], self.roll_no)
        self.assertEqual(todos_data[0]['task'], self.task1)
        self.assertEqual(todos_data[0]['is_completed'], False)
        self.assertEqual(todos_data[1]['task'], self.task2)
        self.assertEqual(todos_data[1]['is_completed'], True)

    def test_get_todos_for_user_no_todos(self):
        # Test retrieving todos for a roll number with no todos
        response = self.client.get(self.url, {'roll_no': 'nonexistent_roll_no'})
        
        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['todos_details']), 0)

    def test_get_todos_for_user_missing_roll_no(self):
        # Test retrieving todos with no roll number provided
        response = self.client.get(self.url)
        
        # Verify the response (could be handled with a 400 if validation is added)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['todos_details']), 0)

