from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from datetime import timedelta
import smtplib
import requests
from sqlalchemy import func
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from db import db
import os
from itsdangerous import Serializer, URLSafeTimedSerializer

app = Flask(__name__)

app.secret_key = "corinthians"
serializer = URLSafeTimedSerializer(app.secret_key)

RECAPTCHA_SITE_KEY = "6LfgoXwrAAAAAMiavVD4pnLJflZdA6SSyatyETWT"
RECAPTCHA_SECRET_KEY = "6LfgoXwrAAAAAKkkfxULDqY-J5mAz7ogIBnyp3FE"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db.init_app(app)
CORS(app, supports_credentials=True)
from models import usuarios
from models import projetos

@app.route("/", methods=["GET", "POST"])
def index():
    todos_projetos = projetos.query.all()
    return render_template("index.html", projetos=todos_projetos)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html", site_key=RECAPTCHA_SITE_KEY)
    try:
        if request.method == "POST":
            data = request.get_json()

            if not data:
                return jsonify({"mensagem": "Dados não recebidos"})
            
            nomeCadastro = data.get("nomeCadastro")
            emailCadastro = data.get("emailCadastro")
            senhaCadastro = data.get("senhaCadastro")
            confirmarSenha = data.get("confirmarSenha")
            recaptcha_response = data.get("g-recaptcha-response")

            if not recaptcha_response:
                return jsonify({"mensagem": "Por favor, confirme que você não é um robô"})
            
            data = {
                "secret": RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response
            }

            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
            resultado = r.json()


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

@app.route("/enviar_email", methods=["POST"])
def enviar_email():
    try:
        data = request.get_json()

        if not data or "emailCadastro" not in data:
            return jsonify({"mensagem": "Email não recebido"}), 400

        emailCadastro = data["emailCadastro"]
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
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("grumelo098@gmail.com", "ourf sgnz wkiw sxse")
            smtp.send_message(msg)

        return jsonify({"mensagem": "Email enviado com sucesso"})

    except Exception as e:
        print("Erro ao enviar email", e)
        return jsonify({"mensagem": "Erro no servidor"}), 500

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()

        emailLogin = data.get("emailLogin")
        senhaLogin = data.get("senhaLogin")

        user = usuarios.query.filter_by(emailCadastro=emailLogin).first()

        if user and check_password_hash(user.senhaCadastro, senhaLogin):
            session['usuario'] = {
                "id": user.id,
                "nome": user.nomeCadastro,
                "email": user.emailCadastro
            }
            return jsonify({"mensagem": "Login efetuado com sucesso"})
        else:
            return jsonify({"mensagem": "Email ou senha incorretos"}), 401
    return render_template("login.html")

@app.route("/verificar_login")
def verificar_login():
    if 'usuario' in session:
        return jsonify({"logado": True, "emailCadastro": session['usuario']['email']})
    return jsonify({"logado": False})

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect(url_for("index"))

