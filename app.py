from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    price = db.Column(db.Float)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_first_request
def setup():
    db.create_all()

    if Product.query.count() == 0:
        db.session.add(Product(name="Teclado Gamer", price=99.90))
        db.session.add(Product(name="Mouse RGB", price=59.90))
        db.session.add(Product(name="Headset", price=149.90))
        db.session.commit()


# ROTAS
@app.route("/")
def index():
    products = Product.query.all()
    cart_ids = session.get("cart", [])
    cart_items = Product.query.filter(Product.id.in_(cart_ids)).all() if cart_ids else []
    total = sum([item.price for item in cart_items])

    return render_template("index.html", products=products, cart_items=cart_items, total=total)

# CADASTRO
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        # Verifica se o usuário existe
        if User.query.filter_by(username=username).first():
            flash("Usuário já existe.")
            return redirect(url_for("register"))

        # Cria novo usuário
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Conta criada com sucesso! Agora faça login.")
        return redirect(url_for("login"))

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Credenciais inválidas.")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# CARRINHO
@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", [])
    cart.append(product_id)
    session["cart"] = cart
    return redirect("/")


@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", [])
    if product_id in cart:
        cart.remove(product_id)
    session["cart"] = cart
    return redirect("/")


@app.route("/checkout", methods=["POST"])
def checkout():
    session["cart"] = []

    return """
    <script>
        alert("Compra finalizada com sucesso!");
        window.location.href = "/";
    </script>
    """



# COMPRA DIRETA
@app.route("/buy/<int:product_id>")
@login_required
def buy(product_id):
    order = Order(user_id=current_user.id, product_id=product_id)
    db.session.add(order)
    db.session.commit()

    flash("Pedido realizado com sucesso!")
    return redirect(url_for("index"))


# INICIALIZAÇÃO DO SERVIDOR
if __name__ == "__main__":
    app.run(debug=True)
