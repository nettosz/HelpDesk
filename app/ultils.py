import uuid
import app
from threading import Thread

from werkzeug.utils import secure_filename
from os.path import join, abspath
from os import remove
import json
from flask_mail import Message
from app.mail import mail

######################

def run_in_thread(fn):
    def run(*k, **kw):
        t = Thread(target=fn, daemon=True,args=k, kwargs=kw)
        t.start()
        return t # <-- this is new!
    return run

####
####
####

def get_mails_list(tck, user, autor):
    mails = [u.email for u in user.query.filter_by(dep="TI").all()]
    mails.append(user.query.filter_by(nome=autor).first().email)

    att_email = tck.att_email
    if att_email:
        mails.append(att_email)
    
    return mails
    
@run_in_thread
def send_mail(templ, desc, mails):
    subject = desc
    body = templ
    
    with app.create_app().app_context():
        with mail.mail.connect() as conn:
            msg = Message(subject=subject,
                        html=body,
                        recipients=mails)
            conn.send(msg)

def remove_file(file):
    try:
        remove(abspath(f"app/{file}"))
    except:
        pass

def insert(d, value, pos):
    if pos and value and pos in d:
        for k, _ in d.items():
            if k == pos:
                d[k].append(value)
                return d
            
    elif pos and value:
        d[pos] = [value]
    else:
        d[pos] = []
    return d

def del_cat(file, cat, sub=""):
    if sub:
        file[cat].remove(sub)
    else:
        file.pop(cat)
    return file

def get(d, pos):
    for k, v in d.items():
        if k == pos:
            return v

def load(file):
    try:
        with open(file, "r") as f:
            return json.loads(f.read())
    except:
        return {}
        
def save(file, value):
    with open(file, "w") as f:
        f.write(json.dumps(value))
    return f

def format_name(filename: str) -> str:
    type = filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{type}"
    return name

def upload_file(f, path):
    if f:
        name = format_name(f.filename)
        p = abspath(join(f"app/{path}", secure_filename(name)))        
        f.save(p)
        return f'{path}/{name}'

def filter_by(chamados, filter, state):
    filter = filter.split("@")

    content = filter[0]
    category = filter[1]

    #Filtros de chamado:
    ###################
    #0 = Usuario
    #1 = Departamento
    #2 = Nivel
    #3 = Categoria
    #4 = Descriçao
    ###################
    
    chamados = chamados.query.filter_by(estado=state).all()
    filter_chamados = []
    
    if category == "0":
        filter_chamados = [chm for chm in chamados if content in chm.autor]
    
    if category == "1":
        filter_chamados = [chm for chm in chamados if content in chm.dep]
    
    if category == "2":
        filter_chamados = [chm for chm in chamados if content in str(chm.prioridade)]

    if category == "3":
        filter_chamados = [chm for chm in chamados if content in chm.ativo]

    if category == "4":
        filter_chamados = [chm for chm in chamados if content in chm.problema]
    
    return filter_chamados
