import os
import secrets

from flask import Flask, render_template

from services.catalog_service import (
    get_categories,
    get_featured_products,
    get_product_by_id,
    get_products,
)
from utils.formatting import format_clp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    )
    if test_config:
        app.config.update(test_config)

    app.jinja_env.filters["clp"] = format_clp

    @app.get("/")
    def home():
        return render_template("home.html", products=get_featured_products())

    @app.get("/productos")
    def products():
        return render_template(
            "products.html",
            products=get_products(),
            categories=get_categories(),
        )

    @app.get("/productos/<int:product_id>")
    def product_detail(product_id):
        product = get_product_by_id(product_id)
        if product is None:
            return render_template("404.html"), 404
        return render_template("product_detail.html", product=product)

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

