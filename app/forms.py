from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.fields import SelectMultipleField
from wtforms.validators import DataRequired, Length
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