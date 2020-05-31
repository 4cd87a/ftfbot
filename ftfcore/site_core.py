from .core import core
from . import funcs
import re

class email_core:
    def __init__(self,base_dir=None,logger=None):
        self.cor = core(chatId=0,idd=0,base_dir=base_dir,logger=logger)
        self.logger = logger

    def test(self):
        self.cor.simplesend("test")
        return "normal test"

    def got_email(self,email):
        if 'from' not in email or \
            'to' not in email or \
            'subject' not in email or \
            'text' not in email: return 0
        ret = self.cor.got_email(email)
        return "Thanks. {}".format(ret)

class site_core:
    def __init__(self,base_dir=None,idd=None,username=None,logger=None):
        self.logger = logger
        try:
            if idd!=None: idd = int(idd)
        except Exception as e:
            self.is_active = False
            print(e)
            return

        self.cor = core(chatId=0,idd=idd,username=username,base_dir=base_dir,logger=logger)
        self.person = self.cor.db.person
        self.id = self.cor.db.idd

        # self._print("+++++++++++++")
        # self._print(self.person)

        if int(self.person['id'])!=0:
            self.is_active = True
        else:
            self.is_active = False

    def check_password(self,idd=None,username=None,password=None,cod=None):
        if username!=None and re.match("^[a-zA-Z][a-zA-Z0-9_]+$",username)==None: username=None
        if idd!=None and re.match("^[0-9]{1,10}$",idd)==None: idd=None
        if password!=None and re.match("^[a-zA-Z0-9]{8,24}$",password)==None: password=None

        if cod!=None:
            if re.match("^[a-zA-Z0-9]{8,24}$",cod)!=None:
                ret = self.cor.reset_password(idd=idd,username=username,cod=cod,password=password)
                if type(ret)==int and ret>0: return ret
                self._print(self.out(ret),'e')
                return self.out(ret)
            else:
                return 0

        check = self.cor.check_password(idd=idd,username=username,password=password)
        self.id = check
        return check

    def reset_password(self,idd=None,username=None,cod=None):
        if username!=None and re.match("^[a-zA-Z][a-zA-Z0-9_]+$",username)==None: username=None
        if idd!=None and re.match("^[0-9]{1,10}$",idd)==None: idd=None
        if cod!=None and re.match("^[a-zA-Z0-9]{20,24}$",cod)==None: cod=None

        check = self.cor.reset_password(idd=idd,username=username)
        return check

    def check_pin(self,idd=None,username=None,password=None):
        check = self.cor.check_pin(idd=idd,username=username,password=password)
        self.id = self.cor.db.idd
        return check


    def get_person_info(self,idd=None,username=None):
        if username == 'None': username = None
        if idd==None and username==None: return self.person
        if int(self.person['access_level'])>=5:
            return self.cor.db.get_person(idd=idd,username=username)
        return False

    def update_person_info(self,idd,name=None, patronymic=None, email=None, year_start=None, wts = None, password=None, pin=None, telname=None, ttype=None, beta=None,access_level=None):
        self._print("password: {}".format(password))
        if password != None:
            password = funcs.passwordHash(password)
            if password.get("bon") == False:
                return [[0, password.get('error')]]
            password = password['hash']

        if pin != None:
            pin = funcs.pinHash(pin)
            if pin.get("bon") == False:
                return [[0, pin.get('error')]]
            pin = pin['hash']

        self.cor.db.update_person_info(idd=idd,name=name,patronymic=patronymic,email=email,year_start=year_start,wts=wts,password=password,pin=pin,telname=telname,ttype=ttype,beta=beta,access_level=access_level)
        return 0


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

    def out(self,send):
        if type(send)!=list: return str(send)
        sendtxt = ''
        for s in send:
            if type(send)!=list and type(send)!=tuple:
                sendtxt+=str(s)
            else:
                if s[0]==0:sendtxt+=str(s[1])+"; "

        return sendtxt

class easyspeak_core:
    def __init__(self,base_dir=None,logger=None,ip=None):
        self.cor = core(chatId=0,idd=0,base_dir=base_dir,logger=logger)
        self.logger = logger
        self.ip = ip

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
        self.cor.close()

    def login(self,username,pin):
        return self.cor.easyspeak_login(username=username,pin=pin,ip=self.ip)

    def sendtext(self,username,pin,text):
        return self.cor.easyspeak_sendtext(username=username,pin=pin,text=text,ip=self.ip)

    def getfile(self,username,pin):
        return self.cor.easyspeak_file_get(username=username,pin=pin,ip=self.ip)


