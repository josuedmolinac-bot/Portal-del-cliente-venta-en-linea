import os
import secrets

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from werkzeug.security import check_password_hash

from services.catalog_service import (
    get_categories,
    get_brands,
    get_featured_products,
    get_product_by_id,
    get_products,
    get_search_suggestions,
    filter_products,
)
from utils.formatting import format_clp
from data.demo_user import DEMO_USER
from services.order_service import (
    ORDER_STATES,
    OrderValidationError,
    build_cart,
    create_order,
    get_order_for_user,
    get_orders_for_user,
    validate_quantity,
)
from utils.security import login_required
from utils.validators import (
    AVAILABILITY_OPTIONS,
    FilterValidationError,
    is_valid_order_id,
)

csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("FLASK_HTTPS_ONLY") == "1",
        SESSION_COOKIE_NAME="pdcvel_session",
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    app.jinja_env.filters["clp"] = format_clp
    csrf.init_app(app)

    @app.before_request
    def load_user():
        g.user = DEMO_USER if session.get("user_id") == DEMO_USER["id"] else None

    @app.context_processor
    def inject_navigation_state():
        cart_count = sum(
            quantity for quantity in session.get("cart", {}).values()
            if isinstance(quantity, int)
        )
        return {"current_user": getattr(g, "user", None), "cart_count": cart_count}

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self'; style-src 'self'; "
            "script-src 'none'; frame-ancestors 'self'"
        )
        return response

    @app.get("/")
    def home():
        return render_template(
            "home.html",
            products=get_featured_products(),
            suggestions=get_search_suggestions(),
        )

    @app.get("/productos")
    def products():
        error = None
        status_code = 200
        try:
            visible_products, filters = filter_products(request.args)
        except FilterValidationError as exception:
            visible_products = get_products()
            filters = {
                "q": request.args.get("q", ""),
                "category": "",
                "brand": "",
                "availability": "",
                "min_price": None,
                "max_price": None,
            }
            error = str(exception)
            status_code = 400
        return (
            render_template(
                "products.html",
                products=visible_products,
                categories=get_categories(),
                brands=get_brands(),
                availability_options=AVAILABILITY_OPTIONS,
                suggestions=get_search_suggestions(),
                filters=filters,
                error=error,
            ),
            status_code,
        )

    @app.get("/productos/<int:product_id>")
    def product_detail(product_id):
        product = get_product_by_id(product_id)
        if product is None:
            return render_template("404.html"), 404
        return render_template("product_detail.html", product=product)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.user:
            return redirect(url_for("account"))
        if request.method == "POST":
            email = " ".join(request.form.get("email", "").split()).casefold()
            password = request.form.get("password", "")
            email_matches = email == DEMO_USER["email"].casefold()
            password_matches = check_password_hash(
                DEMO_USER["password_hash"], password
            )
            if email_matches and password_matches:
                session.clear()
                session["user_id"] = DEMO_USER["id"]
                flash("Sesión de demostración iniciada correctamente.", "success")
                return redirect(url_for("account"))
            flash("Correo o contraseña de demostración incorrectos.", "error")
        return render_template("login.html")

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        flash("La sesión se cerró correctamente.", "success")
        return redirect(url_for("home"))

    @app.get("/cuenta")
    @login_required
    def account():
        return render_template("account.html")

    @app.get("/carrito")
    @login_required
    def cart():
        items, total = build_cart(session.get("cart", {}))
        return render_template("cart.html", items=items, total=total)

    @app.post("/carrito/agregar/<int:product_id>")
    @login_required
    def add_to_cart(product_id):
        product = get_product_by_id(product_id)
        if product is None:
            return render_template("404.html"), 404
        try:
            quantity = validate_quantity(request.form.get("quantity", "1"), product)
            cart_data = dict(session.get("cart", {}))
            new_quantity = cart_data.get(str(product_id), 0) + quantity
            cart_data[str(product_id)] = validate_quantity(new_quantity, product)
            session["cart"] = cart_data
            flash(f"{product['name']} fue agregado al carrito.", "success")
        except OrderValidationError as exception:
            flash(str(exception), "error")
        return redirect(url_for("product_detail", product_id=product_id))

    @app.post("/carrito/actualizar/<int:product_id>")
    @login_required
    def update_cart(product_id):
        product = get_product_by_id(product_id)
        if product is None:
            return render_template("404.html"), 404
        try:
            quantity = validate_quantity(request.form.get("quantity"), product)
            cart_data = dict(session.get("cart", {}))
            if str(product_id) not in cart_data:
                return render_template("404.html"), 404
            cart_data[str(product_id)] = quantity
            session["cart"] = cart_data
            flash("Cantidad actualizada.", "success")
        except OrderValidationError as exception:
            flash(str(exception), "error")
        return redirect(url_for("cart"))

    @app.post("/carrito/eliminar/<int:product_id>")
    @login_required
    def remove_from_cart(product_id):
        cart_data = dict(session.get("cart", {}))
        if str(product_id) not in cart_data:
            return render_template("404.html"), 404
        cart_data.pop(str(product_id))
        session["cart"] = cart_data
        flash("Producto eliminado del carrito.", "success")
        return redirect(url_for("cart"))

    @app.post("/carrito/confirmar")
    @login_required
    def confirm_order():
        try:
            order = create_order(g.user["id"], session.get("cart", {}))
        except OrderValidationError as exception:
            flash(str(exception), "error")
            return redirect(url_for("cart"))
        session_orders = list(session.get("orders", []))
        session_orders.append(order)
        session["orders"] = session_orders
        session["cart"] = {}
        flash(f"Pedido {order['id']} confirmado.", "success")
        return redirect(url_for("order_detail", order_id=order["id"]))

    @app.get("/pedidos")
    @login_required
    def orders():
        return render_template(
            "orders.html",
            orders=get_orders_for_user(g.user["id"], session.get("orders", [])),
        )

    @app.get("/pedidos/<order_id>")
    @login_required
    def order_detail(order_id):
        if not is_valid_order_id(order_id):
            return render_template("404.html"), 404
        order = get_order_for_user(
            order_id, g.user["id"], session.get("orders", [])
        )
        if order is None:
            return render_template("404.html"), 404
        return render_template(
            "order_detail.html", order=order, order_states=ORDER_STATES
        )

    @app.errorhandler(CSRFError)
    def csrf_error(_error):
        return render_template(
            "400.html",
            message="La solicitud no pudo validarse. Actualiza la página e inténtalo nuevamente.",
        ), 400

    @app.errorhandler(400)
    def bad_request(_error):
        return render_template(
            "400.html", message="La solicitud contiene datos no válidos."
        ), 400

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return render_template("500.html"), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
