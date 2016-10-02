from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.fields import SelectMultipleField, HiddenField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import  Length, Email, InputRequired, EqualTo
from wtforms import widgets


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    http://wtforms.readthedocs.io/en/1.0.4/specific_problems.html#specialty-field-tricks
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SymptomsForm(Form):
    symptoms_list = MultiCheckboxField('Symptoms')


class ConditionsForm(Form):
    conditions_list = MultiCheckboxField('Conditions')


class RisksForm(Form):
    risks_list = MultiCheckboxField('Risks')


class SearchPhrasesForm(Form):
    phrasebox = StringField('phrasebox')
    phrases = HiddenField('phrases')


class RegistrationForm(Form):
    name = StringField('name', validators=[InputRequired()])
    email = EmailField('email', validators=[Email(), InputRequired()])
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    age = IntegerField('age')
    locality = StringField('locality', validators=[InputRequired()])
    gender = SelectField('gender', choices=[('female', 'Female'), ('male', 'Male')])


class LoginForm(Form):
    email = EmailField('Email', validators=[Email(), InputRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class SearchFamilyForm(Form):
    members = SelectField("members")
    my_members = MultiCheckboxField('My Family')


class SearchDoctorForm(Form):
    doctortype = StringField('doctortype', validators=[InputRequired()])
