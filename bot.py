# -*- coding: utf-8 -*-
import os, time
pth = os.path.abspath(__file__)
pth = os.path.dirname(pth)
print(pth)
import telebot

from telebot import types
from ftfcore.core import core
from ftfcore import funcs, telfuncs,config

bot = telebot.TeleBot(config.token)

print("Im in 3")

def zabs(i):
    if int(i)<0: return 0
    else: return i

@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    print(message)
    mess = "Hi"
    cor = core(message.chat.id, message.from_user.id)
    if cor.db.person['id']==0:
        cor.db.add_person_byTL(message.from_user.id,message.from_user.username,message.from_user.first_name + ("" if message.from_user.last_name==None else message.from_user.last_name))
        bot.send_message(message.chat.id, mess)
    else:
        bot.send_message(message.chat.id, "Hi again")
    cor.close()

@bot.message_handler(commands=['exit'])
def handle_hello(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    cor = core(message.chat.id, message.from_user.id)
    cor.db.setMode_person()
    bot.send_message(message.chat.id, "Ваш person_mode = 0")
    cor.close()

@bot.message_handler(commands=['login'])
def handle_hello(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    bot.send_message(message.chat.id, "use /signup")

@bot.message_handler(commands=['signup'])
def handle_signup(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True #bot.reply_to(message, "Эта команда невозможна в группе")
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messbeta = cor.signup(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess=mess, chatid=message.chat.id, chattype=message.chat.type,
                    message_id=message.message_id,
                    sendtome=sendtome, messbeta=messbeta)
    except Exception as e:
        print(e)
        bot.reply_to(message, e)


@bot.message_handler(commands=['toadmin'])
def handle_start(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)

        send, sendtome, mess, messout = cor.sendtoadmin(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)

    except Exception as e:
        print(e)
        bot.reply_to(message, e)


@bot.message_handler(commands=['edit'])
def handle_edit(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.edit(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)
    except Exception as e:
        print(e)
        bot.reply_to(message, e)

@bot.message_handler(commands=['send'])
def handle_send(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:#if True:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.send(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)
    except Exception as e:
       print(e)
       bot.reply_to(message, e)

@bot.message_handler(commands=['newsletters'])
def handle_send(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:#if True:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.newsletters(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)
    except Exception as e:
       print(e)
       bot.reply_to(message, e)

@bot.message_handler(commands=['sendanon'])
def handle_send(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.send(message.text, message.message_id, 1, signed=0)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)

    except Exception as e:
        print(e)
        bot.reply_to(message, e)


@bot.message_handler(commands=['id'])
def handle_id(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.getinfo(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)

    except Exception as e:
        print(e)
        bot.reply_to(message, e)

@bot.message_handler(commands=['myinfo'])
def handle_edit(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.myinfo(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)

    except Exception as e:
        print(e)
        bot.reply_to(message, e)

@bot.message_handler(commands=['token'])
def handle_token(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.gettoken(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)

    except Exception as e:
        print(e)
        bot.reply_to(message, e)

@bot.message_handler(commands=['nickname'])
def nickname_info(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.nickname_info(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)
    except Exception as e:
        print(e)
        bot.reply_to(message, e)

@bot.message_handler(commands=['nicknamenew'])
def nickname_info(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        cor = core(message.chat.id, message.from_user.id)
        send, sendtome, mess, messout = cor.nickname_new(message.text, message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)
    except Exception as e:
        print(e)
        bot.reply_to(message, e)


@bot.message_handler(commands=['test'])
def handle_test(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    cor = core(message.chat.id, message.from_user.id)
    cor.close()
    bot.send_message(config.help_chat, "test")


@bot.message_handler(commands=['help'])
def handle_help(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
    try:
        mess = "Бот способен немного распознавать обычный язык. Чтобы узнать о использовании какой-либо команды используете 'man command' (по примеру команды из linux)"
        bot.send_message(message.chat.id, mess)
    except Exception as e:
        print(e)
        bot.reply_to(message, e)


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        if message.chat.type == 'supergroup' or message.chat.type == 'group': return True

        cor = core(message.chat.id, message.from_user.id)
        file_info = bot.get_file(message.document.file_id)
        # print(message.document)
        downloaded_file = bot.download_file(file_info.file_path)
        #print(message.document.thumb)

        file_name_orig = message.document.file_name # чтобы получить формат файла
        if '.' in file_name_orig and len(file_name_orig)<200 and message.document.file_size<10000000:
            extension = file_name_orig[file_name_orig.rfind('.') + 1:]
            file_name = funcs.keyGenerator(message.from_user.id,length=20) + "-" + str(message.date) + "." + extension
            halfday = int(time.gmtime().tm_hour / 12)
            path = "{}/{}".format(halfday,file_name)
            with open(cor.BASE_DIR+'/doc/{}'.format(path), 'wb') as new_file:
                new_file.write(downloaded_file)

            send, sendtome, mess, messout = cor.file((4,[(file_name,path,extension,file_name_orig)]),message.message_id,1)
        else:
            send, sendtome, mess, messout = [[0,"Файлы должны быть с понятным расширением и не больше 10Mb"]], [], "", ""
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)
    except Exception as e:
        print(e)
        bot.reply_to(message, e)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        if message.chat.type == 'supergroup' or message.chat.type == 'group': return True
        cor = core(message.chat.id, message.from_user.id)
        files = []
        ph = message.photo[-1]
        print(message.photo[-1])
        halfday = int(time.gmtime().tm_hour / 12)
        if True:
            file_info = bot.get_file(ph.file_id)
            time_now = time.localtime()
            file_name_orig = "photo-{}-{:2.0f}-{:2.0f}".format(config.name_of_week_days[time_now.tm_wday],time_now.tm_hour,time_now.tm_min).replace(' ','0')
            extension = 'png'
            file_name_orig = '{}.{}'.format(file_name_orig,extension)
            downloaded_file = bot.download_file(file_info.file_path)

            file_name = funcs.keyGenerator(message.from_user.id) + "-" + str(message.date) + '.png';
            path = "{}/{}".format(halfday, file_name)
            with open(cor.BASE_DIR+'/doc/{}'.format(path), 'wb') as new_file:
                new_file.write(downloaded_file)
            files.append((file_name,path,extension,file_name_orig))

        send, sendtome, mess, messout = cor.file((3,files), message.message_id, 1)
        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type, message_id=message.message_id,
                    sendtome=sendtome, messbeta=messout)

    except Exception as e:
        print(e)
        bot.reply_to(message, e)

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    print(message)
    if True:
    # try:
        if message.reply_to_message == None:
            if message.chat.type == 'supergroup' or message.chat.type == 'group':
                print("effort to speak in group with id = {}".format(message.chat.id))
                return True
            cor = core(message.chat.id, message.from_user.id)
            send, sendtome, mess, messout = cor.ans(message.text,message.message_id,1,entities=message.entities)
        else:
            cor = core(message.chat.id, message.from_user.id)
            send, sendtome, mess, messout = cor.reply(message.text, message.message_id,message.reply_to_message.message_id, 1)

        sendmessage(cor, send, startmess = mess, chatid=message.chat.id, chattype=message.chat.type,
                        message_id=message.message_id, sendtome=sendtome, messbeta=messout)
        cor.close()

    # except Exception as e:
    #     print(e)
    #     bot.reply_to(message, e)

#Для каналов
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    kb = types.InlineKeyboardMarkup()
    # Добавляем колбэк-кнопку с содержимым "test"
    kb.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="test"))
    results = []
    single_msg = types.InlineQueryResultArticle(
        id="1", title="Press me",
        input_message_content=types.InputTextMessageContent(message_text="Я – сообщение из инлайн-режима"),
        reply_markup=kb
    )
    results.append(single_msg)
    bot.answer_inline_query(query.id, results)

# Инлайн-режим с непустым запросом
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print("Call back query")
    try:
        if call.message:
            if call.data == "test": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
            if call.data == "ok": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ok")
            if call.data == "del": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                          text="Тут был секретик (но это не точно. тссс)")
            if call.data == "delpass": bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                          text="Тут был секретик. Используйте /myinfo чтобы снова получить эту информацию")
            if call.data == "signupremove":
                cor = core(call.message.chat.id, call.from_user.id)
                mess = cor.signupremove()
                print("out: {}".format(mess))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=mess)

        # Если сообщение из инлайн-режима
        elif call.inline_message_id:
            if call.data == "test": bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")

        dd = funcs.strtojson(call.data)
        if len(dd)==0: return True
        cor = core(call.message.chat.id, call.from_user.id)
        print(call.data)
        if dd.get('mode')=='edit3':
            mess = cor.edit_phase2(dd)
            print("out: {}".format(mess))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=mess)

        if dd.get('mode')=='nl_remove':
            mess = cor.newsletters_remove(dd)
            print("out: {}".format(mess))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=mess)

        if dd.get('mode')=='nl_add':
            mess = cor.newsletters_add(dd)
            print("out: {}".format(mess))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=mess)

        if dd.get('mode')=='send3':
            mess = cor.send2(dd)
            print("out: {}".format(mess))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=mess)

        if dd.get('mode')=='easyfile':
            mess = cor.easyspeak_file_update(dd, message_id = call.message.message_id)
            print("out: {}".format(mess))
            if mess:
                sendmessage(cor, mess, chatid=call.message.chat.id, chattype=call.message.chat.type,
                        message_id=call.message.message_id, editmessage=True)

        cor.close()
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=e)

    return False

@bot.channel_post_handler(content_types=["text","photo","document"])
def posts_from_channels(message):
    try:
        print("Channel message in {}({}); id={}".format(message.chat.title,message.chat.username,message.chat.id))
        cor = core()
        cor.newsletters_channel_post(chatId=message.chat.id,messId=message.message_id)

    except Exception as e:
        print(e)
        bot.send_message(config.admin_chat, e)


def sendmessage(cor, send, chatid=None, chattype="Normal", message_id = None, sendtome = [], startmess='', messbeta='',editmessage=False):
    markup = types.ReplyKeyboardRemove()
    mess = startmess
    issendout = True
    for s in send:
        if s[0] == -2:
            issendout = False
            if len(s[1]): messbeta += s[1]
        if s[0] == -1 and len(s[1]): messbeta += s[1]
        if s[0] == 0:  # -> это просто текст
            mess += s[1] + "\n"
        elif s[0] == 5:  # -> это клавиатура
            if type(s[1]) == str:
                markup = telfuncs.generate_markup(eval(s[1]))
            else:
                markup = telfuncs.generate_markup(s[1])
        elif s[0] == 6:  # -> это кнопки
            if type(s[1]) == str:
                markup = telfuncs.generate_keyboard(eval(s[1]))
            else:
                markup = telfuncs.generate_keyboard(s[1])
        elif s[0] == 3:  # -> это картинка или файл // s = [3, [already sent,is photo,path]]
            messbeta += ("send file {}\n".format(s[1]))
            if s[1].get('sent') == 1:
                if s[1].get('isphoto') == 1:
                    bot.send_photo(chat_id=chatid, photo=s[1].get('hash'))
                else:
                    bot.send_document(chatid, s[1].get('hash'))

            elif s[1].get('sent') == 0:
                if s[1].get('isphoto') == 1:
                    msg = bot.send_photo(chatid, open(cor.BASE_DIR+'/doc/' + s[1].get('path'), 'rb'))
                    cor.db.add_file(s[1].get('path'), str(msg.photo[0].file_id), s[1].get('isphoto'))
                else:
                    msg = bot.send_document(chatid, open(cor.BASE_DIR+'/doc/' + s[1].get('path'), 'rb'))
                    cor.db.add_file(s[1].get('path'), str(msg.document.file_id), s[1].get('isphoto'))

    if issendout: messbeta += "out: {} \n".format(mess)
    print("beta: ", messbeta)

    cor.sendtoadmin(messbeta,message_id)

    if len(mess):
        if  chattype == 'supergroup' or chattype == 'group':
            if not editmessage:
                bot.send_message(chatid, mess, reply_to_message_id=message_id, reply_markup=markup)
        else:
            if not editmessage:
                bot.send_message(chatid, mess, reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=chatid, message_id=message_id, text=mess, reply_markup=markup)
    cor.close()


if __name__ == '__main__':
    if True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print("{!s}\n{!s}".format(type(e), str(e)))
        print("rebout")