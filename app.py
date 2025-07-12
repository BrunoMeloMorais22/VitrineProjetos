from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from datetime import timedelta
import smtplib
import requests
import mysql.connector
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from itsdangerous import Serializer, URLSafeTimedSerializer

app = Flask(__name__)

app.secret_key = "corinthians"
serializer = URLSafeTimedSerializer(app.secret_key)

RECAPTCHA_SITE_KEY = "6Levt30rAAAAAJJzfOzcnPSFrx5RPHj2yp2qMVq5"
RECAPTCHA_SECRET_KEY = "6Levt30rAAAAAMRCl0z4lAtpOHRt8tgcH9be-4_S"

basedir = os.path.abspath(os.path.dirname(__file__))

app.permanent_session_lifetime = timedelta(minutes=30)

CORS(app, supports_credentials=True)

def get_projetos_com_dono():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="passport",
        database="vitrine"
    )
    cursor = conexao.cursor(dictionary=True)
    query = """
    SELECT
      projetos.id,
      projetos.nomeProjeto,
      projetos.descricaoProjeto,
      projetos.linguagens,
      projetos.imagem,
      projetos.link,
      projetos.dono_id,
      usuarios.nomeCadastro AS nomeDono
    FROM projetos
    JOIN usuarios ON projetos.dono_id = usuarios.id;
    """
    cursor.execute(query)
    projetos = cursor.fetchall() 
    cursor.close()
    conexao.close()
    return projetos

def conectar():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "passport",
        database = "vitrine"
    )

@app.route("/")
def index():
    projetos = get_projetos_com_dono()
    return render_template("index.html", projetos=projetos)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html", site_key=RECAPTCHA_SITE_KEY)
    
    try:
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

        verificacao = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": RECAPTCHA_SECRET_KEY, "response": recaptcha_response}
        ).json()

        if not verificacao.get("success"):
            return jsonify({"mensagem": "ReCAPTCHA inválido"})

        if not nomeCadastro or not emailCadastro or not senhaCadastro or not confirmarSenha:
            return jsonify({"mensagem": "Preencha todos os campos"})

        if senhaCadastro != confirmarSenha:
            return jsonify({"mensagem": "As senhas não combinam"})

        con = conectar()
        cur = con.cursor(dictionary=True)
        
        cur.execute("SELECT * FROM usuarios WHERE emailCadastro = %s", (emailCadastro,))
        user_exists = cur.fetchone()

        if user_exists:
            return jsonify({"mensagem": "Email já cadastrado. Faça login"})

        hashed_senha = generate_password_hash(senhaCadastro)

        cur.execute(
            "INSERT INTO usuarios (nomeCadastro, emailCadastro, senhaCadastro) VALUES (%s, %s, %s)",
            (nomeCadastro, emailCadastro, hashed_senha)
        )
        con.commit()

        session['usuario'] = emailCadastro

        return jsonify({"mensagem": "Usuário cadastrado com sucesso!"})

    except Exception as e:
        print("Erro no backend:", e)
        return jsonify({"mensagem": "Erro no servidor"}), 500

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
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()
    email = data.get("emailLogin")
    senha = data.get("senhaLogin")

    con = conectar()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE emailCadastro = %s", (email,))
    user = cur.fetchone()
    con.close()

    if user and check_password_hash(user["senhaCadastro"], senha):
        session['usuario'] = {"id": user['id'], "nome": user['nomeCadastro'], "email": user['emailCadastro']}
        return jsonify({"mensagem": "Login efetuado com sucesso"})

    return jsonify({"mensagem": "Email ou senha incorretos"}), 401

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

    nomeProjeto = request.form.get("nomeProjeto")
    descricaoProjeto = request.form.get("descricaoProjeto")
    link = request.form.get("link")
    linguagens = request.form.get("linguagens")
    imagem = request.files.get("imagem")

    if not nomeProjeto or not descricaoProjeto or not linguagens:
        return jsonify({"mensagem": "Preencha todos os campos"}), 400

    nome_imagem = imagem.filename
    caminho = os.path.join("static/uploads", nome_imagem)
    imagem.save(caminho)

    dono_id = session['usuario']['id']
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO projetos (nomeProjeto, descricaoProjeto, link, linguagens, imagem, dono_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nomeProjeto, descricaoProjeto, link, linguagens, nome_imagem, dono_id))
    con.commit()
    con.close()

    return jsonify({"mensagem": "Projeto cadastrado com sucesso"})


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

