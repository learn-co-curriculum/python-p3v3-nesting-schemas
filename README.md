# Nesting Schemas : Code-Along

## Learning Goals

- Implement nested schemas
- Avoid infinite recursion during two-way nesting

---

## Key Vocab

- **Serialization**: a process to convert programmatic data such as a Python
  object to a sequence of bytes that can be shared with other programs,
  computers, or networks.
- **Deserialization**: the reverse process, converting input data back to
  programmatic data.
- **Nested schema**: A schema that represents a relationship between objects.

---

## Introduction

Schemas can be nested to represent relationships between objects (e.g. foreign
key relationships).

## Setup

This lesson is a code-along, so fork and clone the repo.

Run `pipenv install` to install the dependencies and `pipenv shell` to enter
your virtual environment before running your code.

```console
$ pipenv install
$ pipenv shell
```

---

## Nesting an object

Let's start with an object model representing a doctor's office that schedules
appointments with patients. A patient can schedule an appointment to visit the
doctor at a given date and time. We'll assume the following relationships hold:

- An appointment is related to one patient.
- A patient may be related to many appointments.

The file `lib/nested_object.py` contains the model classes `Patient` and
`Appointment` shown below. Notice each `Appointment` object is initialized with
a reference to one `Patient` object, along with the date and time.

```py
# lib/nested_object.py
# nested objects

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

```

It is easy to define a schema for the patient model, since the fields represent
primitive types. Add the following schema to `lib/nested_object.py`:

```py
# schemas

class PatientSchema(Schema):
    name = fields.String()
    email = fields.Email()
    dob = fields.Date()
```

The appointment schema must reflect the relationship with the patient. We can
use the `fields.Nested` type to reflect the relationship. Update the code to add
the `AppointmentSchema` class, which must be placed after `PatientSchema` due to
the nested reference:

```py
class AppointmentSchema(Schema):
    patient = fields.Nested(PatientSchema)
    appointment_datetime = fields.DateTime()
```

Now we can use an `AppointmentSchema` instance to serialize the list of
`Appointment` objects:

```py
# deserialize nested object

result = AppointmentSchema(many=True).dump(appointment_data)
pprint(result)
```

Running the code results in the serialized patient data nested within each
appointment:

```console
$ python lib/nested_object.py
[{'appointment_datetime': '2023-02-28T18:50:00',
  'patient': {'dob': '2001-05-31', 'email': 'lua@email.com', 'name': 'Lua'}},
 {'appointment_datetime': '2023-09-30T08:45:00',
  'patient': {'dob': '1980-10-02',
              'email': 'kalani@email.com',
              'name': 'Kalani'}},
 {'appointment_datetime': '2023-10-31T08:30:00',
  'patient': {'dob': '2001-05-31', 'email': 'lua@email.com', 'name': 'Lua'}}]
```

## Nested collection

The file `lib/nested_collection.py` defines an object model to represent doctors
and medical specialties. There is a relationship between `Doctor` and
`Specialty`:

- A doctor may specialize in one or more medical practices.

Each `Doctor` object will store a list of `Specialty` objects as part of their
state.

```py
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
```

Let's add a schema for the specialty, with fields for the code and description
as shown below:

```py
# schemas

class SpecialtySchema(Schema):
    code = fields.String()
    description = fields.String()
```

The doctor schema must reflect the relationship with the specialty. Since a
doctor may have many specialties, we need to indicate the field is a list of
nested specialties. Add the `DoctorSchema` class definition after the
`SpecialtySchema` due to the nested reference:

```py
class DoctorSchema(Schema):
    name = fields.String()
    email = fields.Email()
    specialties = fields.List(fields.Nested(SpecialtySchema))
```

Now we can use a `DoctorSchema` instance to serialize the `Doctor` classes
instances:

```py
# serialize nested list of objects

result = DoctorSchema(many=True).dump([doctor_1, doctor_2])
pprint(result)
```

Running the code results in the serialized specialty data nested within each
doctor:

