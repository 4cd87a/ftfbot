# -*- coding: utf-8 -*-
"""
@author: K
"""
from telebot import types
from ftfcore import funcs


def generate_markup(answers):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for item in answers:
        markup.add(item)
    return markup

def generate_keyboard(answers):
    keyboard = types.InlineKeyboardMarkup()
    for b in answers:
        if type(b[1])!=str: b[1] = funcs.jsontostr(b[1])
        #print(b[0],b[1])
        #print(strtojson(b[1]))
        url_button = types.InlineKeyboardButton(text=b[0],callback_data=b[1])
        keyboard.add(url_button)
    return keyboard