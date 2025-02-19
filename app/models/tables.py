from email.policy import default
from app.ext.db import db
from datetime import datetime

##
## Declaração das models
##
class Procedimento(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String, nullable=False)
    procedimento = db.Column(db.String, nullable=False)

class Etapa(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    texto = db.Column(db.String, nullable=False)
    ticket_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="1")
    user = db.Column(db.String, default="")

class Ticket(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problema = db.Column(db.String, nullable=False)
    ativo = db.Column(db.String, nullable=False)
    prioridade = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String, nullable=False, default="Aberto")
    data_hora_a = db.Column(db.DateTime, nullable=False, default=datetime.today())
    data_hora_f = db.Column(db.DateTime, nullable=False, default=datetime.today())
    periodo = db.Column(db.String)
    file = db.Column(db.String)
    autor = db.Column(db.String, nullable=False)
    
    # Pessoa que esta resolvendo o chamado
    att = db.Column(db.String)
    att_email = db.Column(db.String)

    re_att_just = db.Column(db.String)
    dep = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user._id'), nullable=False)

    # Flag para checar definição de prioridade ja foi definida
    p_defined = db.Column(db.String, default="0")

    # Ordem de prioridade na fila
    p_order = db.Column(db.Integer, default=0)
    
    # Historico de emails do chamado
    historico = db.Column(db.String)

class User(db.Model):
    _id = db.Column(db.String, primary_key=True)
    file = db.Column(db.String, nullable=False)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    dep = db.Column(db.String, default="")
    admin = db.Column(db.Boolean, default=False)
    terceiro = db.Column(db.Boolean, default=False)
    
    tickets = db.relationship('Ticket', backref='user',
    cascade="all, delete-orphan",
    lazy='dynamic')
