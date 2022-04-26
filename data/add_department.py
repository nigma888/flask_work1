from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, EmailField
from wtforms.validators import DataRequired


class AddDepartmentForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField('Chief id', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Department Email', validators=[DataRequired()])

    submit = SubmitField('Submit')
