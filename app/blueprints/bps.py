from flask import Blueprint, redirect, render_template, flash, request, session, url_for, send_file
from app.models.tables import Ticket, User, Procedimento, Etapa
from app.models.forms import Tickets, File, Procedimentos, Dep
from datetime import datetime
import json
import requests
import os

from app.auth.auth import auth, get_google_provider_cfg, client, GOOGLE_CLIENT_SECRET, GOOGLE_CLIENT_ID

from ..ultils import get_mails_list, insert, del_cat, load, remove_file,\
    save, upload_file, send_mail, filter_by

from app.ext.db import db

bp_app = Blueprint("bp", __name__)

##
## Views
##

## Endpoint para download do backup, somente admin
@bp_app.route("/save-backup")
def backup():
    backup_file_path = "/home/HelpDeskPython/db.sqlite"
    
    if not session.get("admin"):
        flash("Access denied: Admins only.", "error")
        return redirect(url_for("bp.index"))

    if not os.path.exists(backup_file_path):
        flash("Backup file not found.", "error")
        return redirect(url_for("bp.index"))

    return send_file(backup_file_path, as_attachment=True)

@bp_app.route("/login")
def init_login():
    request_uri = auth()
    return redirect(request_uri)

@bp_app.route("/login/get_user_info")
def get_user_info():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = {
        "id":unique_id, "nome":users_name, "email":users_email, "icon":picture
    }

    icon = user["icon"].split("/")[-1]

    print(url_for("bp.create_user", id=user["id"], email=user["email"], nome=user["nome"], icon=icon))
    # Send user back to homepage
    return redirect(url_for("bp.create_user", id=user["id"], email=user["email"], nome=user["nome"], icon=icon))

@bp_app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("bp.login"))

@bp_app.route("/", methods=["GET", "POST"])
def login():
    try:
        if session["id"]:
            if session["admin"]:
                return redirect("/home-admin")
            return redirect("/home")
    except KeyError:
        pass

    return render_template("login.html")

@bp_app.route("/home")
def index():
    try:
        if session["id"]:
            return render_template("index.html", admin=False)
    except KeyError:
        return redirect("/")

@bp_app.route("/home-admin")
def index_admin():
    if session["admin"]:
        return render_template("index.html", admin=True)
    else:
        return redirect("/")

@bp_app.route("/ticket/<id>")
def ticket(id):
    ### Fila de chamados em atendimento
    #Fila de chamados em atendimento ou abertos
    
    ticket = Ticket.query.filter_by(_id=id).first()
    try:
        fila = Ticket.query.filter_by(estado="Em Atendimento").all() + Ticket.query.filter_by(estado="Aberto").all()

        #Ordena a fila por prioridade
        fila = sorted(fila, key=lambda x: x.prioridade)
        
        
        #posição do chamado na fila
        pos = fila.index(ticket) + 1
        
        ### Fila de chamados em atendimento
    except:
        pos = 0

    return render_template("chamado.html",
    r_user=User.query.filter_by(_id=session["id"]).first().nome,
    admin=session["admin"],
    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro,
    chamado=ticket,
    users = User.query.filter_by(terceiro=True).all() + User.query.filter_by(admin=True).all(),
    pos=pos)

@bp_app.route("/tickets/<filter>")
@bp_app.route("/tickets/")
def tickets(filter=None):
    #Filtra chamados atribuidos para terceiros
    user = User.query.filter_by(_id=session["id"]).first()
    if user.terceiro:
        chamados = Ticket.query.filter_by(att=user.nome).filter(Ticket.estado == "Aberto").all()
        
        return render_template("chamados.html",len=len,list=list,
        chamados=chamados)
    
    if session["admin"]:
        chamados = Ticket
        
        if filter:
            chamados = filter_by(chamados, filter, "Aberto")
        else:
            chamados = Ticket.query.filter_by(estado="Aberto").all()

        print(chamados)
        return render_template("chamados.html",len=len,list=list,
            chamados=chamados,
            admin=session["admin"])
    
    chamados = User.query.filter_by(_id=session["id"]).first().tickets.filter(Ticket.estado == "Aberto").all()
    return render_template("chamados.html",len=len,list=list,
        chamados=chamados)

