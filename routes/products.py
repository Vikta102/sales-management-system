import logging
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from extensions import db
from models import Product

logger = logging.getLogger(__name__)

products_bp = Blueprint("products", __name__, url_prefix="/products")


def _to_int(value: str, *, default: int | None = None) -> int | None:
    value = (value or "").strip()
    if value == "":
        return default
    return int(value)


def _to_decimal(value: str) -> Decimal:
    value = (value or "").strip()
    if value == "":
        return Decimal("0.00")
    return Decimal(value)


@products_bp.get("/")
@login_required
def list_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("products/list.html", products=products)


@products_bp.get("/new")
@login_required
def new_product():
    return render_template("products/form.html", product=None)


@products_bp.post("/new")
@login_required
def create_product():
    name = (request.form.get("name") or "").strip()
    sku = (request.form.get("sku") or "").strip() or None
    try:
        price = _to_decimal(request.form.get("price") or "")
        stock = _to_int(request.form.get("stock") or "", default=0) or 0
    except (InvalidOperation, ValueError):
        flash("Invalid price or stock value.", "warning")
        return redirect(url_for("products.new_product"))

    if not name:
        flash("Name is required.", "warning")
        return redirect(url_for("products.new_product"))
    if stock < 0:
        flash("Stock cannot be negative.", "warning")
        return redirect(url_for("products.new_product"))
    if price < 0:
        flash("Price cannot be negative.", "warning")
        return redirect(url_for("products.new_product"))

    if Product.query.filter(db.func.lower(Product.name) == name.lower()).first():
        flash("Product name already exists.", "danger")
        return redirect(url_for("products.new_product"))
    if sku and Product.query.filter(db.func.lower(Product.sku) == sku.lower()).first():
        flash("SKU already exists.", "danger")
        return redirect(url_for("products.new_product"))

    product = Product(name=name, sku=sku, price=price, stock=stock)
    db.session.add(product)
    db.session.commit()
    logger.info("Product created: %s", name)
    flash("Product created.", "success")
    return redirect(url_for("products.list_products"))


@products_bp.get("/<int:product_id>/edit")
@login_required
def edit_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    return render_template("products/form.html", product=product)


@products_bp.post("/<int:product_id>/edit")
@login_required
def update_product(product_id: int):
    product = Product.query.get_or_404(product_id)

    name = (request.form.get("name") or "").strip()
    sku = (request.form.get("sku") or "").strip() or None
    try:
        price = _to_decimal(request.form.get("price") or "")
        stock = _to_int(request.form.get("stock") or "", default=0) or 0
    except (InvalidOperation, ValueError):
        flash("Invalid price or stock value.", "warning")
        return redirect(url_for("products.edit_product", product_id=product_id))

    if not name:
        flash("Name is required.", "warning")
        return redirect(url_for("products.edit_product", product_id=product_id))
    if stock < 0 or price < 0:
        flash("Stock and price must be non-negative.", "warning")
        return redirect(url_for("products.edit_product", product_id=product_id))

    existing_name = Product.query.filter(
        db.func.lower(Product.name) == name.lower(), Product.id != product.id
    ).first()
    if existing_name:
        flash("Another product already uses that name.", "danger")
        return redirect(url_for("products.edit_product", product_id=product_id))
    if sku:
        existing_sku = Product.query.filter(
            db.func.lower(Product.sku) == sku.lower(), Product.id != product.id
        ).first()
        if existing_sku:
            flash("Another product already uses that SKU.", "danger")
            return redirect(url_for("products.edit_product", product_id=product_id))

    product.name = name
    product.sku = sku
    product.price = price
    product.stock = stock
    db.session.commit()
    logger.info("Product updated: %s", product.id)
    flash("Product updated.", "success")
    return redirect(url_for("products.list_products"))


@products_bp.post("/<int:product_id>/delete")
@login_required
def delete_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    logger.info("Product deleted: %s", product.id)
    flash("Product deleted.", "info")
    return redirect(url_for("products.list_products"))
