# -*- coding: utf-8 -*-
import os.path
import random
import time
from datetime import datetime
from . import funcs, config
import mysql.connector
from werkzeug.security import check_password_hash

class SQLighter:

    def __init__(self, idd = None,telid = None, username=None, chatid = 0, logger=None):
        self.logger = logger
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.connection = mysql.connector.connect(
            host=config.mysql_host,
            port=config.mysql_port,
            user=config.mysql_user,
            passwd=config.mysql_passwd,
            database="ftfbot"
        )
        self.cursor = self.connection.cursor()
        self.chatidtel = chatid
        self.chatid = 0
        self.set_person(idd = idd, telid = telid, username=username)
        self.chat = self.get_person(telid=chatid)
        self.chatid = self.idd if self.chat.get('id', 0) == 0 else self.chat.get('id')
        #print(self.person)
        #print("your id {}".format(self.idd))

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

    def close(self):
        self.cursor.close()
        self.connection.close()

    '''def select_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute("SELECT * FROM `ftfbot`").fetchall()'''

    def getFromTable(self, table, field, like = ""):
        field_text = ""
        for f in field:
            field_text += "`" + str(f) + "`,"
        field_text = field_text[0:-1]
        table = '`' + str(table) + '`'
        #with self.connection:
        self._print("SELECT " + field_text + " FROM " +  str(table) + " " + like,'w')
        self.cursor.execute("SELECT " + field_text + " FROM " +  str(table) + " " + like)
        res = self.cursor.fetchall()

        self.connection.commit()

        if len(res):
            ret = []
            for j in range(len(res)):
                dic = {}
                for i,f in enumerate(field):
                    dic.update({f:res[j][i]})
                ret.append(dic)
            return ret
        else: return []

    def addToTable(self, table, field, whattoad):
        if len(field)!=len(whattoad): raise ValueError("field and whattoad aren't the same leng in addToTable")
        field_text = "("
        add_text = "("
        for i in range(len(field)):
            #print(field[i])
            #print(whattoad[i])
            field_text += "`" + str(field[i]) + "`,"
            #if type(whattoad[i]) == int or type(whattoad[i]) == float: add_text += "" + str(whattoad[i]) + ","
            add_text += "'" + str(whattoad[i]) + "',"

        field_text = field_text[0:-1] + ")"
        add_text = add_text[0:-1] + ")"
        table = '`' + str(table) + '`'

        #with self.connection:
        self._print("INSERT INTO " + table + field_text + " VALUES " + add_text,'w')
        self.cursor.execute("INSERT INTO " + table + field_text + " VALUES " + add_text)
        self.cursor.execute("SELECT max(id) from {}".format(table))
        res = self.cursor.fetchall()

        self.connection.commit()

        return res[0][0]

    def changeTable(self,table, field, whattoad, like):
        if len(field)!=len(whattoad): raise ValueError("field and whattoad aren't the same leng in changeTable")
        if len(field)==0: return True

        field_text = ""
        for i in range(len(field)):
            field_text += "`" + str(field[i]) + "`" + "=" + "'" + str(whattoad[i]) + "',"
        field_text = field_text[0:-1]
        table = '`' + str(table) + '`'

        #with self.connection:
        self._print("UPDATE " + table + " SET " + field_text  + " " + like,'w')
        self.cursor.execute("UPDATE " + table + " SET " + field_text  + " " + like)

        self.connection.commit()

        return True

    def deleteFromTable(self, table, like):
        table = '`' + str(table) + '`'
        #with self.connection:
        self._print("DELETE FROM " + table + " " + like,'w')
        self.cursor.execute("DELETE FROM " + table + " " + like)

        self.connection.commit()

        return True

    def get_command(self, phase):
        return self.getFromTable('ftfbot',['id','command','text','search','function','args','image','year','sem','makeup',
                                           'descr','added','edited','editedBy','root','accuracy','link'],
                                 "WHERE LOWER(`command`) LIKE '%" + phase + "%'")

    def get_command_byID(self, idd):
        res = self.getFromTable('ftfbot',
                                 ['id','command', 'text', 'search', 'function', 'args', 'image', 'year', 'sem', 'makeup',
                                  'descr', 'added','edited', 'editedBy', 'root', 'accuracy','link'],
                                 "WHERE `id`=" + str(idd))
        if len(res): return res[0]
        return 0

    def add_command_simple(self, question, dic={}, text="",image="",link=0):
        ext = self.getFromTable('ftfbot',['id'], "WHERE LOWER(`command`)='" + question + "'")
        if len(ext)==0:
            if 'text' in dic: text = dic.get('text')
            if 'image' in dic: image = dic.get('image')
            if 'link' in dic: link = dic.get('link')

            return self.addToTable('ftfbot',['command','text','image','link','added','edited','editedBy'],[question,text,image,link,time.time(),time.time(),self.idd])
        return ext

    def edit_command_simple_byID(self, idd, dic={}, image="", text="",link=0):
        if 'text' in dic: text = dic.get('text')
        if 'image' in dic: image = dic.get('image')
        if 'link' in dic: link = dic.get('link')
        self.changeTable('ftfbot', ['text','image','link','edited','editedBy'], [text,image,link,time.time(),self.idd], "WHERE `id`=" + str(idd))

    def count_rows(self, phase):
        res = self.getFromTable('ftfbot',['command'], "WHERE LOWER(`command`) LIKE '%" + str(phase) + "%'")
        return len(res)

    def randomfunc10(self,mm,qq):
        with self.connection:
            res = self.cursor.execute("SELECT * FROM `ftfbot`").fetchall()
            random.shuffle(res)
            mess = ""
            for i,r in enumerate(res[:10]):
                mess += str(i+1) + " : " + r[0] + '\n'
            return mess

    def add_question(self,quest,knownques,id_pers,id_msg,accur,typ='text',**kwargs):
        self.addToTable('questions', ['id_pers','id_msg','time','quest','knownQuest','type','accuracy'], [id_pers,id_msg,time.time(),quest,knownques,typ,accur])

    def get_question(self, id_pers=0):
        if (id_pers==0): return [] #id_pers = self.idd
        return self.getFromTable('questions',['id_pers','id_msg','time','quest','knownQuest','type','accuracy'], "WHERE `id_pers`=" + str(id_pers) + " ORDER BY `time` DESC limit 0, 3")

    def get_noanwed(self, phase): #не знаю нужо ли
        return 0
        """ Получаем все вопросы """
        with self.connection:
            #print("SELECT * FROM `questions` WHERE `id`="+str(ms.chat.id)+" ORDER BY `time` DESC")
            arr = self.cursor.execute("SELECT * FROM `questions` WHERE `got`>=1 AND  `question` LIKE '%" + phase + "%' ORDER BY `time` DESC").fetchall()
            if len(arr):
                return arr
            else:
                return []

    def add_person_byTL(self,idd,username,telname,typ=0,beta=0,acc_lev=1):
        self.addToTable('people',['telid','username','telname','beta','access_level','mode','type'],
                        [idd,username,telname,beta,acc_lev,0,typ])


    def add_person_info(self,info,id_pers = 0):
        if (id_pers == 0): id_pers = self.idd
        fields = []; whattoads = []

        for key in info.keys():
            if key in ['name','email','year_start','pin','password','token']:
                fields.append(key)
                whattoads.append(info[key])
        return self.changeTable('people',fields,whattoads,"WHERE `id`="+str(id_pers))

    def update_person_info(self,idd, name=None, patronymic=None, email=None, year_start=None, wts = None, password=None, pin=None, telname=None, ttype=None, beta=None,access_level=None):
        fields = []; whattoads = []

        if name!=None:
            fields.append('name')
            whattoads.append(name)

        if patronymic!=None:
            fields.append('patronymic')
            whattoads.append(patronymic)

        if email!=None:
            fields.append('email')
            whattoads.append(email)

        if year_start!=None:
            fields.append('year_start')
            whattoads.append(year_start)

        if wts!=None:
            fields.append('wts')
            whattoads.append(wts)

        if password!=None:
            fields.append('password')
            whattoads.append(password)

        if pin!=None:
            fields.append('pin')
            whattoads.append(pin)

        if telname!=None and telname=='':
            fields.append('telname')
            whattoads.append('')
            fields.append('telid')
            whattoads.append(0)

        if ttype!=None:
            fields.append('type')
            whattoads.append(ttype)

        if beta!=None:
            fields.append('beta')
            whattoads.append(beta)

        if access_level!=None:
            fields.append('access_level')
            whattoads.append(access_level)

        return self.changeTable('people', fields, whattoads, "WHERE `id`=" + str(idd))

    def set_person(self, idd=None,telid=None,email=None,username=None,password=None):
        person = self.get_person(idd=idd, telid=telid, email=email, username=username)
        if password!=None:
            check = self.check_password(person['id'],password)
            if not check: return False

        self.person = person
        self.idd = self.person['id']
        if self.chatid == 0: self.chatid = self.idd

        try:
            tt = self.person.get('mode')
            self._print("tt = {}".format(tt),'i')
            if type(tt)==int or len(tt)<3:
                self.person_mode = {"mode":tt}
            else:
                self.person_mode = funcs.strtojson(tt)

        except Exception as e:
            self._print("Cannot get right json in person_mode (id={})".format(idd),'e')
            self.person_mode = {"mode":0}

        return True


    def get_person(self, idd=None,telid=None,email=None,username=None):
        res = []
        print(idd,telid,email,username)
        if telid != None:
            telid = str(telid).replace('"', '').replace("'", "").replace('`', '').replace(' ', '')
            res = self.getFromTable('people',
                                    ['id', 'telid' , 'username', 'telname', 'year_start', 'beta', 'access_level', 'mode', 'type',
                                     'name', 'surname', 'patronymic', 'email', 'wts', 'token','newsletters'], "WHERE `telid`={}".format(telid))
        if username != None:
            username = str(username).replace('"','').replace("'","").replace('`','').replace(' ', '')
            res = self.getFromTable('people',
                                    ['id', 'telid' , 'username', 'telname', 'year_start', 'beta', 'access_level', 'mode', 'type',
                                     'name', 'surname', 'patronymic', 'email', 'wts', 'token','newsletters'], "WHERE `username` LIKE '{}'".format(username))

        if email != None:
            email = str(email).replace('"','').replace("'","").replace('`','').replace(' ', '')
            res = self.getFromTable('people',
                                    ['id', 'telid' , 'username', 'telname', 'year_start', 'beta', 'access_level', 'mode', 'type',
                                     'name', 'surname', 'patronymic', 'email', 'wts', 'token','newsletters'], "WHERE `email`='{}'".format(email))

        if idd!=None:
            idd = str(idd).replace('"', '').replace("'", "").replace('`', '').replace(' ', '')
            res =  self.getFromTable('people',
                                     ['id', 'telid','username','telname','year_start','beta','access_level','mode','type',
                                      'name','surname', 'patronymic', 'email','wts','token','newsletters'],"WHERE `id`={}".format(idd))

        if len(res): return res[0]
        else: return self.getFromTable('people',
                     ['id', 'telid', 'username', 'telname', 'year_start', 'beta', 'access_level', 'mode',
                      'type', 'name', 'surname', 'patronymic', 'email', 'wts', 'token', 'newsletters'], "WHERE `id`=0")[0]


    def get_person_telid(self,idd=None):
        if idd==None or idd==self.idd: return self.person['telid']
        return self.get_person(idd=idd)['telid']

    def get_person_param(self,param,idd=None):
        if idd==None or idd==self.idd:
            if type(param)==str:
                return self.person[param]
            else:
                return [self.person[p] for p in param]
        pers = self.get_person(idd=idd)
        self._print("pers = {}".format(pers),'i')
        if type(param) == str:
            return pers[param]
        else:
            return [pers[p] for p in param]

    def get_person_any_param(self,param,idd):
        if type(param)==tuple or type(param)==list:
            return [self.get_person_param(p,idd) for p in param]

        if idd == None: idd = self.idd

        idd = str(idd).replace('"', '').replace("'", "").replace('`', '').replace(' ', '')
        res = self.getFromTable('people', [param], "WHERE `id`={}".format(idd))
        if len(res): return res[0][param]
        return False

    def check_password(self,idd=None,telid=None,email=None,username=None,password=None):
        if password==None: return False
        if idd!=None:
            if int(idd)==0: return False
        else:
            person = self.get_person(idd=idd, telid=telid, email=email, username=username)
            idd = person['id']
            if int(idd) == 0: return False

        truepass = self.get_person_any_param('password',idd=int(idd))

        if check_password_hash(truepass,str(password)):
            return idd
        else: return False

    def check_pin(self,idd=None, telid=None, email=None, username=None, pin=None):
        if (idd != None and int(idd) == 0) or pin == None: return False
        if idd != None:
            truepass = self.get_person_any_param('pin', idd=idd)
        else:
            person = self.get_person(idd=idd, telid=telid, email=email, username=username)
            truepass = self.get_person_any_param('pin', idd=person['id'])

        return check_password_hash(truepass, str(pin))

    def get_person_byName(self,name):
        return self.getFromTable('people',
                          ['id', 'year_start','name', 'surname', 'wts'],
                          "WHERE LOWER(`name`) LIKE '%" + str(name) + "%'")
    def get_year(self):
        if self.person.has_key("year_start"):
            if self.person.get('year_start')==0: return 0
            ret = datetime.now().timetuple().tm_year - self.person.get('year_start')
            if (datetime.now().timetuple().tm_mon > 6): ret+=1
            return ret
        else: return 0

    def setStartYear_person(self,idd,year=0):
        self.changeTable('people',['year_start'],[year],"WHERE `id`=" + str(idd))

    def setBeta_person(self,id_pers,beta=0):
        if (id_pers == 0): id_pers = self.idd
        self.changeTable('people',['beta'],[beta],"WHERE `id`=" + str(id_pers))

    def setMode_person(self,mode=0,id_pers=0):
        if (id_pers == 0): id_pers = self.idd
        self._print("id = {} in setmode {}".format(id_pers,mode),'i')
        self.person_mode = mode if type(mode)==dict else {"mode": str(mode)}
        if type(mode)==dict:
            mode = funcs.jsontostr(mode)
        else: mode = str(mode)
        self.changeTable('people',['mode'],[mode],"WHERE `id`=" + str(id_pers))
    
    def setLevel_person(self,idd,level=0):
        self.changeTable('people',['level'],[level],"WHERE `id`=" + str(idd))
        
    def add_file(self,name, idd,typ = None):
        if typ == None: typ = self.detType_file(name)
        self.addToTable('file_tel_ids',['file_name','id_tel','type'],[name,idd,typ])
    
    def get_file(self,names,typ = None):
        if len(names) > 3 and names[0] == '[' and names[-1] == ']':
            names = eval(names)
        else: names = [names]

        files = []
        for name in names:
            arr = self.getFromTable('file_tel_ids',['id_tel','type'],"WHERE `file_name`='" + name + "'")
            if len(arr):
                file = {'sent':1,'isphoto': arr[0].get('type'),'hash':arr[0].get('id_tel'),'path':name}
            elif typ==None:
                file = {'sent':0,'isphoto': self.detType_file(name),'path':name}
            else:
                file = {'sent': 0, 'isphoto': typ, 'path': name}
            files.append(file)
        return files
    
    def detType_file(self,name):
        ame = name[name.rfind('.')+1:]
        if (ame =="bmp" or ame =="jpeg" or ame =="jpg" or ame =="png"): return 1
        else: return 0

    def tempdata_add(self,data):
        res = self.addToTable('tempdata', ['data', 'timestamp'], [data, round(time.time())])
        return res

    def tempdata_get(self,idd):
        res = self.getFromTable('tempdata', ['data','timestamp'],"WHERE `id`=" + str(idd))
        if len(res):
            return res[0]
        else: return {'data':None}

    def tempdata_update(self,idd,data):
        res = self.changeTable('tempdata', ['data','timestamp'],[data,round(time.time())],"WHERE `id`=" + str(idd))
        return res

    def tempdata_del(self,idd):
        self.deleteFromTable('tempdata', "WHERE `id`=" + str(idd))

    def tel_message_add(self,frm,to,messid,messorigid,typ,islist=0):
        return self.addToTable('tel_messages', ['from','to','mess','mess_orig','type','islist','timestamp'], [frm,to,messid,messorigid,typ,islist,round(time.time())])

    def tel_message_get(self,messid,to=None):
        if to==None: to = self.chatid
        res =self.getFromTable('tel_messages', ['from','mess_orig','type'],"WHERE `to`={} AND `mess`={}".format(to,messid))
        if len(res):
            return res[0]
        else:
            return False

    def nicknames_del(self,idd):
        self.deleteFromTable('nicknames', "WHERE `id`=" + str(idd))

    def nicknames_add(self,person_id,nickname,active=1):
        return self.addToTable('nicknames', ['person_id','nickname','active','timestamp'], [person_id,nickname,active,round(time.time())])

    def nicknames_update(self,idd,nickname,active=1):
        return self.changeTable('nicknames', ['nickname','active','timestamp'],[nickname,active,round(time.time())],"WHERE `id`={}".format(idd))

    def nicknames_get(self,idd=None,person_id=None, nickname=None):
        cond = None
        if idd!=None: cond = "WHERE `id`={}".format(idd)
        if person_id != None: cond = "WHERE `person_id`={}".format(person_id)
        if nickname != None: cond = "WHERE `nickname`='{}'".format(nickname)
        if cond==None: return False

        res = self.getFromTable('nicknames', ['person_id','nickname','active','timestamp'], cond)
        if len(res):
            if idd!=None: return res[0]
            if person_id!=None: return res
            if nickname!=None and len(res)==1: return res[0]
            return False
        else:
            return False
    def easyspeak_file_del(self,idd):
        self.deleteFromTable('personal_files', "WHERE `id`=" + str(idd))

    def easyspeak_file_add(self,name, owner, path=None,active=0,extension='',name_orig=None,message_id=0):
        if path==None: path=name
        if name_orig==None: name_orig=name
        return self.addToTable('personal_files', ['name','origname','owner','path','active','extension','message_id','timestamp'], [name,name_orig,owner,path,active,extension,message_id,round(time.time())])

    def easyspeak_file_update(self,idd,active=0,message_id=0):
        if message_id==0:
            return self.changeTable('personal_files', ['active'],[active],"WHERE `id`={}".format(idd))
        return self.changeTable('personal_files', ['active','message_id'],[active, message_id],"WHERE `id`={}".format(idd))

    def easyspeak_file_get(self,idd=None,owner=None):
        if idd!=None:
            cond = "WHERE `id`={}".format(idd)
        elif owner!=None:
            cond = "WHERE `owner`='{}' ORDER BY active DESC LIMIT 1".format(owner)
        else: return False

        res = self.getFromTable('personal_files', ['id', 'name','origname','owner','path','active','extension','message_id','timestamp'], cond)
        if len(res):
            return res[0]
        else:
            return False

    def easyspeak_iplogs_add(self,ip,username,logged=0):
        if ip==None:return 0
        return self.addToTable('easyspeak_iplogs', ['ip','username','logged','timestamp'], [ip,username,logged,round(time.time())])


    def easyspeak_iplogs_get(self,ip,username,logged=0,since=60*60):
        cond = "WHERE `ip`='{}' AND `username`='{}' AND `logged`={} AND 'timestamp'>'{}' ORDER BY `timestamp`".format(ip,username,logged,round(time.time()-since))

        res = self.getFromTable('easyspeak_iplogs', ['ip','username','logged','timestamp'], cond)
        if len(res):
            return res
        else:
            return False



    def message_add(self,frm,to,global_thread=None,thread=None,mess_id=0,mess_test='',origmess_id=0,origmess_text='',title='',typ=0,islist=0):
        if thread==None:
            thread = self.message_get(frm=frm,to=to)
            thread = 0 if thread==False else int(thread['thread']) + 1
        if thread<5:
            self.deleteFromTable('messages',"WHERE `from`={} AND `to`={} AND `thread`<{}".format(frm,to,thread-2))
        if global_thread==None:
            global_thread = int(self.message_get_global_thread()) + 1

        return self.addToTable('messages',
                    ['from', 'to', 'global_thread', 'thread', 'mess_id', 'mess_test', 'origmess_id', 'origmess_text',
                     'title', 'type', 'islist', 'timestamp'],
                    [frm, to, global_thread, thread, mess_id, mess_test, origmess_id, origmess_text, title, typ, islist, round(time.time())])

    def message_get(self,frm=None,to=None,mess_id=None,thread=None, global_thread=None):
        res = []
        if to!=None and mess_id!=None and frm==None:
            res = self.getFromTable('messages',
                                    ['from', 'to', 'global_thread', 'thread', 'mess_id', 'mess_test', 'origmess_id', 'origmess_text',
                                     'title', 'type', 'islist', 'timestamp'],
                                    "WHERE `to`={} AND `mess_id`={} ORDER BY timestamp DESC LIMIT 1".format(
                                        to, mess_id))
        if frm!=None and to!=None:
            if global_thread!=None:
                res = self.getFromTable('messages',
                                        ['from', 'to', 'global_thread', 'thread', 'mess_id', 'mess_test', 'origmess_id', 'origmess_text',
                                         'title', 'type', 'islist', 'timestamp'],
                                        "WHERE `from`={} AND `to`={} AND `global_thread`={} ORDER BY timestamp DESC LIMIT 1".format(
                                            frm, to, global_thread))
            if thread!=None:
                res = self.getFromTable('messages',
                                        ['from', 'to', 'global_thread', 'thread', 'mess_id', 'mess_test', 'origmess_id', 'origmess_text',
                                         'title', 'type', 'islist', 'timestamp'],
                                        "WHERE `from`={} AND `to`={} AND `thread`={} ORDER BY timestamp DESC LIMIT 1".format(
                                            frm, to, thread))
            elif mess_id!=None:
                res = self.getFromTable('messages',
                                        ['from', 'to', 'global_thread', 'thread', 'mess_id', 'mess_test', 'origmess_id', 'origmess_text',
                                         'title', 'type', 'islist', 'timestamp'],
                                        "WHERE `from`={} AND `to`={} AND `mess_id`={} ORDER BY timestamp DESC LIMIT 1".format(
                                            frm, to, mess_id))
            else:
                res = self.getFromTable('messages',
                                        ['from', 'to', 'global_thread', 'thread', 'mess_id', 'mess_test', 'origmess_id', 'origmess_text',
                                         'title', 'type', 'islist', 'timestamp'],
                                        "WHERE `from`={} AND `to`={} ORDER BY timestamp DESC LIMIT 1".format(frm, to))
        if len(res):
            return res[0]
        else:
            return False

    def message_get_global_thread(self):
        res = self.getFromTable('messages', ['global_thread'], "ORDER BY global_thread DESC LIMIT 1")
        if len(res):
            return res[0].get('global_thread', 0)
        else:
            return 0

    def mailingList_get(self,id=None,name=None,full=False):
        if id!=None:
            res = self.getFromTable('mailing_list',['id','name','list','updated','updatedBy','root','timestamp'],"WHERE `id`={}".format(id))
            if len(res):
                res[0]['list'] = str(res[0]['list']).split(',')
                res[0]['count'] = 0
                return res[0]
            return False
        if name!=None:
            if full:
                res = self.getFromTable('mailing_list', ['id', 'name', 'list', 'updated', 'updatedBy','root','timestamp'],"WHERE `name` LIKE '{}'".format(name))
                for r in res:
                    r['list'] = str(r['list']).split(',')
                    r['count'] = 0
                return res
            else:
                names = name.lower().split(' ')
                res_list = {}
                res_counter = {}
                for n in names:
                    res = self.getFromTable('mailing_list',['id','name','list','updated','updatedBy','root','timestamp'],"WHERE `name` LIKE '%{}%'".format(n))
                    for r in res:
                        r['list'] = str(r['list']).split(',')
                        r['count'] = 0
                        if not r['id'] in res_counter:
                            res_list[r['id']] = r
                        res_counter[r['id']] = res_counter.setdefault(r['id'],0)+1

                res_counter = sorted([[k, v] for k, v in res_counter.items()], key=lambda x: x[1], reverse=True)
                res_return = []
                for i in range(min(len(res_counter),5)):
                    if res_counter[i][1]!=res_counter[0][1]: break
                    res = res_list[res_counter[i][0]]
                    res['count'] = res_counter[i][1]
                    res_return.append(res)
                return res_return
        return []

    def mailingList_addPerson(self,id=None,name=None,person=None):
        com = self.mailingList_get(id,name)
        if len(com)!=1:
            self._print('mailingList_addPerson. Command is not unique','e')
            return False
        return self.changeTable('mailing_list',['list','timestamp'],["{},{}".format(com[0]['list'],person),round(time.time())],"WHERE `id`={}".format(com[0]['id']))

    def mailingList_setList(self,id=None,name=None,lst=None):
        com = self.mailingList_get(id,name)
        if len(com)!=1:
            self._print('mailingList_setList. Command is not unique','e')
            return False
        if type(lst)==list:
            lst = [str(l) for l in lst]
            lst = ','.join(lst)
        elif type(lst)!=str:
            return False
        return self.changeTable('mailing_list',['list','updated','updatedBy'],["{}".format(lst),round(time.time()),self.idd],"WHERE `id`={}".format(com[0]['id']))


    def newsletters_add_person(self,idd_newsletter,idd_person):
        newsletter = self.newsletters_get(idd=idd_newsletter,retliststr=True)
        newsletters = str(self.person['newsletters']).split(',')
        if str(idd_newsletter) not in newsletters:
            if len(str(self.person['newsletters'])):
                lst2 = "{},{}".format(self.person['newsletters'], idd_newsletter)
            else:
                lst2 = str(idd_newsletter)
            self.changeTable('people', ['newsletters'], ["{}".format(lst2)], "WHERE `id`={}".format(self.idd))
        lst = str(newsletter['list']).split(',')
        if str(idd_person) not in lst:
            if len(newsletter['list']):
                lst1 = "{},{}".format(newsletter['list'], idd_person)
            else:
                lst1 = str(idd_person)
            self.changeTable('newsletters', ['list', 'updated', 'updatedBy'],
                             ["{}".format(lst1), round(time.time()), self.idd], "WHERE `id`={}".format(idd_newsletter))
        return 0

    def newsletters_remove_person(self,idd_newsletter,idd_person):
        newsletter = self.newsletters_get(idd=idd_newsletter,retlist=True)
        lst = newsletter['list']
        if len(lst) and str(idd_person) in lst:
            lst.remove(str(idd_person))
            lst1 = ','.join(lst)

            self.changeTable('newsletters', ['list', 'updated', 'updatedBy'],
                             ["{}".format(lst1), round(time.time()), self.idd], "WHERE `id`={}".format(idd_newsletter))

        newsletters = str(self.person['newsletters']).split(',')
        if len(newsletters) and str(idd_newsletter) in newsletters:
            newsletters.remove(str(idd_newsletter))
            lst2 = ','.join(newsletters)

            self.changeTable('people',['newsletters'], ["{}".format(lst2)], "WHERE `id`={}".format(self.idd))

    def newsletters_get(self,idd=None,name=None,telidd=None,full=True,retlist=True,retliststr=False):
        if idd!=None:
            res = self.getFromTable('newsletters',['id','name','list','original_tel','updated','updatedBy','root','timestamp'],"WHERE `id`={}".format(idd))
            if len(res):
                if retliststr:
                    res[0]['list'] = str(res[0]['list'])
                elif retlist:
                    res[0]['list'] = str(res[0]['list']).split(',')
                else: res[0]['list'] = []
                res[0]['count'] = 0
                return res[0]
            return False
        if telidd!=None:
            res = self.getFromTable('newsletters',['id','name','list','original_tel','updated','updatedBy','root','timestamp'],"WHERE `original_tel`={}".format(telidd))
            if len(res):
                if retliststr:
                    res[0]['list'] = str(res[0]['list'])
                elif retlist:
                    res[0]['list'] = str(res[0]['list']).split(',')
                else: res[0]['list'] = []
                res[0]['count'] = 0
                return res[0]
            return False
        if name!=None:
            if full:
                res = self.getFromTable('newsletters', ['id','name','list','original_tel','updated','updatedBy','root','timestamp'],"WHERE `name` LIKE '{}'".format(name))
                for r in res:
                    if retlist:
                        r['list'] = str(r['list']).split(',')
                    else: r['list'] = []
                    r['count'] = 0
                return res
            else:
                names = name.lower().split(' ')
                res_list = {}
                res_counter = {}
                for n in names:
                    res = self.getFromTable('newsletters',['id','name','list','original_tel','updated','updatedBy','root','timestamp'],"WHERE `name` LIKE '%{}%'".format(n))
                    for r in res:
                        if retlist:
                            r['list'] = str(r['list']).split(',')
                        else: r['list'] = []
                        r['count'] = 0
                        if not r['id'] in res_counter:
                            res_list[r['id']] = r
                        res_counter[r['id']] = res_counter.setdefault(r['id'],0)+1
                res_counter = sorted([[k, v] for k, v in res_counter.items()], key=lambda x: x[1], reverse=True)
                res_return = []
                for i in range(min(len(res_counter),5)):
                    if res_counter[i][1]!=res_counter[0][1]: break
                    res = res_list[res_counter[i][0]]
                    res['count'] = res_counter[i][1]
                    res_return.append(res)
                return res_return
        return []