@bp_app.route("/tickets_close/<filter>")
@bp_app.route("/tickets_close")
def tickets_close(filter=None):
    user = User.query.filter_by(_id=session["id"]).first()
    if user.terceiro:
        chamados = Ticket.query.filter_by(att=user.nome).filter(Ticket.estado == "Fechado").all()
        
        return render_template("chamados.html",len=len,list=list,
        chamados=chamados)

    if session["admin"]:
        chamados = Ticket
        
        if filter:
            chamados = filter_by(chamados, filter, "Fechado")
        else:
            chamados = Ticket.query.filter_by(estado="Fechado").all()
            
        return render_template("chamados.html",len=len,list=list,
            chamados=chamados,
            admin=session["admin"])

    return render_template("chamados.html",len=len,list=list,
    chamados=User.query.filter_by(_id=session["id"]).first().tickets.filter(Ticket.estado == "Fechado").all())

@bp_app.route("/tickets_resol/<filter>")
@bp_app.route("/tickets_resol")
def tickets_resol(filter=None):
    user = User.query.filter_by(_id=session["id"]).first()
    if user.terceiro:
        chamados = Ticket.query.filter_by(att=user.nome).filter(Ticket.estado == "Em Atendimento").all()
        
        return render_template("chamados.html",len=len,list=list,
        chamados=chamados)

    if session["admin"]:
        chamados = Ticket
        
        if filter:
            chamados = filter_by(chamados, filter, "Em Atendimento")
        else:
            chamados = Ticket.query.filter_by(estado="Em Atendimento").all()

        return render_template("chamados.html",len=len,list=list,
            chamados=chamados,
            admin=session["admin"])

    
    return render_template("chamados.html",len=len,list=list,
    chamados=User.query.filter_by(_id=session["id"]).first().tickets.filter(Ticket.estado == "Em Atendimento").all())


@bp_app.route("/base_create", methods=["POST", "GET"])
def base_create():
    if request.method == "POST":
        if session["admin"]:    
            data = Procedimento()
            form = Procedimentos()
            if form.validate_on_submit():
                form.populate_obj(data)
                db.session.add(data)
                db.session.commit()
                flash("Procedimento criado com sucesso")
            return redirect("/home-admin")

        flash("Apenas administradores podem criar procedimentos")
        return redirect("/home")
    return render_template("create_base.html", form=Procedimentos())

@bp_app.route("/base_content/<id>")
def base_content(id):
    proc = Procedimento().query.filter_by(_id=id).first()

    return render_template("base_content.html",
    enumerate=enumerate,
    proc=proc,
    etapas=proc.procedimento.split(" "), admin=session["admin"])

@bp_app.route("/base_list")
def base_list():
    return render_template("base_list.html", procs=Procedimento.query.all())

@bp_app.route("/create_ticket", methods=["POST", "GET"])
def create_ticket():
    if request.method == "POST":
        data = Ticket()
        form_cad = Tickets()
        file = File()

        form = request.form

        user = User.query.filter_by(_id=session["id"]).first()
        username = user.nome
        userdep = user.dep

        if form_cad.validate_on_submit() and file.validate_on_submit():
            form_cad.populate_obj(data)
            data.prioridade = 0
            data.ativo = request.form["ativo"]
            data.autor = username
            data.dep = userdep
            data.data_hora_a = datetime.today()
            data.file = upload_file(file.file.data, "static/files/anexos")
            data.user_id = session["id"]
            db.session.add(data)
            db.session.commit()

            flash("Chamado aberto com sucesso!")
            
            templ = render_template("mail_template.html",
            data=datetime.today().strftime("%d/%m/%Y %H:%M"),
            user=username,
            sys=form["ativo"],
            prob=form["problema"],
            info="",
            type=1,
            nome=session["nome"],
            num=data._id,
            nivel="Não definido"
            )

            send_mail(templ=templ,
            desc=f"TI AMCEL - Ticket de Suporte {data._id}",
            mails=get_mails_list(data ,User, username))
            
            #Atualiza o historico do chamado
            if data.historico:
                data.historico += f"<div class='hist'>{templ}</div>"
            else:
                data.historico = f"<div class='hist'>{templ}</div>"
                
            
            db.session.commit()
            
        if session["admin"]:
            return redirect("/home-admin")
        return redirect("/home")
    
    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro
    return render_template("create_ticket.html", terceiro=terceiro, form=Tickets(), file=File(), cats=load("app/categories.json"), admin=session["admin"], chamados=Ticket.query.all())

