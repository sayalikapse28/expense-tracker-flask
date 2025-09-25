from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from models.expense import Expense
import csv
import io

expense_bp = Blueprint("expense", __name__, url_prefix="/expense")

@expense_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        category = (request.form.get("category") or "").strip()
        amount = request.form.get("amount")
        note = (request.form.get("note") or "").strip()
        spent_on_str = request.form.get("spent_on")

        if not category or not amount:
            flash("Category and amount are required.", "danger")
            return redirect(url_for("expense.add"))

        try:
            amount_val = float(amount)
        except ValueError:
            flash("Amount must be a number.", "danger")
            return redirect(url_for("expense.add"))

        try:
            spent_on = datetime.strptime(spent_on_str, "%Y-%m-%d").date() if spent_on_str else None
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("expense.add"))

        exp = Expense(
            category=category,
            amount=amount_val,
            note=note or None,
            spent_on=spent_on,
            user_id=current_user.id
        )
        db.session.add(exp)
        db.session.commit()
        flash("Expense added.", "success")
        return redirect(url_for("dashboard.home"))
    return render_template("add_expense.html")

@expense_bp.route("/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit(expense_id):
    exp = Expense.query.get_or_404(expense_id)
    if exp.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        category = (request.form.get("category") or "").strip()
        amount = request.form.get("amount")
        note = (request.form.get("note") or "").strip()
        spent_on_str = request.form.get("spent_on")

        if not category or not amount:
            flash("Category and amount are required.", "danger")
            return redirect(url_for("expense.edit", expense_id=expense_id))

        try:
            exp.amount = float(amount)
        except ValueError:
            flash("Amount must be a number.", "danger")
            return redirect(url_for("expense.edit", expense_id=expense_id))

        try:
            exp.spent_on = datetime.strptime(spent_on_str, "%Y-%m-%d").date() if spent_on_str else exp.spent_on
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("expense.edit", expense_id=expense_id))

        exp.category = category
        exp.note = note or None
        db.session.commit()
        flash("Expense updated.", "success")
        return redirect(url_for("dashboard.home"))

    return render_template("edit_expense.html", expense=exp)

@expense_bp.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete(expense_id):
    exp = Expense.query.get_or_404(expense_id)
    if exp.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("dashboard.home"))
    db.session.delete(exp)
    db.session.commit()
    flash("Expense deleted.", "info")
    return redirect(url_for("dashboard.home"))

@expense_bp.route("/export_csv")
@login_required
def export_csv():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.spent_on.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["Date", "Category", "Amount", "Note"])
    for e in expenses:
        cw.writerow([e.spent_on, e.category, e.amount, e.note or ""])
    output = si.getvalue().encode("utf-8")
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=expenses.csv"}
    )
