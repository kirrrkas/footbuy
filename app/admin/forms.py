from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeLocalField, IntegerField
from wtforms.validators import DataRequired


class AddMatchForm(FlaskForm):
    opponent = StringField('Соперник', validators=[DataRequired()])
    tournament = StringField('Турнир')
    m_datetime = DateTimeLocalField('Дата и время проведения', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    submit = SubmitField('Добавить')