@bp_app.route("/create_user/<id>/<email>/<nome>/<icon>", methods=["GET"])
def create_user(id, email, nome, icon):
    if user := User.query.filter_by(_id=id).first():
        session["admin"] = user.admin
        session["id"] = user._id
        session["nome"] = user.nome

        if session["admin"]:
            return redirect("/home-admin")
        else:
            return redirect("/home")
    else:
        user = User(_id=id, file=f"https://lh3.googleusercontent.com/a/{icon}", nome=nome, email=email)
        db.session.add(user)
        db.session.commit()
        session["admin"] = user.admin
        session["id"] = user._id
        session["nome"] = user.nome
            
        return redirect("/select_dep")

@bp_app.route("/select_dep", methods=["GET", "POST"])
def select_dep():
    form = Dep()

    if request.method == "POST":
        data = User.query.filter_by(_id=session["id"]).first()
        if form.validate_on_submit():
            form.populate_obj(data)
            db.session.commit()

            if session["admin"]:
                return redirect("/home-admin")
            return redirect("/home")
    return render_template("select_dep.html", form=form)

@bp_app.route("/view_user/<id>")
def view_user(id):
    return render_template("user.html", user=User.query.filter_by(_id=id).first())

@bp_app.route("/view_users")
def view_users():
    return render_template("users.html", users=User.query.all())

@bp_app.route("/view_user_lateral")
def view_user_lateral():
    return render_template("view_user_lat.html", user=User.query.filter_by(_id=session["id"]).first())

##
## Controllers
##

# Deletar Tabela
@bp_app.route("/delete/<data>/<id>")
def delete(data, id):
    if data == "user":
        obj = User.query.filter_by(_id=id).first()
        remove_file(obj.file)

        db.session.delete(obj)
        db.session.commit()

        flash("Usuario excluido com sucesso!")
        return redirect("/home-admin")

    elif data == "ticket":
        obj = Ticket.query.filter_by(_id=id).first()
        etapas = Etapa.query.filter_by(ticket_id=id).all()

        for etapa in etapas:
            db.session.delete(etapa)
        
        remove_file(obj.file)
        db.session.delete(obj)
        db.session.commit()
        
        flash("Chamado excluido com sucesso!")
        return redirect("/home-admin")


    elif data == "proc":
        obj = Procedimento.query.filter_by(_id=id).first()
        db.session.delete(obj)
        db.session.commit()

        flash("Procedimento excluido com sucesso!")
        return redirect("/home-admin")

