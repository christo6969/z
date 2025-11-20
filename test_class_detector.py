"""
Unit tests for ClassDetector module
"""

import unittest
from class_detector import ClassDetector


class TestClassDetector(unittest.TestCase):
    """Test cases for ClassDetector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = ClassDetector()
    
    def test_detect_valid_classes(self):
        """Test detection of valid class formats"""
        text = "Students from 1AA and 2BC should attend the meeting"
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, {'1AA', '2BC'})
    
    def test_detect_single_class(self):
        """Test detection of single class"""
        text = "Class 3XY has the exam tomorrow"
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, {'3XY'})
    
    def test_detect_no_classes(self):
        """Test when no classes are present"""
        text = "This is a general announcement"
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, set())
    
    def test_detect_invalid_formats(self):
        """Test that invalid formats are not detected"""
        # Invalid: wrong number
        text1 = "Class 6AA is invalid"
        classes1 = self.detector.detect_classes_in_text(text1)
        self.assertEqual(classes1, set())
        
        # Invalid: only one letter
        text2 = "Class 1A is invalid"
        classes2 = self.detector.detect_classes_in_text(text2)
        self.assertEqual(classes2, set())
        
        # Invalid: three letters
        text3 = "Class 1AAA is invalid"
        classes3 = self.detector.detect_classes_in_text(text3)
        self.assertEqual(classes3, set())
        
        # Invalid: lowercase
        text4 = "Class 1aa is invalid"
        classes4 = self.detector.detect_classes_in_text(text4)
        self.assertEqual(classes4, set())
    
    def test_detect_all_valid_numbers(self):
        """Test all valid class numbers 1-5"""
        text = "Classes 1AA, 2BB, 3CC, 4DD, 5EE are all valid"
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, {'1AA', '2BB', '3CC', '4DD', '5EE'})
    
    def test_detect_duplicates(self):
        """Test that duplicates are removed"""
        text = "Class 1AA and 1AA and 1AA again"
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, {'1AA'})
        self.assertEqual(len(classes), 1)
    
    def test_detect_mixed_content(self):
        """Test detection in mixed content"""
        text = """
        Important notice for all students:
        - Class 1AA: Meeting at 9:00
        - Class 2BC: Meeting at 10:00
        - Class 5ZZ: Meeting at 11:00
        Please attend on time.
        Contact: 123-456-7890
        """
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, {'1AA', '2BC', '5ZZ'})
    
    def test_format_classes_output(self):
        """Test formatting of detected classes"""
        classes = {'1AA', '2BC', '3XY'}
        output = self.detector.format_classes_output(classes)
        self.assertIn('1AA', output)
        self.assertIn('2BC', output)
        self.assertIn('3XY', output)
        self.assertIn('📚', output)
    
    def test_format_empty_classes(self):
        """Test formatting with no classes"""
        classes = set()
        output = self.detector.format_classes_output(classes)
        self.assertEqual(output, "")
    
    def test_empty_text(self):
        """Test with empty or None text"""
        classes1 = self.detector.detect_classes_in_text("")
        self.assertEqual(classes1, set())
        
        classes2 = self.detector.detect_classes_in_text(None)
        self.assertEqual(classes2, set())
    
    def test_word_boundaries(self):
        """Test that pattern respects word boundaries"""
        # Should not match partial matches
        text = "A1AA should not match, but 1AA should"
        classes = self.detector.detect_classes_in_text(text)
        self.assertEqual(classes, {'1AA'})


if __name__ == '__main__':
    unittest.main()
