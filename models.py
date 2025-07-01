from db import db


class usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomeCadastro = db.Column(db.String(100), nullable=False, unique=True)
    emailCadastro = db.Column(db.String(100), nullable=False)
    senhaCadastro = db.Column(db.String(200), nullable=False)

class projetos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomeProjeto = db.Column(db.String(100), nullable=False, unique=True)
    descricaoProjeto = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)
    linguagens = db.Column(db.String(200))
    imagem = db.Column(db.String(225))
    nomePessoaProjeto = db.Column(db.String(225))
    dono_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))



    