#Atualiza o estado do ticket
@bp_app.route("/update_state/<state>/<id>")
def update_state(state, id):
    obj = Ticket.query.filter_by(_id=id).first()
    user = User.query.filter_by(_id=session["id"]).first()
    
    if user.nome == obj.att or not obj.att:
        obj.estado = state

        if state == "Em Atendimento":
            obj.att = user.nome
            obj.att_email = user.email

            # Reseta as informaçoes de periodo caso o estado: Reabrir chamado
            obj.periodo = ""

            templ = render_template("mail_template.html",
            user=obj.autor,
            sys=obj.ativo,
            prob=obj.problema,
            info="",
            type=2,
            nome=session["nome"],
            data=datetime.today().strftime("%d/%m/%Y %H:%M"),
            nivel = obj.prioridade,
            num=obj._id)

            send_mail(templ=templ,
            desc=f"TI AMCEL - Ticket de Suporte {obj._id}",
            mails=get_mails_list(obj ,User, obj.autor))

            
            #Atualiza o historico do chamado
            if obj.historico:
                obj.historico += f"<div class='hist'>{templ}</div>"
            else:
                obj.historico = f"<div class='hist'>{templ}</div>"
                
            
        if state == "Fechado":
            templ = render_template("mail_template.html",
            user=obj.autor,
            sys=obj.ativo,
            prob=obj.problema,
            info="",
            type=3,
            nome=session["nome"],
            data=datetime.today().strftime("%d/%m/%Y %H:%M"),
            nivel = obj.prioridade,
            num=obj._id)


            send_mail(templ=templ,
            desc=f"TI AMCEL - Ticket de Suporte {obj._id}",
            mails=get_mails_list(obj ,User, obj.autor))

            #Atualiza o historico do chamado
            if obj.historico:
                obj.historico += f"<div class='hist'>{templ}</div>"
            else:
                obj.historico = f"<div class='hist'>{templ}</div>"
            
            agora = datetime.today()
            obj.data_hora_f = agora
            obj.periodo = str(agora - obj.data_hora_a).split(".")[0]

        db.session.commit()
        flash(f"Chamado {state}")
    else:
        flash("Não pode atender um chamado atribuido a outra pessoa!")

    if session["admin"]:
        return redirect("/home-admin")
    return redirect("/home")

#Atualiza as permições do user
@bp_app.route("/make_admin/<id>/<data>")
def make_admin(id, data):
    user = User.query.filter_by(_id=id).first()
    user.admin = bool(int(data))
    db.session.commit()

    flash(f"Permissão do usuario {user.nome} atualizada")
    return redirect("/home-admin")

@bp_app.route("/make_terceiro/<id>/<data>")
def make_terceiro(id, data):
    user = User.query.filter_by(_id=id).first()
    user.terceiro = bool(int(data))
    db.session.commit()

    flash(f"Permissão do usuario {user.nome} atualizada")
    return redirect("/home-admin")

#Reatribuir chamado
@bp_app.route("/att_chamado", methods=["POST"])
def att_chamado():
    form = request.form
    tck = Ticket.query.filter_by(_id=form["id"]).first()

    nome = form["att"]
    
    flash(f"Chamado reatribuido para: {nome}")

    templ = render_template("mail_template.html",
    user=tck.att,
    sys=tck.ativo,
    prob=tck.problema,
    info=form["just"],
    type=4,
    nome=session["nome"],
    data=datetime.today().strftime("%d/%m/%Y %H:%M"),
    num=tck._id,
    nivel = tck.prioridade,
    rtb=nome
    )
    
    #Atualiza o historico do chamado
    if tck.historico:
        tck.historico += f"<div class='hist'>{templ}</div>"
    else:
        tck.historico = f"<div class='hist'>{templ}</div>"
        

    tck.att = form["att"]
    tck.att_email = User.query.filter_by(nome=form["att"]).first().email

    tck.re_att_just = form["just"]
    db.session.commit()
    
    send_mail(templ=templ,
    desc=f"TI AMCEL - Ticket de Suporte {tck._id}",
    mails=get_mails_list(tck ,User, session["nome"]))

    return redirect("home-admin")

#Cria uma categoria de chamados
@bp_app.route("/create_cat", methods = {"GET", "POST"})
def create_cat():
    if request.method == "POST":
        form = request.form
        cat = form["cat"]
        sub_cat = form["sub"]
        if cat:
            file = load("app/categories.json")
            file = insert(file, sub_cat, cat)
            save("app/categories.json", file)
            flash("Categoria criada com susesso")

            return redirect("/home-admin")

    return render_template("create_cat.html")

