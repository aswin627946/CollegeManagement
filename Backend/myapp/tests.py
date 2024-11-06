from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from datetime import datetime
from rest_framework.test import APIClient
from myapp.models import *
from datetime import date
from django.contrib.auth.models import User
from .models import Login
from .models import Todolist

class TestMessageModel(TestCase):
    def test_file_size_limit(self):
        # Create a file over 1 MB for testing
        large_file_content = b'a' * (1024 * 1024 + 1)  # 1 MB + 1 byte
        large_file = SimpleUploadedFile('large_test_file.pdf', large_file_content, content_type='application/pdf')
        
        # Try to create a Message instance with this large file
        message = Message(
            sender='student@example.com',
            recipient='admin',
            message_type='Request for fee receipt',
            file=large_file
        )

        # Expect the validation to raise an error if size limit is implemented
        try:
            message.full_clean()  # This triggers model validation, including file size check
            message.save()
            # If no exception is raised, the test should fail because the limit wasn't enforced
            self.fail("Test failed: The file size limit is not implemented, and file larger than 1 MB was accepted.")
        except ValidationError as e:
            # If ValidationError is raised, it means file size limit check is in place
            self.assertIn('File size cannot exceed 1 MB.', str(e))
            print("Test case passed: the file size constraint is implemented.")


    def test_file_upload_pdf_validation(self):
        # Create a valid PDF file
        valid_pdf = SimpleUploadedFile("valid_file.pdf", b"PDF content", content_type='application/pdf')
        message = Message(sender='student@example.com', recipient='admin', message_type='Request for fee receipt', file=valid_pdf)
        message.full_clean()  # Should not raise ValidationError

        # Create an invalid file (not a PDF)
        invalid_file = SimpleUploadedFile("invalid_file.txt", b"Not a PDF content", content_type='text/plain')
        message_invalid = Message(sender='student@example.com', recipient='admin', message_type='Request for fee receipt', file=invalid_file)
        
        with self.assertRaises(ValidationError,msg=f"Test case failed : Validation error not raised for non pdf file"):
            message_invalid.full_clean()  # Should raise ValidationError

        print("Test cases passed: ValidationError raised for invalid file type")

class TestGetEachClassStudentsList(TestCase):
    def setUp(self):
        # Create test data
        StudentInfo.objects.create(
            roll_no='CS101',
            name='John Doe',
            department='cse',
            joining_year='2023',
            blood_group='O+',
            semester=1,
            contact_number='1234567890',
            address='123 Street Name',
            gender='Male',
            email='john@example.com'
        )
        StudentInfo.objects.create(
            roll_no='CS102',
            name='Jane Smith',
            department='cse',
            joining_year='2023',
            blood_group='A+',
            semester=1,
            contact_number='0987654321',
            address='456 Another St',
            gender='Female',
            email='jane@example.com'
        )

    def test_get_each_class_students_list_with_department_mapping(self):
        # Call the view with the department name that should map to 'cse'
        response = self.client.get(reverse('getEachClassStudentsList'), 
                                    {'department': 'Computer Science and Engineering', 
                                     'joiningYear': '2023'})
        
        # Check that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extract the student list from the response
        student_list = response.data.get('student_list', [])

        # Assert that the student list is not empty
        self.assertGreater(len(student_list), 0, "The student list is empty. Test failed.")

        # If the student list is not empty, print a success message
        print("The student list is not empty. Test passed.")

class TestFeeDefaultersModel(TestCase):
    def test_batch_validation(self):
        # Define a list of invalid batch inputs
        invalid_batches = [
            '12345678',    # No hyphen
            '1234-567',    # Not enough digits after hyphen
            '1234-56789',  # Too many digits after hyphen
            '12-34567',    # Too few digits before hyphen
            '1234-12ab',   # Non-numeric characters
            '1234-12345'   # More than 9 characters
        ]

        for batch in invalid_batches:
            with self.assertRaises(ValidationError, msg=f"Test failed : Validation error not raised for batch: {batch}"):
                fee_defaulter = FeeDefaulters(department='cse', batch=batch, roll_no='221111')
                fee_defaulter.full_clean()  # This will trigger validation

        print("Test Passed: All invalid batch inputs raised a ValidationError as expected.")

