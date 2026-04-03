from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from extensions import db
from models import Product, Sale

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
@login_required
def index():
    product_count = db.session.query(func.count(Product.id)).scalar() or 0
    sales_count = db.session.query(func.count(Sale.id)).scalar() or 0

    revenue = (
        db.session.query(func.coalesce(func.sum(Sale.unit_price * Sale.quantity), 0))
        .scalar()
        or Decimal("0.00")
    )

    return render_template(
        "dashboard.html",
        product_count=product_count,
        sales_count=sales_count,
        revenue=revenue,
    )
