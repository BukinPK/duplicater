from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          CallbackQueryHandler, Filters)
from telegram import Document as TgDocument, File
from telegram.error import BadRequest
import io
from mongoengine import *
from html import escape
from threading import Thread
import duplicater
import markup
from private import TOKEN, ADMIN_ID

updater = Updater(TOKEN, use_context=True)
bot = updater.bot
dispatcher = updater.dispatcher

connect('duplicater')

class User(Document):
    id = IntField(primary_key=True, required=True)
    data = ListField(ListField(StringField()))
    matches = DictField(DictField(DictField(IntField())))
    deleted = ListField(IntField())
    file_id = StringField()
    passed = ListField(IntField())
    last_reply_id = IntField()
    final = BooleanField(default=False)

def start(upd, ctx):
    if not User.objects(id=upd.message.chat.id):
        User(id=upd.message.chat.id).save()

def edit(upd, ctx):
    user = User.objects(id=upd.effective_message.chat.id).first()
    reply_to_message = upd.effective_message.reply_to_message
    if reply_to_message.document.file_id != user.file_id:
        upd.effective_message.edit_text(
            'Открыт на редактирование может быть только один файл.',
            reply_markup=None)
        return
    args = upd.callback_query.data.split()[1:]
    action, number = (args[0], int(args[1])) if len(args) > 1 else (None, None)
    if action == 'del' and number not in user.deleted:
        user.deleted.append(number)
        user.save()
    elif action == 'pass' and number not in user.passed:
        user.passed.append(number)
        user.save()
    post_numbers, text = duplicater.get_one(
        user.data, user.matches, user.deleted, user.passed)

    if post_numbers:
        m = markup.edit(post_numbers)
        try:
            upd.effective_message.edit_text(
                f'<pre>{escape(text)}</pre>', reply_markup=m, parse_mode='HTML')
        except BadRequest as ex:
            if ex.message.startswith('Message is not modified:') \
                    and action == 'pass':
                upd.callback_query.data = f'edit pass {post_numbers[1]}'
                return edit(upd, ctx)
    else:
        upd.effective_message.edit_text(
            '<i>Редактирование окончено.</i>', reply_markup=None,
            parse_mode='HTML')
        user.final = True
        user.save()
        upd.effective_chat.send_action('upload_document')
        file = duplicater.get_final(user.data, user.deleted)
        reply_to_message.reply_document(
            document=io.BytesIO(file.encode()), filename='edited_text.txt',
            caption='<i>Ваш документ был успешно отредактирован.</i>', parse_mode='HTML',
            quote=True)
        upd.effective_message.delete()
        upd.callback_query.answer()

def make_data(upd, ctx):
    msg = upd.message.reply_text(
        '<i>Документ импортируется...</i>',
        parse_mode='HTML', quote=True)
    upd.effective_chat.send_action('typing')

    file = upd.message.document.get_file().download(out=io.BytesIO())
    file.seek(0)
    data = duplicater.make_data(file.read().decode())

    user = User.objects(id=upd.message.chat.id).first()
    if user and not user.final:
        ctx.bot.edit_message_text(
            '<i>Редактирование данного документа было прервано.</i>', user.id,
            user.last_reply_id, reply_markup=None, parse_mode='HTML')
        user.delete()
    user = User(
        id=upd.message.chat.id, data=data, last_reply_id=msg.message_id,
        file_id=upd.message.document.file_id)
    user.save()

    desc = '<i>Документ успешно импортирован.\nИдёт обработка...</i>'
    msg.edit_text( desc, parse_mode='HTML')
    upd.effective_chat.send_action('typing')
    Thread(target=get_matches_thread, args=[user, msg, desc]).start()

def get_matches_thread(user, msg, desc):
    user.matches = duplicater.get_matches(
        user.data, TOKEN, user.id, user.last_reply_id,
        desc=desc + '<pre>')
    user.save()

    match_count = len(
        [k for match_post in user.matches.values() for k in match_post])
    msg.edit_text(
        f'Обработка окончена.\nНайдено дубликатов:<code> {match_count}</code>',
        parse_mode='HTML', reply_markup=markup.main())

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.document, make_data))
dispatcher.add_handler(CallbackQueryHandler(edit, pattern='^edit'))

updater.start_polling()
#updater.idle()
