import telebot
from utils import *
from fsm import FSM
from templates import note_temp
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot('445020523:AAHaB9p_fvz_OC38xR7WzrtIXvrlc4bV_7M')
states = FSM(default='create')


def error(call):
    bot.answer_callback_query(call.id, 'Error was occurred')
    bot.delete_message(call.from_user.id, call.message.message_id)


@bot.message_handler(commands=['start'])
def start(message):
    create_user(message.chat.id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('My categories', 'Add category')
    bot.send_message(chat_id=message.chat.id, text='Hello', reply_markup=markup)


@bot.message_handler(regexp='My categories')
def show_categories(message):
    categories = get_all_categories(message.chat.id)
    if categories:
        group_categories(message.chat.id, categories)
        states.set_state(message.chat.id, 'category')
    else:
        bot.send_message(chat_id=message.chat.id, text='You have not any categories')


@bot.message_handler(regexp='Add category')
def add_category(message):
    states.init_state(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Enter category name', reply_markup=create_cancel_button('_cancel'))


@bot.message_handler(func=lambda m: states.get_state(m.chat.id) == 'title')
def handle_title(message):
    user = message.chat.id
    states.set_state(user, 'content')
    states.add_extra_state(user, 'title', message.text)
    bot.send_message(user, 'Content:', reply_markup=create_cancel_button())


@bot.message_handler(func=lambda m: states.get_state(m.chat.id) == 'content')
def handle_content(message):
    user = message.chat.id
    title = states.get_extra_state(user, 'title')
    category = states.get_extra_state(user, 'category')
    create_note(title, message.text, user, category)
    bot.send_message(user, 'Done')


@bot.message_handler(func=lambda m: states.get_state(m.chat.id) == 'create')
def handle_category(message):
    create_category(message.chat.id, message.text)
    states.remove_state(message.chat.id)
    bot.reply_to(message, 'Done.')


@bot.callback_query_handler(lambda call: call.data == 'create_note')
def create_notes(call):
    user = call.from_user.id
    category = states.get_extra_state(user, 'category')
    if category:
        states.set_state(user, 'title')
        bot.edit_message_text('Title:', user, call.message.message_id, reply_markup=create_cancel_button())
    else:
        group_notes(call)


@bot.callback_query_handler(lambda call: states.get_state(call.from_user.id) == 'notes')
def get_note(call):
    user = call.from_user.id
    category = states.get_extra_state(user, 'category')
    if not category:
        return select_category(user, call)
    markup = InlineKeyboardMarkup()
    delete_note_brn = InlineKeyboardButton(text='Delete', callback_data='delete_note')
    change_category_btn = InlineKeyboardButton(text='Change category', callback_data='change_c')
    markup.add(delete_note_brn, change_category_btn)
    note = get_post(call.data, category, user)
    if note:
        states.remove_state(user)
        states.add_extra_state(user, 'note', note)
        bot.edit_message_text(text=note_temp.format(note.title, note.content),
                              chat_id=user, message_id=call.message.message_id,
                              parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(lambda call: call.data == 'delete_note')
def delete_note(call):
    note = states.get_extra_state(call.from_user.id, 'note')
    if note:
        delete_post(note)
        bot.answer_callback_query(text='Done', callback_query_id=call.id)
        category_settings(call)


@bot.callback_query_handler(lambda call: call.data == 'change_c')
def change_note_category(call):
    categories = get_all_categories(call.from_user.id)
    note = states.get_extra_state(call.from_user.id, 'note')
    if note:
        states.set_state(call.from_user.id, 'change')
        group_categories(call.from_user.id, categories, True, call.message.message_id)


@bot.callback_query_handler(lambda call: states.get_state(call.from_user.id) == 'change')
def change(call):
    states.remove_state(call.from_user.id)
    note = states.get_extra_state(call.from_user.id, 'note')
    if note:
        change_category(note, call.from_user.id, call.data)
        bot.answer_callback_query(call.id, 'Done')
        category_settings(call)


def select_category(user, call):
    categories = get_all_categories(user)
    bot.answer_callback_query(call.id, 'Select category')
    bot.delete_message(chat_id=user, message_id=call.message.message_id)
    group_categories(user, categories)


def category_exist_error(call):
    bot.answer_callback_query(call.id, 'You have not select category')
    bot.delete_message(user, call.message.message_id)
    group_categories(user, get_all_categories(user))


def send_notes(notes, user, message_id):
    markup = InlineKeyboardMarkup()
    states.set_state(user, 'notes')
    for note in notes:
        btn = InlineKeyboardButton(text=note, callback_data=note)
        markup.add(btn)
    bot.edit_message_text('Notes:', user, message_id, reply_markup=markup)


def group_notes(call):
    user = call.from_user.id
    category = states.get_extra_state(user, 'category')
    if not category:
        return category_exist_error(call)
    notes = by_category(user, category)
    if not notes:
        return bot.answer_callback_query(call.id, 'You have not any notes')
    return send_notes(notes, user, call.message.message_id)


@bot.callback_query_handler(lambda call: call.data == 'show')
def show_notes(call):
    group_notes(call)


def category_settings(call):
    category = states.get_extra_state(call.from_user.id, 'category')
    if category:
        markup = InlineKeyboardMarkup()
        delete_btn = InlineKeyboardButton(text='Delete', callback_data='delete')
        create_btn = InlineKeyboardButton(text='Create note', callback_data='create_note')
        notes_btn = InlineKeyboardButton(text='Show notes', callback_data='show')
        markup.add(notes_btn, create_btn)
        markup.add(delete_btn)
        bot.edit_message_text('Options:', call.from_user.id, call.message.message_id, reply_markup=markup)
    else:
        bot.edit_message_text('Canceled', call.from_user.id, call.message.message_id)


@bot.callback_query_handler(lambda call: call.data == '_cancel')
def _cancel(call):
    states.remove_state(call.from_user.id)
    bot.edit_message_text('Canceled', call.from_user.id, call.message.message_id)


@bot.callback_query_handler(lambda call: call.data == 'cancel')
def cancel(call):
    states.remove_state(call.from_user.id)
    category_settings(call)


@bot.callback_query_handler(lambda call: states.get_state(call.from_user.id) == 'category')
def manage_category(call):
    categories = get_all_categories(call.from_user.id)
    if call.data in categories:
        states.add_extra_state(call.from_user.id, 'category', call.data)
        category_settings(call)


def group_categories(user_id, categories, edit=False, msg_id=None):
    markup = InlineKeyboardMarkup()
    for category in categories:
        button = InlineKeyboardButton(text=category, callback_data=category)
        markup.add(button)
    if not edit:
        bot.send_message(chat_id=user_id, text='Select category', reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=user_id, message_id=msg_id, text='Select category', reply_markup=markup)


def create_cancel_button(callback='cancel'):
    markup = InlineKeyboardMarkup()
    cancel_btn = InlineKeyboardButton(text='Cancel', callback_data=callback)
    markup.add(cancel_btn)
    return markup


if __name__ == '__main__':
    bot.polling(none_stop=True)
