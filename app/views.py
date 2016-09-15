from app import app
from flask import render_template
from config import api
from .forms import SymptomsForm, MultiCheckboxField


@app.route('/symptoms/<phrase>', methods=['GET', 'POST'])
def symptoms(phrase):
	title = phrase + " Symptoms"
	possible_symptoms = api.search(phrase, sex = 'male')
	form = SymptomsForm()
	form.symptoms_list.choices = [ (x['id'], x['label']) for x in possible_symptoms]

	return render_template('symptoms.html', title=title, form=form)
