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
        with self.assertRaises(ValidationError) as context:
            message.full_clean()  # This triggers model validation, including file size check
        
        # If the above does not raise an error, we will reach this point
        # Check that the raised error contains the correct message
        self.assertIn('File size cannot exceed 1 MB.', str(context.exception))