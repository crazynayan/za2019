from typing import List

from flask import Response, render_template, flash, redirect, url_for

from flask_app.auth.auth import cookie_login_required
from flask_app.group_select import bp
from flask_app.group_select.selection import SelectionForm, Group


@bp.route("/groups/<group_id>/selection", methods=["GET", "POST"])
@cookie_login_required
def selection(group_id: str) -> Response:
    group = Group.get_by_id(group_id)
    if not group:
        flash("error in retrieving group")
        return redirect(url_for("group_select.view_groups"))
    form = SelectionForm(group)
    if not form.validate_on_submit():
        form.flash_form_errors()
        return render_template("selection-players.html", form=form)
    form.update()
    return redirect(url_for("group_select.view_groups"))


@bp.route("/groups")
@cookie_login_required
def view_groups() -> Response:
    groups: List[Group] = Group.objects.order_by("player_count", Group.objects.ORDER_DESCENDING).get()
    selected = sum(1 if group.selection else 0 for group in groups)
    return render_template("selection-groups.html", groups=groups, selected=selected)
