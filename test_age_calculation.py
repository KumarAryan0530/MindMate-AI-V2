"""
Test script to verify age calculation from date of birth
Run with: E:/all-projects/SafeMind-AI/venv/Scripts/python.exe manage.py shell < test_age_calculation.py
"""

from accounts.models import Profile
from datetime import date
from django.contrib.auth.models import User

print("=== Testing Age Calculation ===\n")

# Get or create a test user
user, created = User.objects.get_or_create(username='test_age_user', defaults={'email': 'test@example.com'})
print(f"User: {user.username}")

# Get or create profile
profile, created = Profile.objects.get_or_create(user=user)

# Test Case 1: Born in 2000
profile.date_of_birth = date(2000, 1, 1)
profile.save()
print(f"\nTest 1:")
print(f"  Date of Birth: {profile.date_of_birth}")
print(f"  Calculated Age: {profile.age} years")
print(f"  Expected: 25 years")

# Test Case 2: Born in 1995
profile.date_of_birth = date(1995, 6, 15)
profile.save()
print(f"\nTest 2:")
print(f"  Date of Birth: {profile.date_of_birth}")
print(f"  Calculated Age: {profile.age} years")
print(f"  Expected: 30 years")

# Test Case 3: Born in 2002, birthday not yet passed this year
profile.date_of_birth = date(2002, 12, 1)
profile.save()
print(f"\nTest 3:")
print(f"  Date of Birth: {profile.date_of_birth}")
print(f"  Calculated Age: {profile.age} years")
print(f"  Expected: 22 years (birthday passed)")

# Test Case 4: No date of birth
profile.date_of_birth = None
profile.save()
print(f"\nTest 4:")
print(f"  Date of Birth: {profile.date_of_birth}")
print(f"  Calculated Age: {profile.age}")
print(f"  Expected: None")

print("\n=== Test Complete ===")
