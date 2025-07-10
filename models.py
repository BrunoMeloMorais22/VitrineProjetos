from db import db
from datetime import datetime
class usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomeCadastro = db.Column(db.String(100))
    emailCadastro = db.Column(db.String(100), unique=True)
    senhaCadastro = db.Column(db.String(200))
    projetos = db.relationship('projetos', backref='dono', lazy=True)

class projetos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomeProjeto = db.Column(db.String(100))
    descricaoProjeto = db.Column(db.Text)
    link = db.Column(db.String(300))
    linguagens = db.Column(db.String(100))
    imagem = db.Column(db.String(100))
    dono_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Denuncia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projetos.id'), nullable=False)
    email_usuario = db.Column(db.String(120)) 
    motivo = db.Column(db.String(255), nullable=False)
    data_denuncia = db.Column(db.DateTime, default=datetime.utcnow)

    projeto = db.relationship('projetos', backref='denuncias')
