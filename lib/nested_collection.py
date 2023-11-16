# lib/nested_collection.py

from marshmallow import Schema, fields
from pprint import pprint

# models

class Specialty:
    def __init__(self, code, description):
        self.code = code
        self.description = description
       
class Doctor:
    def __init__(self, name, email, specialties):
        self.name = name
        self.email = email
        self.specialties = specialties

# schemas


# model instances

specialty_1 = Specialty(code = "fm", description="Family Medicine")
specialty_2 = Specialty(code="ped", description = "Pediatrics")
specialty_3 = Specialty(code="er", description = "Emergency Medicine")
doctor_1 = Doctor(name="Dr. Bones", email="bones@email.com", specialties = [specialty_1, specialty_2])
doctor_2 = Doctor(name="Dr. Brains", email="brains@email.com", specialties = [specialty_3])
  
# serialize nested list of objects