```console
$ python lib/nested_collection.py
[{'email': 'bones@email.com',
  'name': 'Dr. Bones',
  'specialties': [{'code': 'fm', 'description': 'Family Medicine'},
                  {'code': 'ped', 'description': 'Pediatrics'}]},
 {'email': 'brains@email.com',
  'name': 'Dr. Brains',
  'specialties': [{'code': 'er', 'description': 'Emergency Medicine'}]}]
```

## Two-way nested and circular references

Let's look at an example that involves two-way nesting or circular references.

The file `lib/two_way_nesting.py` contains models for books and authors. For
simplicity we'll assume a book has one author, but an author may write many
books. Each `Book` object will store a reference to its `Author` instance.  
The `Author` class does not directly store a list of related books. However, it
provides the method `get_books()` to compute a list of books written by the
author.

`BookSchema` has a nested field to store `AuthorSchema`. Since `AuthorSchema`
does not have any nested fields, the initial schema model represents one-way
(i.e non-circular) nesting.

```py
# lib/two_way_nesting.py
# two-way nesting and circular references

from marshmallow import Schema, fields, pre_dump
from pprint import pprint

# models

class Author:

    all = []
    def __init__(self, name, email):
        self.name = name
        self.email = email
        type(self).all.append(self)

    def get_books(self):
        """Get list of books for this author"""
        return [book for book in Book.all if book.author is self]

class Book:

    all = []
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author
        type(self).all.append(self)


# schemas

class AuthorSchema(Schema):
    name = fields.Str()
    email = fields.Email()

class BookSchema(Schema):
    isbn = fields.Str()
    title = fields.Str()
    author = fields.Nested(AuthorSchema())

# model instances

author_1 = Author(name="William Faulkner", email="will@email.com")
book_1 = Book(isbn="067973225X", title="As I Lay Dying", author=author_1)
book_2 = Book(isbn="0679732241", title="The Sound and the Fury", author=author_1)
author_2 = Author(name="Colson Whitehead", email="colson@email.com")
book_3 = Book(isbn="0385542364", title = "The Underground Railroad", author=author_2)

# serialize books
print("BOOKS")
book_result = BookSchema(many=True).dump([book_1, book_2, book_3])
pprint(book_result, indent=2)

# serialize authors
print("AUTHORS")
author_result = AuthorSchema(many=True).dump([author_1, author_2])
pprint(author_result)
```

Running the code shows that each serialized book contains nested author data.
However, notice the serialize author data does not nest any data about the books
the author wrote.

```console
BOOKS
[ { 'author': {'email': 'will@email.com', 'name': 'William Faulkner'},
    'isbn': '067973225X',
    'title': 'As I Lay Dying'},
  { 'author': {'email': 'will@email.com', 'name': 'William Faulkner'},
    'isbn': '0679732241',
    'title': 'The Sound and the Fury'},
  { 'author': {'email': 'colson@email.com', 'name': 'Colson Whitehead'},
    'isbn': '0385542364',
    'title': 'The Underground Railroad'}]
AUTHORS
[{'email': 'will@email.com', 'name': 'William Faulkner'},
 {'email': 'colson@email.com', 'name': 'Colson Whitehead'}]
```

But what if we would like to see book data included when we serialize an author?
We can achieve this by adding a nested field to `AuthorSchema`, along with a
`@pre_dump` method to compute the associated books prior to serialization.

This represents two-way nesting since each schema nests the other. Circular
relationships can cause issues with infinite recursion, but we'll see how to
avoid that.

As a first step, update `AuthorSchema` to add a nested field named `books` to
store the list of books.

- The field will be used only during serialization, so `dump_only=True` is set.
- There is an order-of-declaration issue since `AuthorSchema` and `BookSchema`
  both declare fields that reference each other. This issue can be avoided by
  passing a lambda expression.

You'll also need to add a pre-dump method to assign the `books` field by calling
the `get_books()` method.

```py
# schemas

class AuthorSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    # Pass a callable to avoid order-of-declaration issues.
    books = fields.List(fields.Nested(lambda: BookSchema(), dump_only=True))

    # Compute list of books for this author prior to serialization
    @pre_dump()
    def get_data(self, data, **kwargs):
        data.books =  data.get_books()
        return data
```

