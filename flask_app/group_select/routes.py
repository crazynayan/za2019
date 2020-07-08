from flask import Response, render_template, flash, redirect, url_for

from flask_app.auth.auth import cookie_login_required
from flask_app.group_select import bp
from flask_app.group_select.selection import SelectionForm


@bp.route("/selection", methods=["GET", "POST"])
@cookie_login_required
def selection() -> Response:
    form = SelectionForm()
    if not form.group:
        flash("Selection complete")
        return redirect(url_for("legacy.home"))
    if not form.validate_on_submit():
        form.flash_form_errors()
        return render_template("selection.html", form=form, title="Group Selection")
    form.update()
    return redirect(url_for("group_select.selection"))
