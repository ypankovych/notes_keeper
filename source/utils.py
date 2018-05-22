from models import *
from peewee import IntegrityError


def get_category(user, name):
    category = user.categories.select().where(Category.name == name).get()
    return category


def get_user(user_id):
    user = User().select().where(User.user == user_id).get()
    return user


def create_user(user_id):
    try:
        user = User(user=user_id)
        user.save()
    except IntegrityError:
        pass


def create_category(user_id, name):
    user = get_user(user_id)
    try:
        category = Category(user=user, name=name)
        return category.save()
    except IntegrityError:
        return False


def create_note(title, content, user_id, category_name):
    user = get_user(user_id)
    category = get_category(user, category_name)
    note = Note(title=title, content=content, user=user, category=category)
    note.save()


def get_all_categories(user_id):
    user = get_user(user_id)
    categories = user.categories.select()
    return [i.name for i in categories]


def by_category(user_id, category):
    user = get_user(user_id)
    cat = get_category(user, category)
    notes = user.notes.select().where(Note.category == cat)
    return [i.title for i in notes]


def get_post(title, category_name, user_id):
    user = get_user(user_id)
    category = get_category(user, category_name)
    note = user.notes.select().where((Note.category == category) & (Note.title == title))
    return note.first()


def change_category(title, category_name, user_id, new):
    post = get_post(title, category_name, user_id)
    user = get_user(user_id)
    new_category = get_category(user, new)
    post.category = new_category
    post.save()
