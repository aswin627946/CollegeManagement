from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Message

class MessageModelTest(TestCase):
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