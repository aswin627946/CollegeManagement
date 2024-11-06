from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from datetime import datetime
from rest_framework.test import APIClient
from myapp.models import *


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
            print("test_add_timetable_missing_semester_field: PASSED")
        except AssertionError:
            print("test_add_timetable_missing_semester_field: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_timetable_missing_day_field(self): #TC4
        data = self.data.copy()
        data['semester']=3
        data['department']='CSE'
        data['day']=''
        
        response = self.client.post(self.url, data, format='json')
        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print("test_add_timetable_missing_semester_field: PASSED")
        except AssertionError:
            print("test_add_timetable_missing_semester_field: FAILED")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)