import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main')))
from string_operations import reverse_string, capitalize_string, count_vowels

def test_reverse_string():
    assert reverse_string("hello") == "olleh"

def test_capitalize_string():
    assert capitalize_string("hello") == "Hello"

def test_count_vowels():
    assert count_vowels("hello") == 2
