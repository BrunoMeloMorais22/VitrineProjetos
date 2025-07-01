from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from datetime import timedelta
import smtplib
from sqlalchemy import func
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from db import db
import os

app = Flask(__name__)

app.secret_key = "corinthians"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db.init_app(app)
CORS(app)
from models import usuarios
from models import projetos

@app.route("/", methods=["GET", "POST"])
def index():
    todos_projetos = projetos.query.all()
    return render_template("index.html", projetos=todos_projetos)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html")
    try:
        if request.method == "POST":
            data = request.get_json()

            if not data:
                return jsonify({"mensagem": "Dados não recebidos"})
            
            nomeCadastro = data.get("nomeCadastro")
            emailCadastro = data.get("emailCadastro")
            senhaCadastro = data.get("senhaCadastro")
            confirmarSenha = data.get("confirmarSenha")


            if not nomeCadastro or not emailCadastro or not senhaCadastro or not confirmarSenha:
                return jsonify({"mensagem": "Por favor, preencha todos os campos para continuar"})
            
            if confirmarSenha != senhaCadastro:
                return jsonify({"mensagem": "As senhas não combinam. Tente novamente"})
            
            user_exists = usuarios.query.filter_by(emailCadastro=emailCadastro).first()

            if user_exists:
                return jsonify({"mensagem": "Email já cadastro. Por favor, faça login"})
            
            hashed_senha = generate_password_hash(senhaCadastro)
            
            new_user = usuarios(nomeCadastro=nomeCadastro, emailCadastro=emailCadastro, senhaCadastro=hashed_senha)
            db.session.add(new_user)
            db.session.commit()

            session['usuario'] = emailCadastro
            return jsonify({"mensagem": "Usuário cadastro com sucesso!"})
    except Exception as e:
        print("Erro no backend", e)
        return jsonify({"mensagem": "Erro no servidor"})

@app.route("/enviar_email", methods=["GET", "POST"])
def enviar_email():
    data = request.get_json()
    emailCadastro = data.get("emailCadastro")
    msg = EmailMessage()
    msg['Subject'] = "Cadastrado com sucesso"
    msg['From'] = "grumelo098@gmail.com"
    msg['To'] = emailCadastro
    msg.add_alternative(f"""
    <!DOCTYPE html>
<html>
  <body>
    <h2>📩 Obrigado por se cadastrar em nosso site!</h2>
    <p>✅ Seu processo de cadastro está finalizado.</p>
    <p>Agora você poderá desfrutar de nossas ferramentas e adicionar seus projetos em nossa plataforma.</p>
    <hr>
    <p>💬 Não responda este email. Em caso de dúvidas, entre em contato.</p>
  </body>
</html>
""", subtype='html')
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("grumelo098@gmail.com", "ourf sgnz wkiw sxse")
            smtp.send_message(msg)
        
    except Exception as e:
        print("Erro ao enviar email", e)
        return jsonify({"Erro no servidor"})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()

        emailLogin = data.get("emailLogin")
        senhaLogin = data.get("senhaLogin")

        user = usuarios.query.filter_by(emailCadastro=emailLogin).first()

        if user and check_password_hash(user.senhaCadastro, senhaLogin):
            session['usuario'] = user.emailCadastro
            return jsonify({"mensagem": "Login efetuado com sucesso"})
        else:
            return jsonify({"mensagem": "Email ou senha incorretos"}), 401
    return render_template("login.html")

@app.route("/verificar_login")
def verificar_login():
    if 'usuario' in session:
        return jsonify({"logado": True, "emailCadastro": session['usuario']})
    return jsonify({"logado": False})

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect(url_for("index"))

@app.route("/cadastrar_projeto", methods=["GET", "POST"])
def cadastrar_projeto():
    if request.method == "GET":
        return render_template("projetos.html")
    
    try:
        nomeProjeto = request.form.get("nomeProjeto")
        descricaoProjeto = request.form.get("descricaoProjeto")
        link = request.form.get("link")
        nomePessoaProjeto = request.form.get("nomePessoaProjeto")
        linguagens = request.form.get("linguagens")
        imagem = request.files.get("imagem")

        if not nomeProjeto or not descricaoProjeto or not linguagens or not imagem:
            return jsonify({"mensagem": "Preencha todos os campos"}), 400

        nome_imagem = imagem.filename
        caminho = os.path.join("static/uploads", nome_imagem)
        imagem.save(caminho)

        novo_projeto = projetos(
            nomeProjeto=nomeProjeto,
            descricaoProjeto=descricaoProjeto,
            link=link,
            linguagens=linguagens,
            imagem=nome_imagem,
            nomePessoaProjeto=nomePessoaProjeto
        )
        db.session.add(novo_projeto)
        db.session.commit()

        return jsonify({"mensagem": "Projeto cadastrado com sucesso"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": f"Erro ao cadastrar projeto: {e}"}), 500
