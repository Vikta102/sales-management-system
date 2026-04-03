import logging
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Product, Sale

logger = logging.getLogger(__name__)

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


def _to_int(value: str) -> int:
    return int((value or "").strip())


def _to_decimal(value: str) -> Decimal:
    return Decimal((value or "").strip())


@sales_bp.get("/")
@login_required
def list_sales():
    sales = Sale.query.order_by(Sale.sale_date.desc(), Sale.created_at.desc()).all()
    return render_template("sales/list.html", sales=sales)


@sales_bp.get("/new")
@login_required
def new_sale():
    products = Product.query.order_by(Product.name.asc()).all()
    return render_template("sales/form.html", products=products, today=date.today().isoformat())


@sales_bp.post("/new")
@login_required
def create_sale():
    try:
        product_id = _to_int(request.form.get("product_id") or "")
        quantity = _to_int(request.form.get("quantity") or "")
        unit_price = _to_decimal(request.form.get("unit_price") or "")
        sale_date_str = (request.form.get("sale_date") or "").strip()
        sale_date_val = date.fromisoformat(sale_date_str) if sale_date_str else date.today()
    except (ValueError, InvalidOperation):
        flash("Invalid input. Check product, quantity, price, and date.", "warning")
        return redirect(url_for("sales.new_sale"))

    if quantity <= 0:
        flash("Quantity must be greater than 0.", "warning")
        return redirect(url_for("sales.new_sale"))
    if unit_price < 0:
        flash("Unit price cannot be negative.", "warning")
        return redirect(url_for("sales.new_sale"))

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("sales.new_sale"))

    if product.stock is not None and product.stock < quantity:
        flash(f"Insufficient stock. Available: {product.stock}.", "warning")
        return redirect(url_for("sales.new_sale"))

    sale = Sale(
        product_id=product.id,
        user_id=current_user.id,
        quantity=quantity,
        unit_price=unit_price,
        sale_date=sale_date_val,
    )
    db.session.add(sale)
    product.stock = (product.stock or 0) - quantity
    db.session.commit()

    logger.info("Sale recorded: sale_id=%s product_id=%s qty=%s", sale.id, product.id, quantity)
    flash("Sale recorded.", "success")
    return redirect(url_for("sales.list_sales"))


@sales_bp.post("/<int:sale_id>/delete")
@login_required
def delete_sale(sale_id: int):
    sale = Sale.query.get_or_404(sale_id)
    if sale.product and sale.product.stock is not None:
        sale.product.stock = (sale.product.stock or 0) + (sale.quantity or 0)
    db.session.delete(sale)
    db.session.commit()
    logger.info("Sale deleted: %s", sale_id)
    flash("Sale deleted.", "info")
    return redirect(url_for("sales.list_sales"))
