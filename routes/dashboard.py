from flask import Blueprint, render_template, request
from flask_login import current_user
from collections import defaultdict
from datetime import date
from sqlalchemy import func
from models.expense import Expense

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    expenses = []
    by_category = defaultdict(float)
    by_month = defaultdict(float)

    category_filter = (request.args.get("category") or "").strip()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Summary metrics
    today_total = 0.0
    month_total = 0.0
    overall_total = 0.0

    if current_user.is_authenticated:
        # Base query for table + charts with filters
        query = Expense.query.filter_by(user_id=current_user.id)
        if category_filter:
            query = query.filter(Expense.category.ilike(f"%{category_filter}%"))
        if start_date:
            query = query.filter(Expense.spent_on >= start_date)
        if end_date:
            query = query.filter(Expense.spent_on <= end_date)

        expenses = query.order_by(Expense.spent_on.desc()).all()

        # Chart aggregations from filtered list
        for e in expenses:
            by_category[e.category] += e.amount
            key = e.spent_on.strftime("%Y-%m") if e.spent_on else "Unknown"
            by_month[key] += e.amount

        # Summary metrics (not affected by the filter; always for current user)
        # Today
        today = date.today()
        today_q = Expense.query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)) \
                               .filter_by(user_id=current_user.id) \
                               .filter(Expense.spent_on == today)
        today_total = float(today_q.scalar() or 0.0)

        # This month
        month_q = Expense.query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)) \
                               .filter_by(user_id=current_user.id) \
                               .filter(func.strftime('%Y-%m', Expense.spent_on) == today.strftime('%Y-%m'))
        # NOTE: func.strftime works on SQLite. For Postgres, switch to date_trunc or EXTRACT.
        month_total = float(month_q.scalar() or 0.0)

        # Overall
        overall_q = Expense.query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)) \
                                 .filter_by(user_id=current_user.id)
        overall_total = float(overall_q.scalar() or 0.0)

    category_labels = list(by_category.keys())
    category_values = [round(v, 2) for v in by_category.values()]
    month_labels = sorted(by_month.keys())
    month_values = [round(by_month[m], 2) for m in month_labels]

    return render_template(
        "dashboard.html",
        expenses=expenses,
        category_labels=category_labels,
        category_values=category_values,
        month_labels=month_labels,
        month_values=month_values,
        category_filter=category_filter,
        start_date=start_date,
        end_date=end_date,
        today_total=today_total,
        month_total=month_total,
        overall_total=overall_total
    )
