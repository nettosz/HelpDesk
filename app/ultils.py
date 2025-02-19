import uuid
import app
from threading import Thread
from bs4 import BeautifulSoup
from hashlib import sha1

from werkzeug.utils import secure_filename
from os.path import join, abspath
from os import remove
import json
from flask_mail import Message
from app.mail import mail
from app.models.tables import Ticket
from app.ext.db import db
from flask import jsonify

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


def clear_duplicates():
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from hashlib import sha1
    
    # Query all tickets
    chamados = Ticket.query.all()
    n = 0

    for chamado in chamados:
        print(f"CHAMADO {n}")

        # List to store unique matches along with their HTML content
        unique_matches = {}
        
        if html := chamado.historico:
            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all <div> elements with class 'hist'
            hist_divs = soup.find_all('div', class_='hist')
            
            for div in hist_divs:
                # Extract text from the <div> element
                div_text = div.get_text(strip=True)
                
                sha1_hash = sha1(div_text.encode('utf-8')).hexdigest()
                if not sha1_hash in unique_matches.keys():
                    unique_matches[sha1_hash] = str(div)

        chamado.historico = "".join(unique_matches.values())
        db.session.commit()
        n += 1
        
    # Return the list of unique matches with their HTML content
    return unique_matches
                
def update_main_reponses(mail):
    body = mail.get('body')
    sub = mail.get('subject')
    email = mail.get('email')

    id = int(sub.split(" ")[-1])
    chamado = Ticket.query.filter_by(_id=id).first()

    email = f"<div class='hist'><div><div>De: {email}</div>{body}</div></div>"
    
    # Create a list to store the SHA-1 hashes
    sha1_hashes = []
    
    #Atualiza o historico do chamado
    if html_content := chamado.historico:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all div elements with the class 'hist'
        hist_divs = soup.find_all('div', class_='hist')

        for div in hist_divs:
            # Get the text content of the div
            div_text = div.text.strip()
            
            # Calculate the SHA-1 hash of the text
            sha1_hash = sha1(div_text.encode('utf-8')).hexdigest()
            
            # Add the hash to the list
            sha1_hashes.append(sha1_hash)

        if not sha1(email.encode('utf-8')).hexdigest() in sha1_hashes:

            chamado.historico += email

        db.session.commit()
    
        # Optionally, you can send a response back to acknowledge the request
        return jsonify({"status": "success", "message": "Email data received successfully!"}), 200

def get_mails_list(tck, user, id):
    mails = [u.email for u in user.query.filter_by(dep="TI").all()]
    mails.append(user.query.filter_by(_id=id).first().email)

    try:
        att_email = tck.att_email
        att_mails_split = att_email.split(",")
        
        if len(att_mails_split) > 1:
            mails.extend(att_mails_split)

        if att_email:
            mails.append(att_email)
    except:
        pass
    
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

def filter_by(chamados, filter):    
    filter_chamados = [chm for chm in chamados if filter in f'{chm.autor}{chm.problema}{chm.ativo}{chm.prioridade}{chm.dep}{chm._id}{chm.att}']
    
    return filter_chamados
