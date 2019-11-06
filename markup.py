from telegram import InlineKeyboardMarkup, InlineKeyboardButton
def main():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Редактировать', callback_data='edit')]])

def edit(post_numbers):
    buttons_list = [
        InlineKeyboardButton(f'Удалить {i}', callback_data=f'edit del {n}')
        for i, n in enumerate(post_numbers, 1)]
    if buttons_list:
        buttons = [buttons_list[i:i+2] for i in range(0, len(post_numbers), 2)]
    else:
        buttons = []
    return InlineKeyboardMarkup(
        buttons +
        [[InlineKeyboardButton('Дальше', callback_data=f'edit pass {post_numbers[0]}')]])
