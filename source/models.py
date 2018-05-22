from peewee import *

db = SqliteDatabase('notes.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user = IntegerField(unique=True)


class Category(BaseModel):
    user = ForeignKeyField(User, backref='categories')
    name = CharField(max_length=128, unique=True)


class Note(BaseModel):
    user = ForeignKeyField(User, backref='notes')
    category = ForeignKeyField(Category, backref='notes')
    title = CharField(max_length=50)
    content = TextField()
