from app import db, f_admin
from . import admin_bp
from flask import redirect, url_for, request, render_template, flash
from .forms import AddMatchForm
from ..models import Fan, Match, Role, FanID, Stadium, Ticket
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_security import SQLAlchemyUserDatastore, current_user, login_required, roles_required
from datetime import datetime
from pytz import timezone


# Админ

@admin_bp.route('/add_match', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def add_match():
    form = AddMatchForm()
    time_now = datetime.now(timezone('Europe/Moscow'))
    all_matches = Match.query.filter(Match.m_datetime >= time_now).order_by(Match.m_datetime).all()
    archive_matches = Match.query.filter(Match.m_datetime <= time_now).order_by(Match.m_datetime).all()
    if form.validate_on_submit():
        try:
            match = Match.query.filter_by(opponent=form.opponent.data, tournament=form.tournament.data,
                                          m_datetime=form.m_datetime.data).first()
            if match is None:
                match = Match(opponent=form.opponent.data, tournament=form.tournament.data,
                              m_datetime=form.m_datetime.data)
                db.session.add(match)
                data_places = Stadium.query.all()
                for place in data_places:
                    ticket = Ticket(ticket_id=f"{match.match_id}{place.place_id}", price=form.price.data,
                                    p_id=place.place_id, m_id=match.match_id)
                    db.session.add(ticket)
                db.session.commit()
            else:
                flash("Матч существует")
        except:
            flash("Недопустимые данные")
        return redirect(url_for('admin_bp.add_match'))
    print(form.errors)
    return render_template('admin/match_form.html', form=form, all_matches=all_matches, archive_matches=archive_matches)


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        flash("Нужны права администратора")
        return redirect(url_for('auth.login', next=request.url))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


class FanAdminView(AdminMixin, ModelView):
    column_filters = ('full_name', 'phone_number', 'email', 'roles', 'confirmed')

    def get_edit_form(self):
        form_class = super(FanAdminView, self).get_edit_form()
        del form_class.password_hash
        return form_class

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password(form.password_hash.data)


class TicketAdminView(AdminMixin, ModelView):
    column_filters = ('t_status', 'price', 'm_id', 'p_id')


class FanIDAdminView(AdminMixin, ModelView):
    column_filters = ('number', 'f_status', 'full_name')


class MatchAdminView(AdminMixin, ModelView):
    column_filters = ('match_id', 'opponent', 'tournament', 'm_datetime')

    def get_edit_form(self):
        form_class = super(MatchAdminView, self).get_edit_form()
        del form_class.m_tickets
        return form_class

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        return redirect(url_for('admin_bp.add_match'))

    def on_model_delete(self, model):
        db.session.query(Ticket).filter_by(m_id=model.match_id).delete()


f_admin.add_view(FanAdminView(Fan, db.session))
f_admin.add_view(MatchAdminView(Match, db.session))
f_admin.add_view(FanIDAdminView(FanID, db.session))
f_admin.add_view(TicketAdminView(Ticket, db.session))


user_datastore = SQLAlchemyUserDatastore(db, Fan, Role)
