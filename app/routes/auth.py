"""Authentication: admin login and customer register/login.

Two separate login flows by design — an admin account and a customer
account are different things, and mixing their login views would let a
mistaken redirect leak which kind of page a URL protects.
"""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db, limiter
from ..forms.auth import AdminLoginForm, CustomerLoginForm, CustomerRegisterForm
from ..models.base import utcnow
from ..models.customer import Customer
from ..models.enums import UserRole
from ..models.user import User
from ..utils.security import normalise_mobile, safe_next_url

bp = Blueprint("auth", __name__)


def _find_admin(identifier: str) -> User | None:
    identifier = identifier.strip()
    query = User.query.filter(User.role == UserRole.ADMIN, User.is_active.is_(True))
    if "@" in identifier:
        return query.filter(User.email == identifier.lower()).first()
    mobile = normalise_mobile(identifier)
    if len(mobile) == 10:
        user = query.filter(User.mobile == mobile).first()
        if user:
            return user
    return query.filter(User.email == identifier.lower()).first()


@bp.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def admin_login():
    if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = _find_admin(form.identifier.data)
        if user and user.check_password(form.password.data):
            user.last_login_at = utcnow()
            db.session.commit()
            login_user(user, remember=form.remember.data)
            flash(_("Welcome back."), "success")
            return redirect(safe_next_url(request.args.get("next"), "admin.dashboard"))
        flash(_("That email/mobile or password is not correct."), "error")

    return render_template("auth/admin_login.html", form=form)


@bp.post("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    flash(_("You have been signed out."), "message")
    return redirect(url_for("public.home"))


@bp.route("/customer/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def customer_login():
    if current_user.is_authenticated and current_user.role == UserRole.CUSTOMER:
        return redirect(url_for("customer.dashboard"))

    form = CustomerLoginForm()
    if form.validate_on_submit():
        mobile = normalise_mobile(form.mobile.data)
        user = User.query.filter(
            User.role == UserRole.CUSTOMER,
            User.mobile == mobile,
            User.is_active.is_(True),
        ).first()
        if user and user.check_password(form.password.data):
            user.last_login_at = utcnow()
            db.session.commit()
            login_user(user, remember=form.remember.data)
            flash(_("Welcome back."), "success")
            return redirect(safe_next_url(request.args.get("next"), "customer.dashboard"))
        flash(_("That mobile number or password is not correct."), "error")

    return render_template("auth/customer_login.html", form=form)


@bp.route("/customer/register", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def customer_register():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))

    form = CustomerRegisterForm()
    if form.validate_on_submit():
        mobile = normalise_mobile(form.mobile.data)
        if User.query.filter_by(mobile=mobile).first():
            flash(
                _("An account with this mobile number already exists. Please sign in instead."),
                "error",
            )
        else:
            user = User(name=form.name.data.strip(), mobile=mobile, role=UserRole.CUSTOMER)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # get user.id

            # Registering creates the account holder's own customer profile too.
            # They can add family members as separate profiles later (Phase 4+).
            profile = Customer(
                name=form.name.data.strip(),
                mobile=mobile,
                address=(form.address.data or "").strip() or None,
                user_id=user.id,
            )
            db.session.add(profile)
            db.session.commit()

            login_user(user)
            flash(_("Welcome to New Star Tailor."), "success")
            return redirect(url_for("customer.dashboard"))

    return render_template("auth/customer_register.html", form=form)


@bp.post("/customer/logout")
@login_required
def customer_logout():
    logout_user()
    flash(_("You have been signed out."), "message")
    return redirect(url_for("public.home"))
