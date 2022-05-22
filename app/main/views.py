from manage import app
from app import db
from sqlalchemy import desc
from flask_security import login_required, current_user
from . import main
from flask import redirect, url_for, request, render_template, flash, send_from_directory, send_file
from ..models import Match, Ticket, Stadium, Fan
from datetime import datetime
from pytz import timezone
import qrcode
from weasyprint import HTML
import io
import os
###  ДЛЯ ОПЛАТЫ ###
# from app import api, checkout
###


@main.route('/')
def index():
    time_now = datetime.now(timezone('Europe/Moscow'))
    matches = Match.query.filter(Match.m_datetime >= time_now).order_by(Match.m_datetime).all()

    return render_template('main/index.html', matches=matches)


@main.route('/profile')
@login_required
def profile():
    # time_now = datetime.now(timezone('Europe/Moscow'))
    # matches = Match.query.filter(Match.m_datetime >= time_now).order_by(Match.m_datetime).all()
    user = current_user
    tickets = db.session.query(Ticket).join(Ticket.fans).filter(Fan.id == user.id).all()
    return render_template('main/profile.html', tickets=tickets)


@main.route('/match<match>/stadium')
def stadium(match):
    sectors = Ticket.query.join(Stadium).with_entities(Stadium.sector).order_by(Stadium.sector).distinct().all()
    return render_template('main/stadium.html', sectors=sectors, match=match)


@main.route('/match<match>/stadium/<m_sector>', methods=['GET', 'POST'])
def sector(match, m_sector):
    if request.method == 'GET':
        m_rows = db.session.query(Stadium.row).filter(Stadium.sector == m_sector).distinct(). \
            order_by(desc(Stadium.row)).all()
        tickets_sector = db.session.query(Ticket).join(Stadium). \
            with_entities(Stadium.row, Stadium.place, Ticket.ticket_id, Ticket.t_status, Ticket.price). \
            filter(Stadium.sector == m_sector, Ticket.m_id == match).order_by(desc(Stadium.row)).all()
        print(tickets_sector)
        return render_template('main/seats.html', m_rows=m_rows, tickets_sector=tickets_sector, m_sector=m_sector)

    if request.method == 'POST':
        tickets = request.form.getlist('ticket[]')
        tickets = ",".join(tickets)
        if len(tickets) <= 0:
            flash("Вы не выбрали ни одного билета")
            m_rows = db.session.query(Stadium.row).filter(Stadium.sector == m_sector).distinct(). \
                order_by(desc(Stadium.row)).all()
            tickets_sector = db.session.query(Ticket).join(Stadium). \
                with_entities(Stadium.row, Stadium.place, Ticket.ticket_id, Ticket.t_status). \
                filter(Stadium.sector == m_sector, Ticket.m_id == match).order_by(desc(Stadium.row)).all()
            return redirect(url_for('main.sector', m_rows=m_rows, tickets_sector=tickets_sector))
        return redirect(url_for('main.buy_tickets', tickets=tickets))


@main.route('/buy_tickets/<tickets>', methods=['GET', 'POST'])
@login_required
def buy_tickets(tickets):
    user = current_user
    if len(tickets) > 0:
        tickets = set(tickets.split(","))
    sum_price = 0
    tickets_info = []
    for i, tick_id in enumerate(tickets, start=0):
        i = Ticket.query.filter_by(ticket_id=tick_id).first_or_404()
        if i.t_status == False and (i not in user.tickets):
            flash("Билет(ы) уже продан(ы)")
            return redirect(url_for('.index'))
        if i in user.tickets:
            flash("Вы можете просмотреть купленные билеты в личном профиле.")
            return redirect(url_for('.index'))
        i.t_status = False
        i.fans.append(user)
        db.session.add(i)
        sum_price += i.price
        tickets_info.append(i)
        qr = qrcode.make(tick_id)
        filename_qr = app.config['UPLOAD_FOLDER'] + f'qr{tick_id}.png'
        qr.save(filename_qr)
    db.session.commit()
    print(tickets)
    # if request.method == 'POST':
    #     if file and allowed_file(file.filename):
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #         process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
    #         return redirect(url_for('uploaded_file', filename=filename))
    return render_template('main/buy.html', tickets=tickets_info, sum_price=sum_price)

    ###### ДЛЯ ОПЛАТЫ ######
    # amount = 0
    # order_description = ""
    # for i, ticket in enumerate(tickets, start=1):
    #     ticket = Ticket.query.filter_by(ticket_id=ticket).first()
    #     amount += ticket.price
    #     place = Stadium.query.filter_by(place_id=ticket.p_id).first()
    #     order_description += f"Билет {i}: сектор {place.sector} ряд {place.row} место {place.place}; "
    # order_description = order_description.rstrip('; ')
    # data = {
    #     "currency": "RUB",
    #     "amount": str(amount) + "00",
    #     "order_desc": f"{order_description}"
    # }
    # url = checkout.url(data).get('checkout_url')
    # return redirect(url)


@main.route('/ticket_download/<ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_download(ticket_id):
    t_us = Ticket.query.filter_by(ticket_id=ticket_id).first_or_404()
    if t_us in current_user.tickets:
        ticket = db.session.query(Ticket).join(Stadium, Match). \
            with_entities(Match.opponent, Match.m_datetime, Ticket.price, Ticket.ticket_id, Stadium.sector,
                          Stadium.row, Stadium.place). \
            filter(Ticket.ticket_id == ticket_id).first_or_404()
        filename_qr = app.config['UPLOAD_FOLDER'] + f'qr{ticket_id}.png'
        html = render_template('ticket/TICKET_TEMPLATE.html', filename=filename_qr, ticket=ticket)
        file_path_pdf = app.config['DOWNLOAD_FOLDER'] + f'ticket{ticket[3]}.pdf'
        HTML(string=html).write_pdf(file_path_pdf)
        # return send_from_directory(app.config['DOWNLOAD_FOLDER'], f'ticket{ticket[3]}.pdf', as_attachment=True)
        return_data = io.BytesIO()
        with open(file_path_pdf, 'rb') as fo:
            return_data.write(fo.read())
        # (after writing, cursor will be at last byte, so move it to start)
        return_data.seek(0)
        os.remove(filename_qr)
        os.remove(file_path_pdf)
        return send_file(return_data, mimetype='application/pdf',
                         attachment_filename=f'ticket{ticket[3]}.pdf')
    else:
        flash("Вы не купили этот билет.")
        return redirect(url_for('.index'))

