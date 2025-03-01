from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField

##
## Declaração dos Formularios com Wtforms
##
class File(FlaskForm):
    file = FileField("Icone", validators=[])

    def insert_data(self, data):
        self.file.data = data.file

class Procedimentos(FlaskForm):
    titulo = StringField("Titulo", validators=[DataRequired()])
    procedimento = StringField("Procedimento", validators=[DataRequired()])
    
    def insert_data(self, data):
        self.titulo.data = data.titulo
        self.procedimento.data = data.procedimento

class Tickets(FlaskForm):
    problema = TextAreaField("Problema", validators=[DataRequired()])
    #prioridade = SelectField('Prioridade',choices=[("1", "Emergencia"),("2", "Urgente"), ("3", "Normal"), ("4", "Não Urgente")], coerce=str)

    def insert_data(self, data):
        self.problema.data = data.problema
        #self.prioridade.data = data.prioridade
        
class Dep(FlaskForm):
    dep = SelectField("departamento", choices=[
    ("Colheita", "Colheita"),
    ("Geoprocessamento", "Geoprocessamento"),
    ("Juridico", "Juridico"),
    ("Pesquisa", "Pesquisa"),
    ("Relaçoes com Comunidade", "Relaçoes com Comunidade"),
    ("DMAST", "DMAST"),
    ("Gerencia", "Gerencia"),
    ("Interprete", "Interprete"),
    ("Administrativo", "Administrativo"),
    ("Import/Export", "Import/Export"),
    ("Diretoria", "Diretoria"),
    ("Compras", "Compras"),
    ("Soja", "Soja"),
    ("GFundiário", "GFundiário"),
    ("BRinfo", "BRinfo"),
    ("Controladoria", "Controladoria"),
    ("RSC", "RSC"),
    ("Recursos Humanos", "Recursos Humanos"),
    ("Sivicultura", "Sivicultura"),
    ("Viveiro", "Viveiro"),
    ("Estoque", "Estoque"),
    ("Planejamento", "Planejamento")


    ], coerce=str)

    def insert_data(self, data):
        self.dep.data = data.dep
        

