# -*- coding: utf-8 -*-
"""
@author: K
"""
import re, string, random
import hashlib, pwnedpasswords
from werkzeug.security import generate_password_hash



def jsontostr(jsn,start="##",dec='#',next=';'): #Простой способ кодирования dict в str, чтобы передовать в callback_data
    #параметры функции абсолютно случайны, главное чтобы они совпадали с декодированием и не могли встретиться в изначальном json
    st = start
    for key in jsn.keys():
        k = str(key).replace(start,"").replace(dec,"").replace(next,"")
        v = str(jsn.get(key)).replace(start,"").replace(dec,"").replace(next,"")
        st += k + dec + v + next
    return st


def strtojson(st,start="##",dec='#',next=';'): #Декодирование str to json
    jsn = {}
    if st.find(start)!=0: return {}
    st = st[len(start):]
    while(next in st):
        key = st[:st.find(dec)]
        value = st[st.find(dec)+len(dec):st.find(next)]
        jsn.setdefault(key,value)
        st = st[st.find(next)+len(next):]
    return jsn
def generateHash(text,length=20):
    return hashlib.sha1('{}'.format(text).encode()).hexdigest()[:length]

def passwordHash(password):
    if len(password)<8: return {"bon":False,"error":"Пароль слишком короткий (<8)."}
    if len(password)>24: return {"bon":False,"error":"Пароль слишком длинный (>24)."}
    if re.search("^[a-zA-Z0-9]{8,24}$", password)==None: return {"bon":False,"error":"Пароль не должен использовать специальные символы."}
    hsh = hashlib.sha1(password.encode()).hexdigest()
    hshcheck = pwnedpasswords.check(hsh)
    if hshcheck>1: return {"bon":False,"error":"Пароль найден {} раз в базе haveibeenpwned, поэтому его не стоит использовать.".format(hshcheck)}
    hsh = generate_password_hash(password)
    return {"bon":True,"hash":hsh}

def pinHash(password):
    if len(password)<4: return {"bon":False,"error":"Пин-код слишком короткий (<4)."}
    if len(password)>12: return {"bon":False,"error":"Пин-код слишком длинный (>12)."}
    if re.search("^[a-zA-Z0-9]+$", password)==None: return {"bon":False,"error":"Пин-код не должен использовать специальные символы."}
    hsh = hashlib.sha1(password.encode()).hexdigest()
    hshcheck = pwnedpasswords.check(hsh)
    if hshcheck>1000: return {"bon":False,"error":"Пароль найден {} раз (т.е. >1000 раз) в базе haveibeenpwned, поэтому его не стоит использовать.".format(hshcheck)}
    hsh = generate_password_hash(password)
    return {"bon":True,"hash":hsh}

def passGenerator(length = 12): # простой генератор паролей
    password_characters = string.ascii_letters + string.digits # + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(length))

def tokenGenerator(login,passHash = None): #Генерирование token
    if passHash == None:
        passHash = passwordHash(passGenerator(24)).get('hash')[21:]
    hsh = hashlib.sha1(str(login).encode()).hexdigest() + passHash
    return hsh

def abc_simpleLet(a):
    if a == 0: a = 35
    if a >= 1 and a < 10: return chr(48+a)
    elif a >= 10 and a <= 35: return chr(87+a)
    else: return abc_simpleLet(a%35)

def abc_toLet(a):
    if (a<=0): return '0'
    ans = ''; aa = 0; i = 0
    while (a > aa): # if start by 'a' instead of 1
        a += 9*35**i
        aa += 35**(i+1)
        i += 1
    while (a > 0):
        ans = abc_simpleLet(a) + ans
        a = int((a-1)/35)
    return ans

def abc_toInt(st,simple=False):
    indx = 0; j = 0
    for i, s in enumerate(st):
        indxx = ord(s)-48
        if (indxx>10): indxx-=39
        indx += indxx*35**(len(st)-1-i)
    if simple: return indx
    # if start by 'a'
    while (indx>9*35**(j)):
        indx-=9*35**j
        j+=1
    return indx

def keyGenerator(key, length=4):
    hsh = ""
    keystr = abc_toLet(key)
    ln = len(keystr)
    length = max(length,ln+1)
    hsh = abc_simpleLet(random.randint(0, int(35/length))*(length-1)+ln)
    hsh += keystr
    for i in range(len(hsh),length): hsh+=abc_simpleLet(random.randint(1, 35))
    return hsh

def keyDecoder(hsh,length=4):
    length = max(length,len(hsh))
    ln = (abc_toInt(hsh[0],simple=True)-1)%(length-1)+1
    key = abc_toInt(hsh[1:1+ln])
    return key