@app.route("/seguranca", methods=["POST"])
def seguranca():
    if "usuario" not in session:
        return jsonify({"mensagem": "Usuário não encontrado"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"mensagem": "Erro ao receber dados"}), 400

    senhaAtual = data.get("senhaAtual")
    novaSenha = data.get("novaSenha")
    confirmarSenha = data.get("confirmarSenha")

    if not senhaAtual or not novaSenha or not confirmarSenha:
        return jsonify({"mensagem": "Por favor, preencha todos os campos"})

    if novaSenha != confirmarSenha:
        return jsonify({"mensagem": "As senhas não combinam"})

    email_usuario = session["usuario"]["email"]
    con = conectar()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE emailCadastro = %s", (email_usuario,))
    user = cur.fetchone()

    if not user:
        con.close()
        return jsonify({"mensagem": "Usuário não existe"})

    if not check_password_hash(user["senhaCadastro"], senhaAtual):
        con.close()
        return jsonify({"mensagem": "Senha Atual incorreta"})

    nova_hash = generate_password_hash(novaSenha)
    cur.execute("UPDATE usuarios SET senhaCadastro = %s WHERE emailCadastro = %s", (nova_hash, email_usuario))
    con.commit()
    con.close()

    return jsonify({"mensagem": "Senha atualizada com sucesso"})


@app.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"mensagem": "Preencha o campo email por favor"})

        con = conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE emailCadastro = %s", (email,))
        user = cur.fetchone()

        if user:
            token = serializer.dumps(email, salt='senha-reset')
            link = url_for("redefinir_senha", token=token, _external=True)

            msg = EmailMessage()
            msg['Subject'] = "Email para redefinição de senha"
            msg['From'] = "grumelo098@gmail.com"
            msg['To'] = email
            msg.set_content(f"Acesse o link para redefinir sua senha: {link}")

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login("grumelo098@gmail.com", 'ourf sgnz wkiw sxse')
                    smtp.send_message(msg)
                return jsonify({"mensagem": "Link de redefinição enviado para o seu email."})
            except Exception as e:
                print("Erro ao enviar email", e)
                return jsonify({"mensagem": "Erro ao enviar email"})
        else:
            return jsonify({"mensagem": "Email não encontrado"}), 404

    return render_template("esqueceuasenha.html")

@app.route("/redefinir_senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    try:
        email = serializer.loads(token, salt="senha-reset", max_age=3600)
    except:
        return jsonify({"mensagem": "Link inválido ou expirado"}), 400

    if request.method == "POST":
        data = request.get_json()
        novaSenha = data.get("novaSenha")

        if not novaSenha:
            return jsonify({"mensagem": "Nova senha obrigatória"}), 400

        hash_nova = generate_password_hash(novaSenha)
        con = conectar()
        cur = con.cursor()
        cur.execute("UPDATE usuarios SET senhaCadastro = %s WHERE emailCadastro = %s", (hash_nova, email))
        con.commit()
        con.close()

        return jsonify({"mensagem": "Senha redefinida com sucesso!"}), 200

    return render_template("redefinir_senha.html")


@app.route("/denunciar/<int:projeto_id>", methods=["POST"])
def denunciar(projeto_id):
    if 'usuario' not in session:
        return jsonify({"mensagem": "Usuário não autenticado"}), 401

    data = request.get_json()
    motivo = data.get("motivo")
    email_usuario = session['usuario']['email']

    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO denuncia (projeto_id, email_usuario, motivo) VALUES (%s, %s, %s)",
                (projeto_id, email_usuario, motivo))
    con.commit()
    con.close()

    return jsonify({"mensagem": "Denúncia enviada com sucesso"})

@app.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")

@app.route("/enviar_ajuda", methods=["POST"])
def enviar_ajuda():
    if "usuario" not in session:
        return jsonify({"mensagem": "Por favor, você precisa estar logado para enviar a mensagem"})
    
    data = request.get_json()
    if not data:
        return jsonify({"mensagem": "Dados não recebidos"})
    
    mensagem = data.get("mensagem")

    if not mensagem:
        return jsonify({"mensagem": "Mensagem Vazia"})
    
    try:
        con = conectar()
        cursor = con.cursor()
        sql = "INSERT INTO mensagem_ajuda(id_usuario, mensagem) VALUES(%s, %s)"
        cursor.execute(sql, (session["usuario"]["id"], mensagem))
        con.commit()
        cursor.close()
        con.close()

        return jsonify({"mensagem": "Mensagem enviada com sucesso"})
    except Exception as e:
        print("Erro ao salvar mensagem", e)
        return jsonify({"mensagem": "Erro ao salvar mensagem"})

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, port=8000)