#Exclui uma categoria de chamados 
@bp_app.route("/delete_cat/<cat>/<sub>")
def delete_cat(cat,sub):
    if cat:
        file = load("app/categories.json")
        file = del_cat(file, cat, sub)
        save("app/categories.json", file)
    
    return render_template("cats.html", cats=load("app/categorias.json"))

@bp_app.route("/cats")
def cats():
    return render_template("cats.html", cats=load("app/categories.json"))

#Retorna lista de etapas para um chamado
@bp_app.route("/etapas/<ticket_id>")
def get_etapas(ticket_id):
    etapas = Etapa.query.filter_by(ticket_id=ticket_id).all()
    chamado = Ticket.query.filter_by(_id=ticket_id).first()
    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro
    
    return render_template("etapas.html", etapas=etapas, chid=ticket_id, admin=session["admin"], terceiro=terceiro, chamado=chamado)

#Atualiza e returna lista de etapas
@bp_app.route("/update_etapa/<etapa_id>")
def update_etapa(etapa_id):
    etapa = Etapa.query.filter_by(_id=etapa_id).first()
    if etapa.status == "0":
        etapa.status = "1"
    else:
        etapa.status = "0"
    
    db.session.commit()
    
    ticket_id = etapa.ticket_id 
    etapas = Etapa.query.filter_by(ticket_id=ticket_id).all()
    chamado = Ticket.query.filter_by(_id=ticket_id).first()

    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro
    return render_template("etapas.html", etapas=etapas, admin=session["admin"], terceiro=terceiro, chamado=chamado)

@bp_app.route("/delete_etapa/<etapa_id>")
def delete_etapa(etapa_id):
    etapa = Etapa.query.filter_by(_id=etapa_id).first()
    db.session.delete(etapa)
    db.session.commit()

    ticket_id = etapa.ticket_id 
    etapas = Etapa.query.filter_by(ticket_id=ticket_id).all()
    chamado = Ticket.query.filter_by(_id=ticket_id).first()

    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro
    return render_template("etapas.html", etapas=etapas, admin=session["admin"], terceiro=terceiro, chamado=chamado)

#Cria uma etapa
@bp_app.route("/create_etapa/<ticket_id>")
@bp_app.route("/create_etapa/<ticket_id>/<value>")
def create_etapa(ticket_id, value):
    etapa = Etapa(texto=value, ticket_id=ticket_id)
    db.session.add(etapa)
    db.session.commit()

    etapas = Etapa.query.filter_by(ticket_id=ticket_id).all()
    chamado = Ticket.query.filter_by(_id=ticket_id).first()

    templ = render_template("mail_template.html",
    user=chamado.att,
    sys=chamado.ativo,
    prob=chamado.problema,
    type=5,
    nome=session["nome"],
    data=datetime.today().strftime("%d/%m/%Y %H:%M"),
    num=chamado._id,
    nivel = chamado.prioridade,
    etapa = etapa.texto
    )
    
    send_mail(templ=templ,
    desc=f"TI AMCEL - Ticket de Suporte {chamado._id}",
    mails=get_mails_list(chamado ,User, chamado.autor))
    
    #Atualiza o historico do chamado
    if chamado.historico:
        chamado.historico += f"<div class='hist'>{templ}</div>"
    else:
        chamado.historico = f"<div class='hist'>{templ}</div>"
     

    db.session.commit()
    
    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro
    return render_template("etapas.html", etapas=etapas, admin=session["admin"], terceiro=terceiro, chamado=chamado)

@bp_app.route("/set_pr/<id>/<pr>")
@bp_app.route("/set_pr")
def set_pr(id,pr):
    
    ticket = Ticket.query.filter_by(_id=id).first()
    ticket.p_defined = "1"
    ticket.prioridade = int(pr)
    db.session.commit()
    
    terceiro = User.query.filter_by(_id=session["id"]).first().terceiro

    return render_template("create_ticket.html", admin=session["admin"],terceiro=terceiro, chamados=Ticket.query.all())

def configure(app):
    app.register_blueprint(bp_app)