class TestStudentInfoModel(TestCase):
    def test_semester_validation(self):
        # Try creating a StudentInfo instance with invalid semester values
        invalid_semesters = [0, 9, -1, 10]

        for semester in invalid_semesters:
            student = StudentInfo(
                roll_no="S12345", 
                name="Test Student", 
                department="cse", 
                joining_year="2024", 
                blood_group="O+", 
                semester=semester,  # Invalid semester
                contact_number="1234567890", 
                address="Test Address", 
                gender="M", 
                email="teststudent@example.com"
            )

            # Check if the ValidationError is raised
            with self.assertRaises(ValidationError,msg=f"Test case failed : Validation error not raised for semester: {semester}"):
                student.full_clean()  # This will trigger the model validation

        # If no validation error is raised for invalid semester, the test case will fail
        print("Test case passed: ValidationError raised for invalid semester.")

    
    def test_contact_number_validation(self):
        # Try creating StudentInfo instances with invalid contact numbers
        invalid_contact_numbers = ["123456789", "12345678901", "12345abcde", "abcdefghij"]
        for contact_number in invalid_contact_numbers:
            student = StudentInfo(
                roll_no="S12345", 
                name="Test Student", 
                department="cse", 
                joining_year="2024", 
                blood_group="O+", 
                semester=3, 
                contact_number=contact_number,  # Invalid contact number
                address="Test Address", 
                gender="M", 
                email="teststudent@example.com"
            )

            # Check if the ValidationError is raised
            with self.assertRaises(ValidationError,msg=f"Test case failed : Validation error not raised for contact number: {contact_number}"):
                student.full_clean()  # This will trigger the model validation

        # If validation errors are raised for all invalid numbers, the test passes
        print("Test case passed: ValidationError raised for invalid contact numbers.")


    def test_joining_year_validation(self):
        # Test cases with invalid joining years
        invalid_years = ['2025', '20xx', '123', '202', '20223', 'abcd']
        
        for year in invalid_years:
            student = StudentInfo(
                roll_no='123456',
                name='John Doe',
                department='cse',
                joining_year=year,  # Invalid year
                blood_group='O+',
                semester=1,
                contact_number='1234567890',
                address='123 Street',
                gender='Male',
                email='john.doe@example.com'
            )
            with self.assertRaises(ValidationError,msg=f"Test case failed : Validation error not raised for joining year: {year}"):
                student.full_clean()  # This will trigger the model validation
        
        # If validation errors are raised for all invalid joining years, the test passes
        print("Test case passed: ValidationError raised for invalid joining years.")

class TimetableAPICallTestCase(TestCase): # TC1
    def setUp(self):
        self.client = APIClient()
        self.semester = '3'
        self.department = 'cse'

    def test_view_status_code(self):
        status_code=None

        try:
            url = reverse('getTimetableForStudent')
            response = self.client.get(url, {'semester': self.semester, 'department': self.department})
            status_code=response.status_code
            self.assertEqual(status_code, status.HTTP_200_OK)
            print("test_view_status_code: PASSED")
        except Exception as e:
            print("test_view_status_code: FAILED")
            self.assertEqual(status_code, status.HTTP_200_OK)


class TimetableTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('addTimetable')
        # self.url = reverse('addTimetableforFail')
        
        self.data = {
            'semester': 3,
            'department': 'CSE',
            'day': 'friday',
            'slot_1': 'cs101',
            'slot_2': 'cs102',
            'slot_3': 'cs103',
            'slot_4': 'cs104',
            'slot_5': 'cs201',
            'slot_6': 'cs202',
            'slot_7': 'cs203'
        }
        
        TimeTable.objects.create(
            semester=self.data['semester'],
            department=self.data['department'],
            day=self.data['day'],
            slot_1=self.data['slot_1'],
            slot_2=self.data['slot_2'],
            slot_3=self.data['slot_3'],
            slot_4=self.data['slot_4'],
            slot_5=self.data['slot_5'],
            slot_6=self.data['slot_6'],
            slot_7=self.data['slot_7']
        )

    def test_add_timetable_missing_semester_field(self): #TC4
        data = self.data.copy()
        data['semester']=0
        
        response = self.client.post(self.url, data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_add_timetable_missing_semester_field: PASSED")
        except AssertionError:
            print("test_add_timetable_missing_semester_field: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_timetable_missing_department_field(self): #TC4
        data = self.data.copy()
        data['semester']=3
        data['department']=''
        
        response = self.client.post(self.url, data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_add_timetable_missing_department_field: PASSED")
        except AssertionError:
            print("test_add_timetable_missing_department_field: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_timetable_missing_day_field(self): #TC4
        data = self.data.copy()
        data['semester']=3
        data['department']='CSE'
        data['day']=''
        
        response = self.client.post(self.url, data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_add_timetable_missing_day_field: PASSED")
        except AssertionError:
            print("test_add_timetable_missing_day_field: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_timetable_invalid_semester_data(self):
        data = self.data.copy()
        data['semester'] = 9

        response = self.client.post(self.url, data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_add_timetable_invalid_semester_data: PASSED")
        except AssertionError:
            print("test_add_timetable_invalid_semester_data: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_timetable_invalid_department_data(self):
        data = self.data.copy()
        data['semester'] = 3
        data['department'] = 'EEE'

        response = self.client.post(self.url, data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_add_timetable_invalid_department_data: PASSED")
        except AssertionError:
            print("test_add_timetable_invalid_department_data: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_duplicate_timetable_entry(self): #TC2
        response = self.client.post(self.url, self.data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_donot_add_duplicate_timetable_entry: PASSED")
        except AssertionError:
            print("test_donot_add_duplicate_timetable_entry: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

class DataFetcher(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('search')
        StudentInfo.objects.create(name="Alice Johnson", roll_no="2022001", department="CSE", semester=3, joining_year=2021, email="alice@example.com")
        FacultyInfo.objects.create(name="Dr. Bob Miller", faculty_id="F002", position="Professor", description="Physics faculty", designation="Professor", email="bob.miller@example.com")
        AdministrationInfo.objects.create(name="Charlie Brown", position="Principal", staff_id="A003", email="charlie.brown@example.com")

    def test_search_with_valid_query(self):
        response = self.client.get(self.url, {'searchText': 'Alice'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_list', response.data)
        self.assertEqual(len(response.data['search_list']), 1)
        self.assertEqual(response.data['search_list'][0]['name'], "Alice Johnson")
        print("test_search_with_valid_query: PASSED")
    
    def test_search_query_too_short(self):
        response = self.client.get(self.url, {'searchText': 'Ali'})
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_search_query_too_short: PASSED")
        except AssertionError:
            print("test_search_query_too_short: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_no_results(self):
        response = self.client.get(self.url, {'searchText': 'Snigdha'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        try:
            self.assertEqual(len(response.data['search_list']), 0)
            print("test_search_no_results: PASSED")
        except AssertionError:
            print("test_search_no_results: FAILED")
            self.assertEqual(len(response.data['search_list']), 0)

    def test_search_case_insensitivity(self):
        response = self.client.get(self.url, {'searchText': 'alice'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_list', response.data)
        try:
            self.assertEqual(len(response.data['search_list']), 1)
            try:
                self.assertEqual(response.data['search_list'][0]['name'], "Alice Johnson")
                print("test_search_case_insensitivity: PASSED")
            except AssertionError:
                print("test_search_case_insensitivity: FAILED")
                self.assertEqual(response.data['search_list'][0]['name'], "Alice Johnson")
        except AssertionError:
            print("test_search_case_insensitivity: FAILED")
            self.assertEqual(len(response.data['search_list']), 1)

    def test_search_multiple_results(self): 
        # Create an additional student with a name containing "Bob"
        StudentInfo.objects.create(name="Bob Miles", roll_no="2022002", department="ECE", semester=2, joining_year=2020, email="bob.roberts@example.com")
        response = self.client.get(self.url, {'searchText': 'Bob M'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_list', response.data)
        try:
            self.assertEqual(len(response.data['search_list']), 2)
            # Check if the names returned are correct
            names = [result['name'] for result in response.data['search_list']]
            try:
                self.assertIn("Dr. Bob Miller", names)
                try:
                    self.assertIn("Bob Miles", names)
                    print("test_search_multiple_results: PASSED")
                except AssertionError:
                    print("test_search_multiple_results: FAILED")
                    self.assertIn("Bob Miles", names)
            except AssertionError:
                print("test_search_multiple_results: FAILED")
                self.assertIn("Dr. Bob Miller", names)
        except AssertionError:
            print("test_search_multiple_results: FAILED")
            self.assertEqual(len(response.data['search_list']), 2)

    def test_search_missing_query(self):
        response = self.client.get(self.url)
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_search_missing_query: PASSED")
        except AssertionError:
            print("test_search_missing_query: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    


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
        response = self.client.post(self.login_url, {'username': 'asdfasdf', 'password': self.password})
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

