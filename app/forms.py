from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.fields import SelectMultipleField, HiddenField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length, Email, InputRequired, EqualTo
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
    phrases = HiddenField('phrases',
                          validators=[InputRequired(message='You have to enter at least one keyword to continue')])


class RegistrationForm(Form):
    name = StringField('name', validators=[InputRequired(message='Name field cannot be left blank')])
    email = EmailField('email', validators=[Email(), InputRequired(message='Email field cannot be left blank')])
    password = PasswordField('New Password', validators=[InputRequired(message='Password field cannot be left blank'),
                                                         EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password',
                            validators=[InputRequired(message='Confirm Password field cannot be left blank')])
    age = IntegerField('age', validators=[InputRequired(message='Age field cannot be left blank')])
    locality = StringField('locality', validators=[InputRequired(message='Locality field cannot be left blank')])
    gender = SelectField('gender', choices=[('female', 'Female'), ('male', 'Male')],
                         validators=[InputRequired(message='Gender field cannot be left blank')])


class LoginForm(Form):
    email = EmailField('Email', validators=[Email(message='Invalid Email format'),
                                            InputRequired(message='Email field cannot be left blank'), Length(1, 64)])
    password = PasswordField('Password', validators=[InputRequired('Password field cannot be left blank')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class SearchFamilyForm(Form):
    members = SelectField("members")
    my_members = MultiCheckboxField('My Family')


class SearchDoctorForm(Form):
    doctortype = StringField('doctortype', validators=[InputRequired()])


class ConditionHistoryForm(Form):
    cond = HiddenField('cond')
