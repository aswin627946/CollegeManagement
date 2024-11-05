from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Message,StudentInfo,FeeDefaulters
from django.urls import reverse
from rest_framework import status

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