However, if you run the code right now you'll see an error message caused by
infinite recursion, since the author and book schemas both nest each other.

```console
$ python lib/two_way_nesting.py
...
RecursionError: maximum recursion depth exceeded in comparison
```

We can fix this by using `only` or `exclude` parameters to filter fields during
serialization.

- `AuthorSchema` should exclude data about the author in the nested books.
- `BookSchema` should exclude data about books in the nested author.

Update the code as shown below:

```py
# schemas

class AuthorSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    # Pass a callable to avoid order-of-declaration issues.
    # Use 'only' or 'exclude' to avoid infinite recursion.
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=("author",)), dump_only=True))

    # Compute list of books for this author prior to serialization
    @pre_dump()
    def get_data(self, data, **kwargs):
        data.books =  data.get_books()
        return data

class BookSchema(Schema):
    isbn = fields.Str()
    title = fields.Str()
    # Use 'only' or 'exclude' to avoid infinite recursion.
    author = fields.Nested(AuthorSchema(exclude=("books",)))
```

Now when you run the code, you should see each book containing filtered data
about the author, and each author containing filtered data about their books:

```console
BOOKS
[ { 'author': {'email': 'will@email.com', 'name': 'William Faulkner'},
    'isbn': '067973225X',
    'title': 'As I Lay Dying'},
  { 'author': {'email': 'will@email.com', 'name': 'William Faulkner'},
    'isbn': '0679732241',
    'title': 'The Sound and the Fury'},
  { 'author': {'email': 'colson@email.com', 'name': 'Colson Whitehead'},
    'isbn': '0385542364',
    'title': 'The Underground Railroad'}]
AUTHORS
[{'books': [{'isbn': '067973225X', 'title': 'As I Lay Dying'},
            {'isbn': '0679732241', 'title': 'The Sound and the Fury'}],
  'email': 'will@email.com',
  'name': 'William Faulkner'},
 {'books': [{'isbn': '0385542364', 'title': 'The Underground Railroad'}],
  'email': 'colson@email.com',
  'name': 'Colson Whitehead'}]
```

## Conclusion

Object relationships can be serialized by nesting a schema within another.
Issues that arise with circular references when two schemas nest each other can
be avoided through filtering.

## Solution Code

```py
# lib/nested_object.py
# nested objects

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

class PatientSchema(Schema):
    name = fields.String()
    email = fields.Email()
    dob = fields.Date()

class AppointmentSchema(Schema):
    patient = fields.Nested(PatientSchema)
    appointment_datetime = fields.DateTime()

# model instances
patient_1 = Patient(name="Lua", email="lua@email.com", dob=datetime(2001,5,31))
patient_2 = Patient(name="Kalani", email="kalani@email.com", dob=datetime(1980,10,2))

appointment_1 = Appointment(patient=patient_1, appointment_datetime = datetime(2023,2,28,18,50))
appointment_2 = Appointment(patient=patient_2, appointment_datetime = datetime(2023,9,30,8,45))
appointment_3 = Appointment(patient=patient_1, appointment_datetime = datetime(2023,10,31,8,30))
appointment_data = [appointment_1, appointment_2, appointment_3]

# serialize nested object

result = AppointmentSchema(many=True).dump(appointment_data)
pprint(result)
# => [{'appointment_datetime': '2023-02-28T18:50:00',
# =>   'patient': {'dob': '2001-05-31', 'email': 'lua@email.com', 'name': 'Lua'}},
# =>  {'appointment_datetime': '2023-09-30T08:45:00',
# =>   'patient': {'dob': '1980-10-02',
# =>               'email': 'kalani@email.com',
# =>               'name': 'Kalani'}},
# =>  {'appointment_datetime': '2023-10-31T08:30:00',
# =>   'patient': {'dob': '2001-05-31', 'email': 'lua@email.com', 'name': 'Lua'}}]
```