@app.route("/cadastrar_projeto", methods=["GET", "POST"])
def cadastrar_projeto():
    if request.method == "GET":
        return render_template("projetos.html")
    
    if 'usuario' not in session:
        return jsonify({"mensagem": "Usuário não autenticado"}), 401
    
    try:
        nomeProjeto = request.form.get("nomeProjeto")
        descricaoProjeto = request.form.get("descricaoProjeto")
        link = request.form.get("link")
        linguagens = request.form.get("linguagens")
        imagem = request.files.get("imagem")

        if not nomeProjeto or not descricaoProjeto or not linguagens or not imagem:
            return jsonify({"mensagem": "Preencha todos os campos"}), 400

        nome_imagem = imagem.filename
        caminho = os.path.join("static/uploads", nome_imagem)
        imagem.save(caminho)

        usuario = session['usuario']
        dono_id = usuario['id']

        novo_projeto = projetos(
            nomeProjeto=nomeProjeto,
            descricaoProjeto=descricaoProjeto,
            link=link,
            linguagens=linguagens,
            imagem=nome_imagem,
            dono_id=dono_id,
        )
        db.session.add(novo_projeto)
        db.session.commit()

        return jsonify({"mensagem": "Projeto cadastrado com sucesso"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": f"Erro ao cadastrar projeto: {e}"}), 500


@app.route("/perfil")
def perfil():
    nomeCadastro = session['usuario']['nome']
    emailCadastro = session['usuario']['email']
    return render_template("perfil.html", nomeCadastro=nomeCadastro, emailCadastro=emailCadastro)


@app.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():
    nomeCadastro = session.get("nomeCadastro")
    emailCadastro = session.get("emailCadastro")
    return render_template("configuracoes.html", nomeCadastro=nomeCadastro, emailCadastro=emailCadastro)

@app.route("/seguranca", methods=["GET", "POST"])
def seguranca():
    if "usuario" not in session:
        return jsonify({"mensagem": "Usuário não encontrado"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"Erro ao receber dados"}), 400
    
    senhaAtual = data.get("senhaAtual")
    novaSenha = data.get("novaSenha")
    confirmarSenha = data.get("confirmarSenha")

    if not senhaAtual or not novaSenha or not confirmarSenha:
        return jsonify({"mensagem": "Por favor, preencha todos os campos"})
    
    if novaSenha != confirmarSenha:
        return jsonify({"mensagem": "As senhas não combinam"})
    
    email_usuario = session["usuario"]["email"]
    user = usuarios.query.filter_by(emailCadastro=email_usuario).first()

    if not user:
        return jsonify({"mensagem": "Usuário não existe"})
    
    if not check_password_hash(user.senhaCadastro, senhaAtual):
        return jsonify({"mensagem": "Senha Atual incorreta"})
        

    user.senhaCadastro = generate_password_hash(novaSenha)
    db.session.commit()

    return jsonify({"mensagem": "Senha atualizada com sucesso"})

@app.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        data = request.get_json()

        emailRedefinição = data.get("email")

        if not emailRedefinição:
            return jsonify({"mensagem": "Preencha o campo email por favor"})
        
        user = usuarios.query.filter_by(emailCadastro=emailRedefinição).first()

        if user:
            token = serializer.dumps(emailRedefinição, salt='senha-reset')
            user.token = token
            db.session.commit()

            link = url_for("redefinir_senha", token=token, _external=True)
            msg = EmailMessage()
            msg['Subject'] = "Email para redefinição de senha"
            msg['From'] = "grumelo098@gmail.com"
            msg['To'] = emailRedefinição
            msg.set_content(f"Acesse o link para redefinir sua senha {link}")

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login("grumelo098@gmail.com", 'ourf sgnz wkiw sxse')
                    smtp.send_message(msg)
                return jsonify({"mensagem": "Link de redefinição enviado para o seu email. Por favor verifique."})
            except Exception as e:
                print("Erro ao enviar email", e)
                return jsonify({"mensagem": "Erro ao envir email"})
        else:
            return jsonify({"mensagem": "Email não encontrado"}), 404
    return render_template("esqueceuasenha.html")

@app.route("/redefinir_senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    try:
        email = serializer.loads(token, salt="senha-reset", max_age=3600)
    except:
        return jsonify({"mensagem": "Link inválido ou experirado"}), 400
    
    user = usuarios.query.filter_by(emailCadastro=email).first()

    if request.method == "POST":
        data = request.get_json()
        novaSenha = data.get("novaSenha")
        
        if not novaSenha:
            return jsonify({"mensagem": "Nova Senha obrigatório"}), 400
    
        hashed = generate_password_hash(novaSenha)
        user.senhaCadastro = hashed
        user.confirmarSenha = hashed
        user.token = token
        db.session.commit()

        return jsonify({"mensagem": "Senha redefinida com sucesso!!!"}), 200
    
    return render_template("redefinir_senha.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
