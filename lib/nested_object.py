# lib/nested_object.py

from datetime import datetime
from marshmallow import Schema, fields
from pprint import pprint

# models

class Patient:
    def __init__(self, name, email, dob):
        self.name = name
        self.email = email
        self.dob = dob

class Appointment:
    def __init__(self, patient, appointment_datetime) :
        self.patient = patient
        self.appointment_datetime = appointment_datetime

# schemas


# model instances
patient_1 = Patient(name="Lua", email="lua@email.com", dob=datetime(2001,5,31))
patient_2 = Patient(name="Kalani", email="kalani@email.com", dob=datetime(1980,10,2))

appointment_1 = Appointment(patient=patient_1, appointment_datetime = datetime(2023,2,28,18,50))
appointment_2 = Appointment(patient=patient_2, appointment_datetime = datetime(2023,9,30,8,45))
appointment_3 = Appointment(patient=patient_1, appointment_datetime = datetime(2023,10,31,8,30))
appointment_data = [appointment_1, appointment_2, appointment_3]

# serialize nested object
