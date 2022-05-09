from app import db, login_manager
from flask import current_app
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# МОДЕЛИ. БАЗА ДАННЫХ


fans_tickets = db.Table(
    'fans_tickets',
    db.Column('fan_id', db.Integer, db.ForeignKey('fans.id')),
    db.Column('ticket_id', db.String(64), db.ForeignKey('tickets.ticket_id'), unique=True)
)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    ticket_id = db.Column(db.String(64), primary_key=True)
    t_status = db.Column(db.Boolean, nullable=False, default=True)
    price = db.Column(db.Integer)
    p_id = db.Column(db.String(32), db.ForeignKey('places.place_id'))
    m_id = db.Column(db.Integer, db.ForeignKey('matches.match_id'))
    buy_tickets = db.relationship('Fan', secondary=fans_tickets, backref='tickets', lazy='dynamic')

    def __repr__(self):
        return f"Матч: {self.match.opponent}, {self.match.m_datetime.strftime('%d.%m.%Y, %H:%M:%S')}. \n" \
               f"Место: сектор {self.place.sector} ряд {self.place.row} место {self.place.place}"


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('fans.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.r_id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    r_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30), unique=True)
    description = db.Column(db.String(150))

    def __str__(self):
        return self.name


class Fan(db.Model, UserMixin):
    __tablename__ = 'fans'
    id = db.Column(db.Integer, db.ForeignKey('fans_passport.number'), primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, index=True)  # было 64
    password_hash = db.Column(db.String(128))
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.r_id'), default=2)
    confirmed = db.Column(db.Boolean, default=False)
    buy_tickets = db.relationship('Ticket', secondary=fans_tickets, backref='fans', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f"Имя: {self.full_name}"

    # Flask - Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_administrator(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True


class FanID(db.Model):
    __tablename__ = 'fans_passport'
    number = db.Column(db.Integer, primary_key=True)
    f_status = db.Column(db.Boolean, nullable=False, default=True)
    full_name = db.Column(db.String(128), nullable=False)
    f_id = db.relationship('Fan', backref='id_fan')


class Stadium(db.Model):
    __tablename__ = 'places'
    place_id = db.Column(db.String(32), primary_key=True)
    sector = db.Column(db.String(8), nullable=False)
    row = db.Column(db.Integer, nullable=False)
    place = db.Column(db.Integer, nullable=False)
    p_tickets = db.relationship('Ticket', backref='place')

    def __repr__(self):
        return f"{self.place_id}"

    # def __str__(self):
    #     return self.sector


class Match(db.Model):
    __tablename__ = 'matches'
    match_id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(32), nullable=False)
    tournament = db.Column(db.String(64))
    m_datetime = db.Column(db.DateTime(), nullable=False)
    m_tickets = db.relationship('Ticket', backref='match')

    def __repr__(self):
        return f"Матч {self.match_id}: {self.opponent}, {self.tournament}, " \
               f"{self.m_datetime.strftime('%d.%m.%Y, %H:%M:%S')}"


@login_manager.user_loader
def load_user(user_id):
    return Fan.query.get(int(user_id))
