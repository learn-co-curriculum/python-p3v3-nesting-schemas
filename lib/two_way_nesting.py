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