import os
import secrets

from flask import Flask, render_template, request

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
from utils.validators import AVAILABILITY_OPTIONS, FilterValidationError


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    )
    if test_config:
        app.config.update(test_config)

    app.jinja_env.filters["clp"] = format_clp

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
