from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Message

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

         # Try to save the message instance and expect a validation error for file size
        with self.assertRaises(ValidationError):
            message.full_clean()  # This triggers model validation, including file size check