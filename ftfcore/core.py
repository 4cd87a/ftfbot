from .SQLighter import SQLighter
from . import funcs,config, telfuncs
import os.path, shutil, io
import random, re, time
import smtplib


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def zabs(i):
    if float(i)<0: return 0
    else: return i

class core:
    def __init__(self, chatId=0,telid = None, idd=None, username=None, base_dir=None,logger=None):
        self.logger = logger
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if base_dir==None else base_dir
        self._print("-------------------------")
        self.db = SQLighter(idd=idd, telid=telid, username=username, chatid=chatId,logger=logger) # Модуль подключения к базе данных
        self.chatId = chatId # Сохраняем ID чата в котором происходят эти сообщения
        self.canwork = self.canworkcheck()

    def _print(self,txt,type="INFO"):
        if self.logger==None:
            print("[{}] : {}".format(type,txt))
        else:
            type = type.lower()
            if type=="info" or type=='i':
                self.logger.info(txt)
            if type=="warning" or type=='w':
                self.logger.warning(txt)
            if type=="error" or type=='e':
                self.logger.error(txt)

    def close(self): # Обязательно закрываем базу данных
        self.db.close()

    def canworkcheck(self):
        if self.db.person.get('id') == 0: # Если случайно пользователь не использовал команду start
            return ([[0,"Используйте сначала команду /start"]],[],"","")
        if False and int(self.db.person.get('access_level'))<3:
            return ([[0, "Bot временно не работает. Cкоро он будет доступен с новыми функциями"]], [], "", "")
        return 0

    def getText(self,mess,pretexts="",change=True,depth=0,command=''): #Чистим текст от всякой фигни -> dict("text":хороший текст,"mode": bool все ли хорошо,"error": ошибка если есть,"depth":какой именно претекст использован)
        #            (текст, текст с которого должен начинаться текст, нужно ли удалять все не противные символы, глубина, если просто команда)
        self._print("pretexts = {}, depth = {}".format(pretexts,depth))
        if change: mess = mess.lower();
        if type(command)==str: command=[command]
        if mess in command:
            return {'text': mess, 'mode': -1, 'depth': depth}
        mod = 1; error = ""
        if type(pretexts)==list:
            pretext = pretexts[0]
            pretexts = pretexts[1:]
        else: pretext = pretexts

        if len(pretext):
            if mess.find(pretext)==0:
                mess = mess[len(pretext):]
            else:
                error = ("Не хватает параметра после команды или неправильная ссылка на команду")
                mod=0

        if mess == '/':
            error = ("Ошибка наличия слеша")
            mod=0

        if len(mess) < 2 and change:
            error = ("Ошибка длины")
            mod=0

        if (mod==0):
            if type(pretexts)==list and len(pretexts): return self.getText(mess,pretexts,change,depth+1)
            return {'text': mess, 'mode': mod,"error":error,'depth':depth}

        '''Удаляем символы'''
        for s in mess:
            if (change and (s in [chr(i) for i in [el for lst in [range(33, 47), range(58, 60), [63]] for el in lst]])) or ((not change) and (s in [chr(i) for i in [34, 39]])):
                mess = mess.replace(s, ' ').replace('  ', ' ')
        return {'text': mess, 'mode': mod,'depth':depth};

    def named(self):
        if self.db.person['name']=="" or self.db.person['name']==None:
            return False
        else:
            return True

    def ans(self,mess,messId=0,where=0,entities=None):#where:0=web;1=telegram
        if self.canwork!=0: return self.canwork
        if len(self.db.person_mode) and 'mode' in self.db.person_mode:
            if self.db.person_mode.get('mode')=='edit':
                return self.edit(mess,messId,where)
            if self.db.person_mode.get('mode')=='edit3':
                return self.edit_phase3(mess,messId,where)
            if self.db.person_mode.get('mode')=='signup':
                return self.signup(mess,messId,where)
            if self.db.person_mode.get('mode')=='send':
                return self.send(mess,messId,where)
            if self.db.person_mode.get('mode')=='newsletters':
                return self.newsletters(mess,messId,where)
            if self.db.person_mode.get('mode')=='send3':
                return self.send3(mess,messId,where,entities=entities)
            if self.db.person_mode.get('mode')=='getinfo':
                return self.getinfo(mess,messId,where)

        nothing = {"mode":0,"ans":"","markup":[]} #dict который отдам в случаи ошибк
        mess = self.getText(mess) # Чистим текст от хлама

        if (mess.get('mode') == 0): return nothing #Если mode=0 => значит неверный формат текста
        messagetext = mess.get('text') #закинули очищеный текст в отдельную переменную

        #print("----------------------------------------------------------------")
        messout = ""
        messbeta = "Person: {}; al: {}; type: {};\n Сообщение: {}; \n".format(self.db.person['username'],self.db.person['access_level'],self.db.person['type'],messagetext)

        if self.db.person['name'] == "" or self.db.person['name'] == None:
            messbeta += "\n should signup\n"
            return ([[0, "Вы не имеете право отправлять сообщения пока не зарегистрируетесь (/signup)"]], [], messout, messbeta)

        quesAll = self.db.get_question() #Получаем другие вопросы

        #Оставляем только которые раньше были получены
        ques = [messagetext]
        for que in quesAll:
            kque = self.db.get_command_byID(que.get('knownQuest'))
            ques.append(kque.get['command'])
        messout += arraytotest(ques[1:],"Вопросы:")

        #Магически получаем ответ
        #diclen, diclist, dicanw \#Получаем (Не знаю что; Словарь ответов(ответ,оценка); Не знаю что)
        anw, trueanw, code, logs = self.getanw(ques) # Получаем ответ на вопрос который был + ответ на вопрос на который он ссылается + информация насколько точно мы это знаем + логи

        #Готовим сообщение
        messans = ""

        #Вывод 2 возможный ответов
        messans += ("Ответы:\n")
        if 'possAns' in logs:
            anslist = logs.get('possAns')
            for i in range(min(3, len(anslist))): messans+= anslist[i][0] + " - " + anslist[i][1] + "\n "
                #dicanw.get(diclist[i][0]).get('command') + " - " + str(round(diclist[i][1], 3)) + "\n "

        '''Вывод ответа'''
        messbeta += messans+'\n'; messans = ""; messout = ""

        sendadmin = []
        send = []
        # if len(diclist) == 0:
        if code == 0:
            #print('code = 0')
            messout += "Нет ответа; "
            send.append([0, "Такое редко бывает. Но я вообще не знаю"])
            # Отправляем просьбу уточнить вопрос
            self.askforhelp(messagetext,messId)
            # Заносим вопрос в базу вопросов
            self.db.add_question(ques[0], 0, self.chatId, messId, 1000)

            return [send, sendadmin, messans, messbeta]

        elif code == 1:
            #print('code = 1')
            send.append([0, "{} -> ".format(anw['command'])])
            # Отправляем просьбу уточнить вопрос
            self.askforhelp(messagetext, messId)

        # Заносим вопрос в базу вопросов
        self.db.add_question(ques[0], anw['id'], self.chatId, messId, anw["accuracy"])

        # текстовый ответ
        anw = trueanw
        anw['text'] = str(anw['text'])
        if len(anw.get('text')):
            try:
                if len(anw.get('text')) > 3 and anw.get('text')[0] == '[' and anw.get('text')[-1] == ']':  # Проверка многозначности ответа
                    messout+=("многозначный ответ; ")
                    com_arr = eval(anw.get('text'))
                    send.append([0, random.choice(com_arr)])
                else:
                    send.append([0, anw.get('text')])
            except SyntaxError:
                messout+=('ошибка SyntaxError; ')
                send.append([0, anw.get('text')])
            except TypeError:
                messout+=('ошибка TypeError; ')
                send.append([0, anw.get('text')])

        # Выполнение функции
        if anw.get('function') != "" and anw.get('function') != None:
            messout+=("function : " + str(anw.get('function'))+"; ")
            # functext = (eval(str(anw.get('function')) + "("+str(message)+", "+str(ques)+", "+str(db)+")"))
            if anw.get('args') != "" and anw.get('args') != None:
                functext = (eval(str(anw.get('function')) + "(" + str(anw.get('args')) + ",messagetext,ques, db)"))
            else:
                functext = (eval(str(anw.get('function')) + "(messagetext,ques, db)"))

            #print(type(functext))
            if functext != None:
                if type(functext) == list:
                    send.append([0, functext[0]])
                    send.append([5, functext[1]])
                elif type(functext) == str:
                    send.append([0, functext])

        # Отправка изображение
        if anw.get('image') != "" and anw.get('image') != None:
            #messout +=('image: ' + anw.get('image')+'; ')
            files = self.db.get_file(anw.get('image'))
            for file in files:
                send.append([3, file])

        if anw.get('makeup') != "" and anw.get('makeup') != None:
            send.append([5, anw.get('makeup')])

        return [send,sendadmin,messans,messbeta]

    def reply(self,mess,messId,replyMessId=None,where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "reply from {} in {} \n".format(self.db.person['username'],self.chatId)

        frm = self.db.message_get(to = (self.db.chatid), mess_id=replyMessId) #self.db.idd if self.db.chatid==None else self.db.chatid)
        if frm:
            messtosend = [[0,mess]]
            if frm.get('type')=='0': # Анонимный ответ
                messtosend.append([0,"(***)",'sign'])
            if frm.get('type')=='1': # Обычный ответ
                messtosend.append([0,"({})".format(self.db.person['name']),'sign'])
            if frm.get('type')=='5': # Ответ из группы помощи
                pass

        #messtosend +="\n(Вы можете ответить на него используя reply к этому сообщению)"

            res = self.sendmess(to=frm.get('from'),send=messtosend, replyTo=frm.get('origmess_id'))
            #if frm.get('type')!=5:# Если запрещается отправлять ответ на сообщение из группы помощи
            if res!=None:
                self.db.message_add(frm=self.db.chatid, to=frm.get('from'), mess_id=res.message_id,origmess_id=messId, typ=frm.get('type'))
                #self.db.tel_message_add(self.db.chatid, frm.get('from'), res.message_id,messId,frm.get('type'))

        else:
            messbeta += "не существует id c данным вопросом \n"
            messout  += "не существует id c данным вопросом \n"

        return (send, sendadmin, messout, messbeta)

    def file(self,files,messId,where=0):
        if self.canwork != 0: return self.canwork
        if len(self.db.person_mode) and 'mode' in self.db.person_mode:
            mode = '{}'.format(self.db.person_mode.get('mode'))
            if mode=='edit3':
                return self.edit_phase3(files,messId,where)
            if mode=='send3':
                return self.send3(files,messId,where)
            # if self.db.person_mode.get('mode')=='send3':
            #     return self.send3(files,messId,where)
            if  mode == '0' or mode =='wassent':
                return self.easyspeak_file_add(files)


        send = [[0,"Файл(ы) не будет сохранен так как не несет никакой пользы"]]; sendadmin = []; messout = ""; messbeta = "no right file from {} in {} \n".format(self.db.person['username'],self.chatId)
        for file_name, path, extension in files[1]:
            os.remove(self.BASE_DIR+'/doc/{}'.format(path))

        return (send,sendadmin,messout,messbeta)

    def edit(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "edit from {} in {} \n".format(self.db.person['username'],self.chatId)

        mess = self.getText(mess,['/edit ',''],command='/edit')  # Чистим текст от хлама
        if (mess.get('mode') == 0): return ([[0,mess.get('error')]],sendadmin,messout,messbeta)  # Если mode=0 => значит неверный формат текста
        if (mess.get('mode') == -1):
            self.db.setMode_person({"mode":'edit'})
            return ([[0, "Введите вопрос"]], sendadmin, messout, messbeta)

        messagetext = mess.get('text')  # закинули очищеный текст в отдельную переменную

        anw, trueanw, code, logs = self.getanw([messagetext])

        if code==0 or code==1:
            send.append([0, "Похожих вопросов в базе не найдено. Вы хотите создать следующий вопрос"])
            idd = self.db.tempdata_add(messagetext)
            send.append([6, [["Дословный вопрос: {}".format(messagetext),
                              {"mode": "edit3", "text": idd, "qmode": "new"}]]])
        else:
            send.append([0,"Ответ на данный вопрос: {}".format(trueanw.get('text'))])
            if (anw.get('id')!=trueanw.get('id')):
                send.append([0,"Этот вопрос вопрос ссылается на другой. Вы можете поменять ответ на базовый вопрос или отменить связь и уточнить ответ именно на данный вопрос."])
                send.append([0,"Выберите вопрос, который хотите редактировать:"])
                keys = [["Оригинал (#{}): {}".format(trueanw.get('id'),trueanw.get('command')),{"mode":"edit3","id":trueanw.get('id'),"qmode":"org"}],
                        ["Ближайший вопрос (#{}): {}".format(anw.get('id'), anw.get('command')),{"mode":"edit3","id":anw.get('id'),"qmode":"link"}]]
                if messagetext!=anw.get('command'):
                    idd = self.db.tempdata_add(messagetext)
                    keys.append(["Дословный вопрос: {}".format(messagetext),{"mode":"edit3","text":idd,"qmode":"new"}])

                send.append([6, keys])
            else:
                send.append([0, "Выберите вопрос, который хотите редактировать:"])
                keys = [["Ближайший вопрос (#{}): {}".format(trueanw.get('id'),trueanw.get('command')),{"mode":"edit3","id":anw.get('id'),"qmode":"org"}]]
                if messagetext!=anw.get('command'):
                    idd = self.db.tempdata_add(messagetext)
                    keys.append(["Дословный вопрос: {}".format(messagetext),{"mode":"edit3","text":idd,"qmode":"new"}])
                send.append([6, keys])

        return (send,sendadmin,messout,messbeta)

    def edit_phase2(self,dd):
        if self.canwork != 0: return self.canwork
        self.db.setMode_person(dd)
        if dd.get('qmode')=='new':
            textq = self.db.tempdata_get(dd.get('text')).get('data')
            mess = "Вы создаете новый вопрос '{}'\nВведите ответ который желаете. \nЕсли хотите настроить ссылку -- введите сообщение типа '#id 000'".format(textq)
        else:
            comd = self.db.get_command_byID(dd.get('id'))
            if comd.get('link')!=0:
                text = "#id: {}".format(comd.get('link'))
            else:
                text = comd.get('text')
            mess = "Вы меняете вопрос '{}' (#id: {}).\nОтвет на данный момент: '{}', с точностью {}.\nВведите ответ который желаете.\nЕсли хотите настроить ссылку введите сообщение например '#id 000'".format(comd.get('command'),comd.get('id'),text,comd.get('accuracy'))
        return mess

    def edit_phase3(self, mess, messId=0, where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "edit3 from {} in {} \n".format(self.db.person['username'],self.chatId)
        if self.db.person.get('access_level')==0:
            send.append([0,"Вы заблокированы и не имеете право изменять ответы"])
        else:
            if self.db.person_mode.get('qmode')=='new':
                textq = self.db.tempdata_get(self.db.person_mode.get('text')).get('data')
                if type(mess) == tuple:
                    for file_name, path, extension in mess[1]:
                        copyfile(path_in=self.BASE_DIR+'/doc/{}'.format(path), path_out = self.BASE_DIR + '/doc/{}'.format(file_name))
                    files = str([m[0] for m in mess[1]])
                    res = self.db.add_command_simple(textq, image=files.replace("'",'"'))
                    if type(res)!=list or len(res)==0:
                        send.append([0, "Добавлена новая команда '{}'(#{})->\n'{}'\n".format(textq, res, "image(s)")])
                    else:
                        send.append([0,"Вы хотите создать новый вопрос. Однако такой вопрос уже существует (#id: {})".format(res[0].get('id'))])
                else:
                    if re.search("^#id [0-9]+$", mess)!=None:
                        mess = {'mode':1,'text':'','link':mess[4:]}
                    else: mess = self.getText(mess,change=False)  # Чистим текст от хлама
                    if (mess.get('mode') == 0):
                        send.append([0,"Сообщение не подходит по формату"]) # Если mode=0 => значит неверный формат текста
                    else:
                        res = self.db.add_command_simple(textq, mess)
                        if (type(res)!=list or len(res)==0):
                            send.append([0, "Добавлена новая команда '{}'(#{})\n->'{}'\n".format(textq, res, mess.get('text'))])
                        else:
                            send.append([0,"Вы хотите создать новый вопрос. Однако такой вопрос уже существует (#id: {})".format(res[0].get('id'))])

            else:
                comd = self.db.get_command_byID(self.db.person_mode.get('id'))
                if (comd.get('root')==1 and self.db.person.get('access_level')>=2) or comd.get('root')==0:
                    textq = self.db.person_mode.get('id')
                    if type(mess) == tuple:
                        for file_name, path, extension in mess[1]:
                            copyfile(path_in=self.BASE_DIR+'/doc/{}'.format(path), path_out=self.BASE_DIR + '/doc/{}'.format(file_name))
                        files = str([m[0] for m in mess[1]])
                        self.db.edit_command_simple_byID(self.db.person_mode.get('id'), image=files.replace("'",'"'))
                        send.append([0, "#id: {}->\n'{}'".format(textq, "image(s)")])
                        messbeta += ("edit command #id: {}->\n'{}'\n".format(textq, str(mess[1])))
                    else:
                        if re.search("^#id [0-9]+$", mess) != None:
                            mess = {'mode': 1, 'text':'','link':mess[4:]}
                        else:
                            mess = self.getText(mess,change=False)  # Чистим текст от хлама
                        if (mess.get('mode') == 0):
                            send.append([0, "Сообщение не подходит по формату"])  # Если mode=0 => значит неверный формат текста
                        else:
                            self.db.edit_command_simple_byID(self.db.person_mode.get('id'), mess)
                            send.append([0, "#id: {}->\n'{}'".format(textq, mess.get('text'))])
                            messbeta += ("edit command #id: {}->\n'{}'\n".format(textq, mess.get('text')))
                else:
                    send.append([0, "У вас не достаточно прав чтобы редактировать данное сообщение"])

        self.db.setMode_person()
        return (send,sendadmin,messout,messbeta)

    def newsletters(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "newsletters from {} in {} \n".format(self.db.person['username'],self.chatId)
        self.db.setMode_person()
        if not self.named():
            return ([[0, "Вы не имеете право на это пока не зарегистрируетесь (/signup)"]], sendadmin, messout, messbeta)

        mess = self.getText(mess,['/newsletters ',''],change=False,command='/newsletters')  # Чистим текст от хлама
        if (mess.get('mode') == 0):
            return ([[0,mess.get('error')]],sendadmin,messout,messbeta)  # Если mode=0 => значит неверный формат текста
        if (mess.get('mode') == -1): # Если просто введенна комманда
            self.db.setMode_person({"mode":'newsletters'})

            newsletters = str(self.db.person['newsletters']).split(',')
            if len(newsletters)==0 or newsletters==['']:
                send.append([0,"На данный момент вы не подписаны ни на какую рассылку. Вы можете ввести название рассылки, чтобы подписаться на нее. Или написать /exit, чтобы ничего не делать"])
                return (send, sendadmin, messout, messbeta)
            keys = []
            send.append([0,
                         "Вы подписаны на данные рассылки. \n - Если хотите удалить что-то, нажмите на нее. \n - Хотите добавить еще одну, введите имя.  \n - Ничего не делать, напишите /exit"])
            for n in newsletters:
                if len(n):
                    nl = self.db.newsletters_get(idd=n,retlist=False)
                    keys.append([nl['name'],{"mode": "nl_remove", "id": n}])

            keys.append(["Удалить это сообщение", "del"])

            send.append([6, keys])
            return (send,sendadmin,messout,messbeta)

        messagetext = mess.get('text')  # закинули очищеный текст в отдельную переменную
        messbeta += "send to {}\n".format(messagetext)

        # Проверяем есть ли такой лист рассылок
        if re.match("^[A-Za-zА-Яа-я0-9\- ]+$", messagetext) == None:
            send.append([0, "Использованы недопустимые символы."])
            return (send, sendadmin, messout, messbeta)

        res = self.db.newsletters_get(name=messagetext.lower(), full=False,retlist=False)
        if len(res):
            if len(res) > 1:
                keys = []
                for r in res:
                    if r['count'] != res[0]['count']: break
                    if r['root'] > int(self.db.person.get('access_level')): continue
                    messbeta += "list = {} \n".format(r['name'])
                    keys.append(["{}".format(r['name']), {"mode": "nl_add", "id": r['id']}])
                if len(keys):
                    send.append([0, "Уточните в какую группу вы хотите вступить"])
                    send.append([6, keys])
                    return (send, sendadmin, messout, messbeta)

            if int(res[0]['root']) > int(self.db.person.get('access_level')):
                send.append([0, "Вы не имеете право отправлять сообщения данному списку рассылки."])
                return (send, sendadmin, messout, messbeta)

            messbeta += "to list = {} \n".format(res[0].get('name'))
            self.db.newsletters_add_person(res[0]['id'],self.db.idd)
            send.append([0, 'Теперь вы будете получать уведомления от "{}"'.format(res[0]['name'])])
            self.db.setMode_person()
            return (send, sendadmin, messout, messbeta)
        else:
            return ([[0,"Не существует рассылки с таким именем"]],sendadmin, messout, messbeta)

    def newsletters_remove(self,dd):
        if self.canwork != 0: return self.canwork
        self.db.setMode_person()
        self.db.newsletters_remove_person(idd_newsletter=dd['id'],idd_person=self.db.idd)
        mess = "Сделано. Теперь вы будете получать меньше сообщений"
        return mess

    def newsletters_add(self,dd,person_id=None):
        if person_id == None:
            if self.canwork != 0: return self.canwork
            self.db.setMode_person()
            person_id = self.db.idd
        self.db.newsletters_add_person(idd_newsletter=dd['id'],idd_person=person_id)
        mess = "Сделано. Теперь вы будете получать больше сообщений"
        return mess

    def newsletters_channel_post(self,chatId,messId):
        self._print("newsletters_channel_post: chatId = {}, messId = {}".format(chatId, messId))
        newsletter = self.db.newsletters_get(telidd=chatId)
        if newsletter:
            import telebot
            bot = telebot.TeleBot(config.token)
            for p in newsletter['list']:
                #print("send to ",self.db.get_person_telid(p), chatId, messId)
                bot.forward_message(self.db.get_person_telid(p), chatId, messId)

    def getinfo(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "getinfo from {} in {} \n".format(self.db.person['username'],self.chatId)
        if self.db.person['name'] == "" or self.db.person['name'] == None:
            messbeta += "\n should signup\n"
            return ([[0, "Вы не имеете право отправлять сообщения пока не зарегистрируетесь (/signup)"]], [], messout, messbeta)

        mess = self.getText(mess,['/id ',''],command='/id')  # Чистим текст от хлама
        if (mess.get('mode') == 0): return ([[0, mess.get('error')]], sendadmin, messout, messbeta)  # Если mode=0 => значит неверный формат текста
        if (mess.get('mode') == -1):
            self.db.setMode_person({"mode":'getinfo'})
            return ([[0, "Введите вопрос"]], sendadmin, messout, messbeta)

        messagetext = mess.get('text')  # закинули очищеный текст в отдельную переменную
        code = 2
        messbeta += ("on = {}".format(messagetext))
        if re.search("^[0-9]+$",messagetext)==None:
            anw, trueanw, code, logs = self.getanw([messagetext])
        else:
            anw = self.db.get_command_byID(messagetext)
            if anw==0: code=0 #Если ответа в базе не найдено (что возможно по id), код ошибки 0

        if code==0 or code==1:
            send.append([0, "Похожих вопросов в базе не найдено"])
        else:
            send.append([0, "id = {}; Вопрос = {};".format(anw.get('id'),anw.get('command'))])
            send.append([0, "Ответ = {};".format(anw.get('text'))])
            send.append([0, "search={}; function={}; args={}; image={}; year={}; semester={}; markup={}; description={};added={};\nedited={};editedBy={};root={};accuracy={};link={}".format(
                anw.get('search'),
                anw.get('function'),
                anw.get('args'),
                anw.get('image'),
                anw.get('year'),
                anw.get('sem'),
                anw.get('makeup'),
                anw.get('descr'),
                anw.get('added'),
                anw.get('edited'),
                anw.get('editedBy'),
                anw.get('root'),
                anw.get('accuracy'),
                anw.get('link')
            )])

        return (send,sendadmin,messout,messbeta)

    def getanw(self, ques):
        '''-------------------Поиск ответа------------------'''
        dic = {}; dicanw = {}
        for q in range(min(2, len(ques))):

            # print(row)
            words = ques[q].lower().split(' ')
            if q == 0:
                row = self.db.get_command(ques[q].lower())
                if row != []:  # полная проверка актуального запроса, иначе нет смысла
                    #print("Проверка полного предложения: " + ques[q].lower())
                    if len(row):
                        for i in range(len(row)):
                            dicanw.setdefault(row[i].get('id'), row[i])
                            if len(words) == 1:
                                dic.update({row[i].get('id'): dic.setdefault(row[i].get('id'), 0) + zabs(
                                    len(words) - abs(len(words) - row[i].get('command').count(' '))) * 3.04})
                            else:
                                dic.update({row[i].get('id'): dic.setdefault(row[i].get('id'), 0) + zabs(
                                    len(words) - abs(len(words) - row[i].get('command').count(' '))) * 1.6})

                    ##arr = sorted([[k, v] for k, v in dic.items()], key=lambda x: x[1], reverse=True)
                    ##for i in range(min(5, len(arr))): print('    ' + dicanw.get(arr[i][0]).get('command') + ' - ' + str(arr[i][1]))
                    ##print('\n')

            ##print("Проверка словосочитаний")
            for j in range(len(words) - 1):
                w = words[j] + ' ' + words[j + 1]
                if len(w) > 1:
                    row = self.db.get_command(w)
                    ##print("словосочитание: " + w)
                    for i in range(len(row)):
                        comd = row[i].get('command')
                        '''Проверка на сколько совпало'''
                        indx = 1
                        if comd.find(w):  # Если это слово не первое смотрим что спереди не буква
                            if not (comd[comd.find(w) - 1:comd.find(w)].isalpha()):
                                indx += 0.1
                        if (len(comd) - comd.find(w) - 2):  # Если это слово не последнее смотрим что сзади не буква
                            if not (comd[comd.find(w):comd.find(w) + 1].isalpha()):
                                indx += 0.1

                        dicanw.setdefault(row[i].get('id'), row[i])
                        dic.update({row[i].get('id'): dic.setdefault(row[i].get('id'), 0) + indx * 2.4 / ((q + 1) ** 2)})
                        ## print("q:" + row[i][0] + str(dic.get(row[i][0])))

            ##arr = sorted([[k, v] for k, v in dic.items()], key=lambda x: x[1], reverse=True)
            ##for i in range(min(5, len(arr))): print('    ' + dicanw.get(arr[i][0]).get('command') + ' - ' + str(arr[i][1]))
            ##print('\n')

            ##print("Проверка отдельных слов")
            for w in words:
                if len(w) > 1:
                    row = self.db.get_command(w)
                    # print("слово:"  + w)
                    for i in range(len(row)):
                        '''Проверка на сколько совпало'''
                        indx = 1
                        fin = row[i].get('command').find(w)
                        if fin:  # Если это слово не первое смотрим что спереди не буква
                            # print("слово не первое")
                            if not ((row[i].get('command'))[fin - 1:fin].isalpha()):
                                # print("слово пробел до")
                                indx += 0.15
                        else:
                            indx += 0.15

                        if (len(row[i].get('command')) - fin - len(
                                w) - 2):  # Если это слово не последнее смотрим что сзади не буква
                            # print("слово не последнее")
                            if not ((row[i].get('command'))[fin + len(w):fin + len(w) + 1].isalpha()):
                                # print("слово пробел после")
                                indx += 0.15
                        else:
                            indx += 0.15

                        dicanw.setdefault(row[i].get('id'), row[i])
                        dic.update({row[i].get('id'): dic.setdefault(row[i].get('id'), 0) + indx / (
                                    (q + 1) ** 2)})
                        # print("q:" + row[i][0] + str(dic.get(row[i].get('command'))))

            ##arr = sorted([[k, v] for k, v in dic.items()], key=lambda x: x[1], reverse=True)
            ##for i in range(min(5, len(arr))): print('    ' + dicanw.get(arr[i][0]).get('command') + ' - ' + str(arr[i][1]))
            ##print('\n')

        # bot.send_message(message.chat.id, messagetext)

        '''Сортирует ответы'''
        # abs(len(ques[0])*1.-v)*len(k.split(' '))+abs(len(k.split(' '))*1.-v)*len(ques[0])*1.5
        #print('\n')
        #print("Сортирует ответы")
        arr = sorted([[k, v] for k, v in dic.items()], key=lambda x: x[1], reverse=True)
        for i in range(min(5, len(arr))): print('    ' + dicanw.get(arr[i][0]).get('command') + '  -  ' + str(arr[i][1]))
        # print(dic.items())
        try:
            diclist = [[k, (zabs((ques[0].count(' ') + 1) * 4.24 + 0.2 - v))] for k, v in
                       dic.items()]  # тут должен быть минус 0.2
            # diclist = [[k,abs(len(k.split(' '))-v)/(1+len(k.split(' '))*0.5)/(v+1)**3] for k, v in dic.items()]
        except ZeroDivisionError:
            print("Деленние на 0")
            return 1
        diclist.sort(key=lambda x: x[1], reverse=False)

        '''Выводим ответы'''
        #print('\n')
        #print("Возможные ответы:")
        #for i in range(min(5, len(diclist))): print('    ' + dicanw.get(diclist[i][0]).get('command') + '  -  ' + str(diclist[i][1]))
        #print('\n')

        '''Вывод первых 3 вопросов в сообщение'''
        '''mess=""
        if person_data[5]:
            for i in range(min(2,len(diclist))):
                mess = mess + diclist[i][0] + " - " + str(round(diclist[i][1],3)) + "\n"
            mess += "\n"
        print(mess)'''

        dicanwret = {}
        for i in range(min(5, len(diclist))):
            # print(dicanw.get(diclist[i][0]))
            dicanwret.setdefault(diclist[i][0], dicanw.get(diclist[i][0]))


        if len(diclist) == 0:
            return 0, 0, 0, {'possAns':[]}
        else:
            anw = dicanw.get(diclist[0][0])
            anw['accuracy'] = diclist[0][1]
            if anw.get('link') == 0:
                trueanw = anw
            else:
                trueanw = self.db.get_command_byID(anw.get('link'))
            ##print(anw)
            ##print(trueanw)

            possAns = []
            for i in range(min(3, len(diclist))):
                possAns.append([dicanw.get(diclist[i][0]).get('command'), str(round(diclist[i][1], 3))])


            if len(diclist) > 1 and diclist[0][1] == diclist[1][1]:
                return anw, trueanw, 1, {'possAns':possAns}
            else: return anw, trueanw, 2, {'possAns':possAns}

        # except Exception as e:
        #    print("{!s}\n{!s}".format(type(e), str(e)))

    def signup(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "signup from {} in {} \n".format(self.db.person['username'],self.chatId)
        dd = self.db.person_mode
        if dd.get('mode')!='signup': #str(dd.get('mode')) == '0': # 0 is state by default
            if self.db.person['name'] == "" or self.db.person['name'] == None:
                messbeta += ('Starting signup processus\n')
                send.append([0, "Введите вашу 'Имя Фамилию', чтобы вам могли писать (или код приглашения)"])
                self.db.setMode_person({"mode":"signup","stage":1})
            else:
                send.append([0, "Вы уже зарегистрированы"])
            return (send, sendadmin, messout, messbeta)

        if dd.get('mode')=='signup':
            mess = self.getText(mess,change=False)  # Чистим текст от хлама
            if (mess.get('mode') == 0): return (send, sendadmin, messout, messbeta)  # Если mode=0 => значит неверный формат текста
            messagetext = mess.get('text')  # закинули очищеный текст в отдельную переменную

            if dd.get('stage')=='1': # Ввели фамилию
                if re.match("^[А-Я][а-я]+(-[А-Яа-я]+){0,1} [А-Я][а-я]+(-[А-Яа-я]+){0,1}$", messagetext)==None:
                    if re.search("^[0-9a-z]{4,6}$", messagetext)==None:
                        send.append([0,"Ответ не подходит по формату ^[А-Я][а-я]+ [А-Я][а-я]+$"])
                    else:
                        temid = funcs.keyDecoder(messagetext)
                        dat = self.db.tempdata_get(temid).get('data')
                        if dat!=None:
                            dat = funcs.strtojson(dat)
                            if "key" in dat and dat.get('key')==messagetext:
                                self.db.tempdata_del(temid)
                                dd['stage'] = 4
                                if "name" in dat: dd['name'] = dat.get("name")
                                if "surname" in dat: dd['surname'] = dat.get("surname")
                                if "email" in dat: dd['email'] = dat.get("email")
                                if "year_start" in dat: dd['year_start'] = dat.get("year_start")
                                if "beta" in dat: dd['beta'] = dat.get("beta")
                                if "access_level" in dat: dd['access_level'] = dat.get("access_level")
                                if "type" in dat: dd['type'] = dat.get("type")
                                self.db.setMode_person(dd)
                                send.append([0, "Введите пин код (это что-то +- простое).\n (4<= pin <=8) є [a-zA-Z0-9]"])
                            else: send.append([0,"Это не является кодом"])
                        else: send.append([0, "Это не является кодом"])
                else:
                    dd['stage'] = 2
                    dd['name'] = messagetext
                    self.db.setMode_person(dd)
                    send.append([0, "Введите свой email. (чтобы пропустить напишите 0)"])
                return (send, sendadmin, messout, messbeta)

            if dd.get('stage') == '2': #Ввели email (optional)
                if messagetext == "0":
                    messagetext = ""
                if messagetext != "" and  re.search("^[A-Za-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,5}$", messagetext) == None:
                    send.append([0, "Ответ не подходит по формату (^[A-Za-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,5}$)"])
                else:
                    dd['stage'] = 3
                    dd['email'] = messagetext
                    self.db.setMode_person(dd)
                    send.append([0, "Введите год поступления на ФТФ"])
                return (send, sendadmin, messout, messbeta)

            if dd.get('stage') == '3': #Ввели год поступления на фтф
                if re.search("^[12][0-9]{3}$", messagetext) == None:
                    send.append([0, "Ответ не подходит по формату (^[12][0-9]{3}$)"])
                else:
                    dd['stage'] = 4
                    dd['year_start'] = messagetext
                    self.db.setMode_person(dd)
                    send.append([0, "Введите пин код (это что-то +- простое).\n (4<= pin <=12) є [a-zA-Z0-9]"])
                return (send, sendadmin, messout, messbeta)

            if dd.get('stage') == '4': #Ввели pin код
                pin = funcs.pinHash(messagetext)
                if pin.get("bon") == False:
                    send.append([0, pin.get('error')])
                    return (send, sendadmin, messout, messbeta)
                else:
                    dd['stage'] = 5
                    dd['pin'] = pin.get('hash')
                    password = funcs.passGenerator();
                    dd['password'] = funcs.passwordHash(password).get('hash')
                    dd['token'] = funcs.tokenGenerator(self.db.idd)
                    if self.db.add_person_info(dd):
                        self.newsletters_add({'id':1})
                        send.append([0, "Ваша информация такова:"])
                        send.append([0, "Имя: {}".format(dd['name'])])
                        send.append([0, "Email: {}".format(dd['email'])])
                        send.append([0, "Год поступления: {}".format(dd['year_start'])])
                        send.append([0, "Password: {}".format(password)])
                        send.append([0, "Token: /token"])
                        send.append([0, "(Пароль храниться в хеше, поэтому его невозможно востановить)"])
                        send.append([0, "Советую удалить это сообщение и хранить пароль в другом месте."])
                        send.append([0, "(однако на данный момент пароль нигде не используется, в дальнейшем он будет использоваться где-то в web-версиях (которая даже существует), но на данный момент просто не обращайте внимания)"])
                        send.append([0, "Вы по-умолчанию подписаны на рассылку об обновлениях бота. Чтобы узнать больше о функциональности бота можете спросить 'Что ты умеешь'"])
                        send.append([6,[["Удалить это сообщение","delpass"],["Отменить все изменения","signupremove"]]])
                        self.db.setMode_person()
                        return (send, sendadmin, messout, messbeta)


        send.append([0, "Какая-то ошибка. Код ошибки {}. Попробуйте /exit".format(funcs.passGenerator(12))])
        return (send, sendadmin, messout, messbeta)

    def myinfo(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        self.db.setMode_person()
        send = []; sendadmin = []; messout = ""; messbeta = "myinfo from {} in {} \n".format(self.db.person['username'],self.chatId)
        send.append([0, "Вся ваша информация такова:"])
        send.append([0, "Username: {}".format(self.db.person['username'])])
        send.append([0, "Beta mode: {}".format(self.db.person['beta'])])
        send.append([0, "access_level: {}".format(self.db.person['access_level'])])
        send.append([0, "type: {}".format(self.db.person['type'])])

        if self.db.person['name']=="" or self.db.person['name']==None:
            send.append([0,"Вы не ввели свое настоящее имя"])
        else:
            send.append([0, "Имя: {}".format(self.db.person['name'])])
            send.append([0, "Email: {}".format(self.db.person['email'])])
            send.append([0, "Год поступления: {}".format(self.db.person['year_start'])])
            send.append([0, "Token: /token"])

        send.append([-2, ""])

        return (send,sendadmin,messout,messbeta)

    def gettoken(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        self.db.setMode_person()
        send = []; sendadmin = []; messbeta = "gettoken from {} in {} \n".format(self.db.person['username'],self.chatId)
        send.append([0,self.db.person['token']])
        send.append([6,[["Удалить это сообщение", "del"]]])
        send.append([-2, ""])
        return send, sendadmin, "", messbeta

    def nickname_info(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        self.db.setMode_person()
        send = []; sendadmin = []; messbeta = "nickname_info from {} in {} \n".format(self.db.person['username'],self.chatId)
        nicks = self.db.nicknames_get(person_id=self.db.idd)
        if nicks:
            send.append([0, 'Ваши псевдонимы:'])
            for nick in nicks:
                if nick['active']==1:
                    send.append([0, '{}'.format(nick['nickname'])])
                else:
                    send.append([0, '{} (Не активен)'.format(nick['nickname'])])
        else:
            send.append([0,'У вас нет псевдонимов.'])
        send.append([0, 'Используйте /nicknamenew, чтобы получить новый псевдоним.'])
        send.append([0, 'Используя псевдоним вам могут написать, при этом вы останетесь анонимным.'])
        return send, sendadmin, "", messbeta

    def nickname_new(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        self.db.setMode_person()
        send = []; sendadmin = []; messbeta = "nickname_new from {} in {} \n".format(self.db.person['username'],self.chatId)
        nickname = 1
        res = int(self.db.nicknames_add(person_id=self.db.idd,nickname=nickname))
        if res<5200:
            nickname = funcs.generateHash(res, 6)
        else: nickname = funcs.generateHash(res, 10)

        res = self.db.nicknames_update(res, nickname)
        send.append([0, 'Ваш новый псевдоним'])
        send.append([0, '{}'.format(nickname)])
        return send, sendadmin, "", messbeta

    def signupremove(self):
        if self.canwork != 0: return self.canwork
        if self.db.add_person_info({'name':'','email':'','year_start':'','pin':'','password':'','token':''}):
            return "Ваши данные успешно удалены"
        return "Уупс"

    def send(self,mess='',messId=0,where=0,signed = 1, title='',ismail=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "send from {} in {} \n".format(self.db.person['username'],self.chatId)
        #self.db.setMode_person()
        if self.db.person['name'] == "" or self.db.person['name'] == None:
            return ([[0, "Вы не имеете право отправлять сообщения пока не зарегистрируетесь (/signup)"]], sendadmin, messout, messbeta)

        if ismail==1:
            tosend = mess.replace('"','').replace("'",'').replace('`','')
            titleId = re.match("#[A-Za-z0-9]+$", title)
            if titleId!=None:
                titleId = funcs.keyDecoder(titleId[1:])
                self.db.message_get(to=self.db.idd,mess_id=titleId)


        else:
            mess = self.getText(mess,['/sendanon ','/send ',''],change=False,command=['/send','/sendanon']) # Чистим текст от хлама
            if (mess.get('mode') == 0): return ([[0,mess.get('error')]],sendadmin,messout,messbeta)  # Если mode=0 => значит неверный формат текста
            if (mess.get('mode') == -1):
                self.db.setMode_person({"mode": "send", "signed": signed})
                return ([[0, "Введите имя кому вы хотите отправить текст"]], sendadmin, messout, messbeta)

            if mess['depth']==2 and 'signed' in self.db.person_mode: signed = self.db.person_mode['signed']

            messagetext = mess.get('text')  # закинули очищеный текст в отдельную переменную
            messbeta += "send to {}\n".format(messagetext)

        replied = False

        if messagetext.lower()[:4]=="re: ":
            messagetext = messagetext[4:]
            replied = True
        if re.match("^[a-z0-9]{6}$", messagetext) != None:
            nick = self.db.nicknames_get(nickname=messagetext)
            if nick:
                if nick['active']==1:
                    messbeta += "only person by nick\n"
                    send.append([0, "Что вы хотите отправить? (сообщение так же будет отправленно анонимно)"])
                    if str(self.db.get_person_any_param(param='wts',idd=nick['person_id'])) == '1':
                        send.append([0,
                                 "Сообщение будет отправлено на почту, поэтому можете указать тему письма написав в первой строчке: [тема письма]. В противном случаи тема письма будет ваше имя."])
                    self.db.setMode_person({"mode": "send3", "to": nick['person_id'], "list": 0, 'signed': 0})
                else:
                    send.append([0, "Такой псевдоним уже не активен."])
            else:
                send.append([0, "Такого псевдонима не существует."])

            return (send, sendadmin, messout, messbeta)

        res = self.db.mailingList_get(name=messagetext.lower(), full=False)
        # Проверяем есть ли такой лист рассылок
        if re.match("^[A-Za-zА-Яа-я0-9\- ]+$", messagetext)==None:
            send.append([0, "Использованы недопустимые символы."])
            return (send, sendadmin, messout, messbeta)
        res = self.db.mailingList_get(name=messagetext.lower(),full=False)
        if len(res):
            if len(res)>1:
                #send.append([0, "По загадочным причинам этот список рассылки создан больше одного раза. Свяжитесь пожалуйста с админом."])
                keys = []
                max1 = res[0]['count']
                for r in res:
                    if r['count'] != max1: break
                    if r['root'] > int(self.db.person.get('access_level')): continue
                    messbeta += "list = {} \n".format(r['name'])
                    keys.append(["{}".format(r['name']), {"mode": "send3", "to": r['id'], "list": 1, 'signed': signed}])
                if len(keys):
                    send.append([0, "Уточните кому вы хотите отправить сообщение"])
                    send.append([6, keys])
                    return (send, sendadmin, messout, messbeta)

            if int(res[0]['root'])>int(self.db.person.get('access_level')):
                send.append([0,"Вы не имеете право отправлять сообщения данному списку рассылки."])
                return (send, sendadmin, messout, messbeta)
            if signed == 0 or signed == '0':
                send.append([0, "Нельзя отправлять анонимное сообщения списку рассылки."])
                return (send, sendadmin, messout, messbeta)

            messbeta += "to list = {} \n".format(res[0].get('name'))
            send.append([0, "Что вы хотите отправить to '{}'".format(res[0].get('name'))])
            self.db.setMode_person({"mode": "send3", "to": res[0].get('id'), "list": 1, 'signed': signed})
            return (send, sendadmin, messout, messbeta)


        if re.search("^([0-9]{4} ){0,1}([А-Я][а-я]+ ){0,1}[А-Я][а-я]+( [0-9]{4}){0,1}$", messagetext)==None:
            send.append([0,"Неверный формат имени. Правильный формат:"]) #или не найдено такого списка для рассылки
            send.append([0, "/send (год поступления) Имя (Фамилия) (год поступления)"])
            send.append([0, "Примеры: '/send 2014 Александр' или '/send Иванов Антон'"])
            return (send, sendadmin, messout, messbeta)

        persons = {}
        personsres = {}
        names =  re.findall("[А-Я][а-я]+", messagetext)
        years = re.findall("[0-9]{4}", messagetext)
        shouldbethesameyear = False
        # if len(years)==0 and len(names)==1: # можно сделать чтобы человек не мог искать людей только по имени
        #    return ([[0,"Вы ввели слишком мало информации про человека"]], sendadmin, messout, messbeta)

        for name in names:
            res = self.db.get_person_byName(name)
            for r in res:
                personsres[r['id']] = r
                persons.update({r.get('id'): persons.setdefault(r.get('id'), 0) + 1})

        if len(years)==0:
            shouldbethesameyear = True
            year_rate = 0.5
            year = str(self.db.person.get('year_start'))
        else:
            year_rate = 1
            year = years[0]

        messbeta += ("year = {}\n".format(year))

        for pers, rate in persons.items():
            if str(personsres[pers].get('year_start'))==year:
                persons[pers]=rate+year_rate
            elif shouldbethesameyear:
                persons[pers]=0

        persons = sorted([[k, v] for k, v in persons.items()], key=lambda x: x[1], reverse=True)
        if len(persons)==0:
            messbeta +="No such person \n"
            send.append([0,"Такого человека не найдено"])
        elif persons[0][1]==0:
            send.append([0, "Такого человека на вашем курсе не найдено"])
        elif len(persons)==1:
            messbeta += "only person = {} \n".format(personsres[persons[0][0]].get('name'))
            send.append([0,"Что вы хотите отправить to '{} {}'".format(personsres[persons[0][0]].get('name'),personsres[persons[0][0]].get('year_start'))])
            print("personsres {}".format(personsres[persons[0][0]]))
            if str(personsres[persons[0][0]].get('wts'))=='1':
                send.append([0,"Сообщение будет отправлено на почту, поэтому можете указать тему письма написав в первой строчке: [тема письма]. В противном случаи тема письма будет ваше имя."])
            self.db.setMode_person({"mode": "send3", "to": persons[0][0], "list": 0, 'signed':signed})
        else:
            send.append([0,"Уточните кому вы хотите отправить сообщение"])
            keys = []
            max1 = persons[0][1]
            for pers, val in persons[:3]:
                if val!=max1: break
                messbeta += "person = {} \n".format(personsres[persons[0][0]].get('name'))
                keys.append(["{} {}".format(personsres[pers].get('name'),personsres[pers].get('year_start')), {"mode": "send3", "to": pers, "list": 0, 'signed':signed}])
            send.append([6, keys])
        return (send,sendadmin,messout,messbeta)

    def send2(self,dd):
        if self.canwork != 0: return self.canwork
        if dd['mode']!='send3' or ('to' not in dd) or ('list' not in dd) or ('signed' not in dd) or len(dd)!=4: return "Подделка dd"
        self.db.setMode_person(dd)
        if str(dd['list'])=='1':
            lst = self.db.mailingList_get(id=dd['to'])
            return "Что вы хотите отправить to '{}'".format(lst.get('name'))
        else:
            pers = self.db.get_person(idd=dd['to'])
            if str(pers.get('wts'))=='1':
                return "Что вы хотите отправить to '{} {}'? \n Сообщение будет отправлено на почту, поэтому можете указать тему письма написав в первой строчке: [тема письма]".format(pers.get('name'),pers.get('year_start'))
            else:
                return "Что вы хотите отправить to '{} {}'".format(pers.get('name'),pers.get('year_start'))

    def send3(self,mess,messId=0,where=0,mode={},entities=None):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "send3 from {} in {} \n".format(self.db.person['username'],self.chatId)
        if self.db.person_mode.get('mode')!='send3':
            return ([[0,'Невозможно отправить сообщение; не указано однозначно имя.',1]],sendadmin,messout,messbeta)

        messtosend = []
        if type(mess)==str:
            mess = get_bbcode(mess,entities,urled=True)
            title, mess = get_title(mess)
            messtosend.append([0,mess])
            if title and len(title): messtosend.append([7,title])

        if len(mode):
            sendto = mode['to']
            if 'list' in mode:
                islist = True if mode['list']=='1' else False
            else: islist = False
            signed = '1'
        else:
            if 'to' not in self.db.person_mode or \
                'signed' not in self.db.person_mode or \
                'list' not in self.db.person_mode: return ([[0,'Невозможно отправить сообщение; не указано однозначно имя.',1]],sendadmin,messout,messbeta)
            sendto = self.db.person_mode['to']
            signed = self.db.person_mode['signed']
            islist = True if self.db.person_mode['list']=='1' else False

        if str(signed) == '0':
            messtosend.append([0,"(это сообщение анонимно)","sign"])
        elif str(signed) == '1':
            messtosend.append([0,"({} {})".format(self.db.person['name'],self.db.person['year_start']),"sign"])
        else:
            messtosend.append([0,"(signed = {})".format(signed),'sign'])

        messtosend.append([0,"(Вы можете ответить на него используя reply к этому сообщению)",'canreply'])
        if islist:
            lst = self.db.mailingList_get(id=sendto)
            if int(lst['root'])>int(self.db.person.get('access_level')):
                send.append([0,"Странно что вы дошли до этого этапа, однако вы не имеете право отправлять сообщения данному списку рассылки."])
                return (send, sendadmin, messout, messbeta)
            if str(signed) == '0':
                send.append([0,"Странно что вы дошли до этого этапа, запрещено делать анонимную рассылку."])
                return (send, sendadmin, messout, messbeta)

            lst = lst.get('list') # получаем лист из пользователей
            for idd in lst:
                res = self.sendmess(to=idd, send=messtosend,frm=self.db.idd,html=True) # Отправляем каждому
                if res != None:
                    self.db.message_add(frm=self.db.idd, to=int(idd), mess_id=res.message_id, origmess_id=messId, typ=signed, islist=islist)
                    #self.db.tel_message_add(self.db.get_person_telid(self.db.idd), self.db.get_person_telid(int(idd)), res.message_id, messId, signed, islist)
            send.append([0, "{} cообщений успешно отправлены".format(len(lst))])
        else:
            res = self.sendmess(to=sendto,send=messtosend,frm=self.db.idd,html=True)
            #self._print(res)
            send.append([0,"Сообщение успешно отправлено"])
            if res != None:
                self.db.message_add(frm=self.db.idd,to=int(sendto),mess_id=res.message_id,origmess_id=messId,typ=signed, islist=islist)
                #self.db.tel_message_add(self.db.get_person_telid(self.db.idd),self.db.get_person_telid(int(sendto)),res.message_id,messId,signed, islist)
        self.db.person_mode['mode'] = "wassent"
        self.db.setMode_person(self.db.person_mode)
        return (send, sendadmin, messout, messbeta)

    def more(self,mess,messId=0,where=0):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messbeta = "more from {} in {} \n".format(self.db.person['username'],self.chatId)
        if self.db.person_mode["mode"] == "wassent":
            self.db.person_mode["mode"] = "send3"
            self.db.setMode_person(self.db.person_mode)
        else:
            send.append([0,"Эту команду можно использовать после использования других команд. Например, чтобы отправить еще одно сообщение тому же получателю"])
            return send, sendadmin, "", messbeta

    def sendmess(self,to=None, send=[], replyTo=None, frm=None, totel=None, subject=None,html=False,editmessage=False):
        self._print("sendmess: to:{}, send: {}, replyTo: {}".format(to, send,replyTo))
        if type(send)==str:
            send = [(0, send)]
        #     titlematch = re.match("^\[[a-zA-Z0-9а-яА-Я \.\,]+\]",send)
        #     if titlematch:
        #         tiltitle = titlematch.end()
        #         send = [(7,send[1:tiltitle-1]),(0,send[tiltitle:])]
        #     else: send = [(0,send)]
        if type(send)==tuple: send = [send]
        if replyTo=='0': replyTo=None
        mess = ""

        if totel!=None: wts = '0'
        elif to!=None: wts = str(self.db.get_person_param('wts',idd=to))
        else: wts = '-1'

        if str(wts)=='0' or replyTo:
            if totel==None: totel = self.db.get_person_telid(int(to))

            import telebot
            from telebot import types
            bot = telebot.TeleBot(config.token)
            markup = types.ReplyKeyboardRemove()
            for s in send:
                if s[0] == 0:  # -> это просто текст
                    mess += s[1] + "\n"
                elif s[0] == 3:  # -> это картинка или файл // s = [3, [already sent,is photo,path]]
                    msg = bot.send_photo(totel, open(self.BASE_DIR + '/doc/' + s[1], 'rb'),reply_to_message_id=replyTo)
                elif s[0] == 4:
                    msg = bot.send_document(totel, open(self.BASE_DIR + '/doc/' + s[1], 'rb'),reply_to_message_id=replyTo)
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
                elif s[0] == 7:
                    mess = "[{}]\n{}".format(s[1],mess)
            if len(mess):
                if replyTo==None:
                    return bot.send_message(totel, mess,reply_markup=markup)
                elif editmessage:
                    return bot.edit_message_text(chat_id=totel, message_id=replyTo, text=mess, reply_markup=markup)
                else:
                    return bot.send_message(totel, mess,reply_to_message_id=replyTo, reply_markup=markup)

        elif str(wts)=='1':
            smtp = smtplib.SMTP(host=config.email_host, port=config.email_port)
            smtp.starttls()
            smtp.login(config.email_login, config.email_passwd)
            msg = MIMEMultipart()  # create a message
            msg['From'] = config.email_login
            msg['To'] = self.db.get_person_param('email',idd=to)

            if frm!=None:
                frm_person = self.db.get_person_param(['name','year_start'],idd=frm)
                title = "{} {}".format(frm_person[0],frm_person[1])
            else:
                title = "Общий"

            for s in send:
                if s[0] == 0:  # -> это просто текст
                    mess += s[1] + "\n"
                if s[0] == 7:
                    title = "{}. {}".format(s[1], title)

            msg['Subject'] = title
            if html:
                print(mess.replace('\n','<br>'))
                msg.attach(MIMEText(mess.replace('\n','<br>'), 'html'))
            else:
                msg.attach(MIMEText(mess, 'plain'))
            self._print("send email to {}".format(msg['To']))
            self._print(smtp.send_message(msg))
            return None


    def askforhelp(self,mess,messId=0,replyTo=None):
        if self.canwork != 0: return self.canwork
        res = self.sendmess(totel=config.help_chat, send=mess, replyTo=replyTo)
        if res != None:
            self.db.message_add(self.db.idd, 1, mess_id=res.message_id, origmess_id = messId, typ=5)
            #self.db.tel_message_add(self.db.get_person_telid(self.db.idd), config.help_chat, res.message_id, messId, 5)

    def sendtoadmin(self,mess,messId=0,replyTo=None):
        if self.canwork != 0: return self.canwork
        send = []; sendadmin = []; messout = ""; messbeta = "Send message to admin \n"
        if ("/toadmin" in mess):
            if not self.named():
                mess = self.getText(mess, ["/sendtoadmin ","/toadmin "], change=False)
                if (mess.get('mode') == 0): return ([[0, mess.get('error')]], sendadmin, messout, messbeta)  # Если mode=0 => значит неверный формат текста
                messagetext = mess.get('text')  # закинули очищеный текст в отдельную переменную

                send, sendadmin, messout, messbeta = self.send3(messagetext, messId, 1, mode={"to": config.admin_chat})
                return (send, sendadmin, messout, messbeta)
            else:
                send.append([0, "Вы не имеете право отправлять сообщения пока не зарегистрируетесь (/signup)"])
                return (send, sendadmin, messout, messbeta)
        else:
            res = self.sendmess(to=config.admin_chat, send=mess, replyTo=replyTo)
            if res != None:
                self.db.message_add(frm=self.db.idd, to=config.admin_chat, mess_id=res.message_id, origmess_id=messId, typ=5)
                #self.db.tel_message_add(self.db.get_person_telid(self.db.idd), config.admin_chat, res.message_id, messId, 5)

        return True

    def simplesend(self,mess):
        self._print("simplesend")
        # s = smtplib.SMTP(host=config.email_host, port=config.email_port)
        # s.starttls()
        # s.login(config.email_login, config.email_passwd)
        # msg = MIMEMultipart()  # create a message
        # msg['From'] = config.email_login
        # msg['To'] = '4cd87a@gmail.com'
        # msg['Subject'] = "This is TEST"
        # msg.attach(MIMEText("123", 'plain'))
        # s.send_message(msg)
        # s.quit()

        return "123"
        # import telebot
        # bot = telebot.TeleBot(config.token)
        # print("started telebot")
        # bot.send_message(config.admin_chat, mess)
        # print("sent")

    def got_email(self,email):
        self.db.set_person(email=email["from"])
        self.canwork = self.canworkcheck()
        if self.canwork != 0:
            return 0#self.canwork

        retsent = str(self.send(mess=email['text'], title=email['subject']), ismail=1)
        self._print(self.db.person)
        #retsent += str(self.send3())

        return "RET: {}; Your ip = {};".format(retsent,self.db.idd)

    def easyspeak_login(self,username, pin, ip=None):
        if re.match("^[a-zA-Z][a-zA-Z0-9_]+$",username)!=None and re.search("^[a-zA-Z0-9]{4,12}$", pin)!=None:
            res = self.db.easyspeak_iplogs_get(ip=ip, username=username)
            if (not res) or len(res)<3:
                if self.check_pin(username=username,pin=pin):
                    self.db.easyspeak_iplogs_add(ip=ip, username=username,logged=1)
                    file = self.db.easyspeak_file_get(owner=self.db.get_person(username=username).get('id'))
                    if time.time() - file.get('active', 0) < 10 * 60:
                        return file['origname']
                    return True
            else: return False

        self.db.easyspeak_iplogs_add(ip=ip, username=username, logged=0)
        return False

    def easyspeak_sendtext(self, username, pin, text, ip=None):
        if re.match("^[a-zA-Z][a-zA-Z0-9_]+$", username)!= None and re.search("^[a-zA-Z0-9]{4,12}$", pin)!= None:
            res = self.db.easyspeak_iplogs_get(ip=ip, username=username)
            if (not res) or len(res) < 3:
                if self.check_pin(username=username,pin=pin):
                    #if re.match("^[a-zA-Z][a-zA-Z0-9]+$", text)!= None:
                    text = "{}".format(text)
                    if len(text)<100 and text.count('\n')<=5:
                        self.sendmess(to=self.db.get_person(username=username).get('id'),send="{}".format(text))
                    else:
                        halfday = int(time.gmtime().tm_hour / 12)
                        filename = '{}'.format(round(time.time()))
                        with open(self.BASE_DIR + '/doc/{}/{}.txt'.format(halfday,filename), 'w') as new_file:
                            new_file.write(text)
                        self.sendmess(to=self.db.get_person(username=username).get('id'), send=[[4,'{}/{}.txt'.format(halfday,filename)]])
                    return True
            else: return False

        self.db.easyspeak_iplogs_add(ip=ip, username=username, logged=0)
        return False

    def easyspeak_file_add(self,files):
        self._print("easyspeak_file_add: files:{}".format(files))
        send = []; sendadmin = []; messout = ""; messbeta = ""
        if len(files[1])!=1:
            self._print("не правильный размер")
            return ([[0, "Можно сохранять только один файл за раз"]],sendadmin, messout, messbeta)

        self._print(files[1][0])

        file_name, path, extension, file_name_orig = files[1][0]
        file_id = self.db.easyspeak_file_add(name=file_name,owner=self.db.idd,path=path,extension=extension, name_orig = file_name_orig)

        send.append([0, "Файл сохранен и будет хранится 12 часов. Вы можете скачать файл ftf.kh.ua"])
        send.append([6, [['Активировать файл',{"mode": "easyfile", "id": file_id,"action":1}],
                         ['Дезактивировать файл', {"mode": "easyfile", "id": file_id,"action":0}]
                         ]])

        return (send, sendadmin, messout, messbeta)

    def easyspeak_file_update(self, dd, message_id=0):
        self._print("easyspeak_file_update: dd:{}".format(dd))
        send = []
        if dd['mode']!='easyfile' or 'id' not in dd or 'action' not in dd: return "Фактчекинг провалился"
        file = self.db.easyspeak_file_get(idd=dd['id'])
        if file.get('owner',0)!=self.db.idd: return "У вас нет доступа к этому файлу"

        end_time = time.localtime(time.time() + 60 * 10)

        if dd['action']=='0':
            if file.get('active', 0)==0: return False
            self.db.easyspeak_file_update(idd=dd['id'],active=0,message_id=message_id)
            send.append([0, "Файл деактивирован"])

        elif dd['action']=='1':

            self.db.easyspeak_file_update(idd=dd['id'],active=round(time.time()),message_id=message_id)
            if time.time() - file.get('active', 0) < 1 ^ 60: return False
            send.append([0,
                         "Файл будет активен на единоразовое скачивание до {}:{}. \n Вы можете скачать файл на ftf.kh.ua".format(
                             end_time.tm_hour, '{:2.0f}'.format(end_time.tm_min).replace(' ','0'))])


        send.append([6, [['Активировать файл', {"mode": "easyfile", "id": dd['id'], "action": 1}],
                         ['Деактивировать файл', {"mode": "easyfile", "id": dd['id'], "action": 0}]
                         ]])

        return send

    def easyspeak_file_get(self, username, pin,ip=None):
        if re.match("^[a-zA-Z][a-zA-Z0-9_]+$", username)!= None and re.search("^[a-zA-Z0-9]{4,12}$", pin)!= None:
            res = self.db.easyspeak_iplogs_get(ip=ip, username=username)
            if (not res) or len(res) < 3:
                if self.check_pin(username=username,pin=pin):
                    pers_id = self.db.get_person(username=username).get('id')
                    file = self.db.easyspeak_file_get(owner=pers_id)
                    if time.time() - file.get('active', 0) < 10*60:
                        with open(self.BASE_DIR+'/doc/{}'.format(file.get('path')), 'rb') as fin:
                            self._print("file to send: {}".format(file))
                            data = io.BytesIO(fin.read())

                        self.db.easyspeak_file_update(idd=file.get('id'), active=0)
                        send = []
                        send.append([0, "Файл деактивирован"])
                        send.append([6, [['Активировать файл', {"mode": "easyfile", "id": file['id'], "action": 1}],
                                         ['Деактивировать файл', {"mode": "easyfile", "id": file['id'], "action": 0}]
                                         ]])
                        self.sendmess(to=pers_id, send=send, replyTo=file.get('message_id'),editmessage=True)
                        return (file.get('origname'),data)
                    return False
            else: return False

        self.db.easyspeak_iplogs_add(ip=ip, username=username, logged=0)
        return False

    def check_password(self, idd=None, telid=None, username=None, password=None):
        return self.db.check_password(idd=idd, telid=telid, username=username, password=password)

    def check_pin(self, idd=None, telid=None, username=None, pin=None):
        if pin==None: return False
        return self.db.check_pin(idd=idd, telid=telid, username=username, pin=pin)

    def reset_password(self,idd=None,username=None,cod=None,password=None):
        if idd==None: idd = self.db.get_person(username=username)['id']
        if idd!=0 and cod==None:
            data_id = self.db.tempdata_add('0')
            data_hsh = funcs.keyGenerator(data_id,length=8)
            token = funcs.passGenerator(24-len(data_hsh)).replace(':','')
            self.db.tempdata_update(idd=data_id, data="{}:{}{}".format(idd, data_hsh, token))
            self.sendmess(to=idd, send="[Восстановления пароля]Ссылка на восстановление пароля: ftf.kh.ua/login?cod={}{}".format(data_hsh, token))
            return 0

        if idd!=0 and cod!=None and password!=None:
            data_id = funcs.keyDecoder(cod[:8],length=8)
            self._print('data_id = {}'.format(data_id))
            temp = self.db.tempdata_get(data_id)
            token = temp.get('data')
            if token==None: return [(0,'Не верный код (1)')]

            tokens = token.split(':')
            if len(tokens)!=2: return [(0,'Не верный код (2)')]
            if tokens[0]!=str(idd): return [(0,'Не верный код (3)')]
            if tokens[1]!=cod: return [(0,'Не верный код (4)')]

            if round(time.time())-int(temp['timestamp'])>3600: return [(0,'Код восстановления устарел')]

            if password == None: return [(0,'Пароль не введен')]

            password = funcs.passwordHash(password)
            if password.get("bon") == False:
                return [(0, password.get('error'))]
            password = password['hash']
            self.db.update_person_info(idd=idd, password=password)
            self.db.tempdata_del(data_id)

            return idd

        return 0


def arraytotest(arr,beginning="",separate="; "):
    messout = beginning
    for a in arr: messout += a + separate
    messout += "."
    return messout

def get_bbcode(message_text, entities, urled=False):
    if message_text is None: return None
    if entities is None: return message_text

    last_offset = 0
    bbcode_text = ''
    for entity in entities:
        text = message_text[int(entity.offset):int(entity.offset)+int(entity.length)]
        if entity.type == 'text_link':
            insert = '<a href="{}">{}</a>'.format(entity.url, text)
        elif entity.type == 'mention':
            insert = '<a href="https://t.me/{0}">{1}</a>'.format(text.strip('@'),text)
        elif entity.type == 'url' and urled:
            insert = '<a href="{0}">{0}</a>'.format(text)
        elif entity.type == 'bold':
            insert = '<b>' + text + '</b>'
        elif entity.type == 'italic':
            insert = '<i>' + text + '</i>'
        elif entity.type == 'underline':
            insert = '<u>' + text + '</u>'
        elif entity.type == 'strikethrough':
            insert = '<s>' + text + '</s>'
        elif entity.type == 'code':
            insert = '<code>' + text + '</code>'
        elif entity.type == 'pre':
            insert = '<pre>' + text + '</pre>'
        else:
            insert = text

        bbcode_text += message_text[int(last_offset):int(entity.offset)] + insert
        last_offset = int(entity.offset) + int(entity.length)

    bbcode_text += message_text[last_offset:]
    return bbcode_text

def get_title(message_text):
    span = re.search("^\[.*?\]", message_text)
    if span:
        span = span.span()
        title = message_text[span[0]+1:span[1]-1]
        message_text = message_text[span[1]+1:]
        if message_text.startswith('\n'): message_text = message_text[1:]
        return title, message_text
    return '', message_text

def copyfile(path_in, path_out):
    shutil.copyfile(path_in, path_out)
    # f_src = open(path_in, 'rb')
    # with open(path_out, 'wb') as new_file:
    #     new_file.write(f_src)