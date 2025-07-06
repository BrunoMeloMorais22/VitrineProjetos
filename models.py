# models.py
from db import db

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
