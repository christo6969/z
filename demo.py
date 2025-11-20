#!/usr/bin/env python3
"""
Demo script for ClasseViva Monitor Bot
Demonstrates class detection functionality
"""

from class_detector import detect_classes

def main():
    print("=" * 60)
    print("ClasseViva Monitor - Class Detection Demo")
    print("=" * 60)
    print()
    
    # Test 1: Simple text detection
    print("Test 1: Simple text detection")
    print("-" * 60)
    text1 = "Students from class 1AA and 2BC should attend the meeting"
    print(f"Input: {text1}")
    result1 = detect_classes(text=text1)
    print(f"Output: {result1}")
    print()
    
    # Test 2: Multiple classes
    print("Test 2: Multiple classes in communication")
    print("-" * 60)
    text2 = """
    Important Notice:
    - Class 3XY: Exam on Monday
    - Class 4AB: Exam on Tuesday
    - Class 5ZZ: Exam on Wednesday
    """
    print(f"Input: {text2}")
    result2 = detect_classes(text=text2)
    print(f"Output: {result2}")
    print()
    
    # Test 3: Duplicates are removed
    print("Test 3: Duplicate detection (should show unique classes)")
    print("-" * 60)
    text3 = "Class 1AA has a meeting. Students from 1AA should attend. 1AA is important."
    print(f"Input: {text3}")
    result3 = detect_classes(text=text3)
    print(f"Output: {result3}")
    print()
    
    # Test 4: Invalid formats
    print("Test 4: Invalid formats (should not detect)")
    print("-" * 60)
    text4 = "Class 6AA (invalid), class 1A (invalid), class 1AAA (invalid)"
    print(f"Input: {text4}")
    result4 = detect_classes(text=text4)
    print(f"Output: {result4 if result4 else '(No classes detected)'}")
    print()
    
    # Test 5: Mixed valid and invalid
    print("Test 5: Mixed valid and invalid formats")
    print("-" * 60)
    text5 = "Classes: 1AA (valid), 6BB (invalid), 2CD (valid), 3E (invalid)"
    print(f"Input: {text5}")
    result5 = detect_classes(text=text5)
    print(f"Output: {result5}")
    print()
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