```py
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

class SpecialtySchema(Schema):
    code = fields.String()
    description = fields.String()

class DoctorSchema(Schema):
    name = fields.String()
    email = fields.Email()
    specialties = fields.List(fields.Nested(SpecialtySchema))

# model instances

specialty_1 = Specialty(code = "fm", description="Family Medicine")
specialty_2 = Specialty(code="ped", description = "Pediatrics")
specialty_3 = Specialty(code="er", description = "Emergency Medicine")
doctor_1 = Doctor(name="Dr. Bones", email="bones@email.com", specialties = [specialty_1, specialty_2])
doctor_2 = Doctor(name="Dr. Brains", email="brains@email.com", specialties = [specialty_3])

# serialize nested list of objects

result = DoctorSchema(many=True).dump([doctor_1, doctor_2])
pprint(result)
# => [{'email': 'bones@email.com',
# =>  'name': 'Dr. Bones',
# =>  'specialties': [{'code': 'fm', 'description': 'Family Medicine'},
# =>                  {'code': 'ped', 'description': 'Pediatrics'}]},
# =>  {'email': 'brains@email.com',
# =>  'name': 'Dr. Brains',
# =>  'specialties': [{'code': 'er', 'description': 'Emergency Medicine'}]}]
```

```py
# lib/two_way_nesting.py
# two-way nesting and circular references

from marshmallow import Schema, fields, pre_dump
from pprint import pprint

# models

class Author:

    all = []
    def __init__(self, name, email):
        self.name = name
        self.email = email
        type(self).all.append(self)

    def get_books(self):
        """Get list of books for this author"""
        return [book for book in Book.all if book.author is self]

class Book:

    all = []
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author
        type(self).all.append(self)


# schemas

class AuthorSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    # Pass a callable to avoid order-of-declaration issues.
    # Use 'only' or 'exclude' to avoid infinite recursion.
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=("author",)), dump_only=True))

    # Compute list of books for this author prior to serialization
    @pre_dump()
    def get_data(self, data, **kwargs):
        data.books =  data.get_books()
        return data

class BookSchema(Schema):
    isbn = fields.Str()
    title = fields.Str()
    # Use 'only' or 'exclude' to avoid infinite recursion.
    author = fields.Nested(AuthorSchema(exclude=("books",)))

# model instances

author_1 = Author(name="William Faulkner", email="will@email.com")
book_1 = Book(isbn="067973225X", title="As I Lay Dying", author=author_1)
book_2 = Book(isbn="0679732241", title="The Sound and the Fury", author=author_1)
author_2 = Author(name="Colson Whitehead", email="colson@email.com")
book_3 = Book(isbn="0385542364", title = "The Underground Railroad", author=author_2)

# serialize books
print("BOOKS")
book_result = BookSchema(many=True).dump([book_1, book_2, book_3])
pprint(book_result, indent=2)
# => [ { 'author': {'email': 'will@email.com', 'name': 'William Faulkner'},
# =>     'isbn': '067973225X',
# =>     'title': 'As I Lay Dying'},
# =>   { 'author': {'email': 'will@email.com', 'name': 'William Faulkner'},
# =>     'isbn': '0679732241',
# =>     'title': 'The Sound and the Fury'},
# =>   { 'author': {'email': 'colson@email.com', 'name': 'Colson Whitehead'},
# =>     'isbn': '0385542364',
# =>     'title': 'The Underground Railroad'}]

# serialize authors
print("AUTHORS")
author_result = AuthorSchema(many=True).dump([author_1, author_2])
pprint(author_result)
# => [{'books': [{'isbn': '067973225X', 'title': 'As I Lay Dying'},
# =>            {'isbn': '0679732241', 'title': 'The Sound and the Fury'}],
# =>  'email': 'will@email.com',
# =>  'name': 'William Faulkner'},
# => {'books': [{'isbn': '0385542364', 'title': 'The Underground Railroad'}],
# =>  'email': 'colson@email.com',
# =>  'name': 'Colson Whitehead'}]
```

---

## Resources

- [marshmallow](https://pypi.org/project/marshmallow/)
- [marshmallow quickstart](https://marshmallow.readthedocs.io/en/stable/quickstart.html)
