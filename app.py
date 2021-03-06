# aplicação de exemplo

from flask import Flask, request, Response, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import filtros

# caso precise customizar pasta onde ficam templates
#app = Flask(__name__, template_folder="modelos")

# pegando referência ao flask e customizando pasta pra conteúdo estático, como css..
app = Flask(__name__, 
    static_folder="public")

#Bootstrap(app)


#chave precisa ser criada pra trabalhar com sessão...
app.config["SECRET_KEY"] = "secret" # pra produção, precisa ser tratada.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.jinja_env.filters["formatdate"] = filtros.format_date

login_manager = LoginManager(app)

@login_manager.user_loader
def current_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(84), nullable= False)
    email = db.Column(db.String(84),nullable= False, unique= True, index= True)
    password = db.Column(db.String(255), nullable=False)
    # user profile
    profile = db.relationship('Profile', backref='user', uselist=False)

    def __str__(self):
        return self.name
    
class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key= True)
    photo = db.Column(db.Unicode(124), nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def __str__(self):
        return self.name


# LOGIN/ CADASTRO DE USUÁRIO

@app.route("/")
def index():
    #return "<a href='/posts/3'>Posts</a>"
    users = User.query.all() # select * from users;
    return render_template("users.html", users=users)

@app.route("/user/<int:id>")
@login_required
def unique(id):
    user = User.query.get(id)
    return render_template("user.html", user=user)

@app.route("/user/delete/<int:id>")
def delete(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if(request.method=="POST"):
        user = User()
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.password = generate_password_hash(request.form["password"])

        db.session.add(user)
        db.session.commit()

        return redirect( url_for("index"))

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if(request.method=="POST"):
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form["remember"]

        user = User.query.filter_by(email=email).first()
        if(not user):
            flash("Credenciais inválidas! Usuário não localizado.")
            render_template(url_for("login"))
        if(not check_password_hash(user.password, password)):
            flash("Credenciais inválidas! Senha não confere.")
            render_template(url_for("login"))
        login_user(user, remember=remember, duration=timedelta(days=7))        

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("login.html")


# USO DE TEMPLATES
@app.route("/templates")
def templates():
    
    # loop python
    #for item in range(1,10):
    #    print(item)

    user_page = True

    return render_template("index.html", user_page= user_page)
@app.route("/users")
def users():

    usuarios = [{
        "name": "Joaquim José da Silva Xavier",
        "age": 65,
        "email": "tiradentes@gmail.com",
        "active": True,
        "since": datetime.utcnow()
    },
    {
        "name": "maria joaquina da silva xavier",
        "age": 60,
        "email": "maria@gmail.com",
        "active": False, 
        "since": datetime.utcnow()
    }]

    flash(message="testando envio de mensagens flash...", category="success")

    return render_template("usuarios.html", users=usuarios)


# ROTAS / HTTP
@app.route("/redirect")
def redirecionar():
    #return redirect("/response")
    return redirect(url_for("response"))


@app.route("/response")
def response():
    return render_template("response.html")

@app.route("/posts/<int:id>")
def posts(id):
    titulo = request.args.get("titulo")
    data = dict(
        path = request.path,
        referrer = request.referrer,
        content_type = request.content_type,
        method = request.method,
        titulo = titulo,
        id = id if id else 0
    )
    return data



if(__name__ == "__main__"):
    app.run(debug=True)