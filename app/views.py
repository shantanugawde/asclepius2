from app import app
from flask import render_template, flash, redirect, url_for
from config import api
from .forms import SymptomsForm, MultiCheckboxField, ConditionsForm
import infermedica_api

selected_symptoms = list()

@app.route('/symptoms/<phrase>', methods=['GET', 'POST'])
def symptoms(phrase):
	title = phrase + " Symptoms"
	possible_symptoms = api.search(phrase, sex = 'male')
	form = SymptomsForm()
	form.symptoms_list.choices = [ (x['id'], x['label']) for x in possible_symptoms]
	
	if form.validate_on_submit():
		selected_symptoms.clear()
		for symp in form.symptoms_list:
			if symp.checked == True:
				selected_symptoms.append(symp.data)
		return redirect(url_for('conditions', phrase=phrase))
	
	return render_template('symptoms.html', title=title, form=form)


@app.route('/conditions/<phrase>', methods=['GET', 'POST'])
def conditions(phrase):
	title = phrase + " Conditions"
	possible_conditions = infermedica_api.Diagnosis(sex='male', age=35)
	for symp in selected_symptoms:
		possible_conditions.add_symptom(symp,'present')
    
    # call diagnosis
	possible_conditions = api.diagnosis(possible_conditions)
	probability_mapping = {x['id']: x['probability'] for x in possible_conditions.conditions}
	
	form = ConditionsForm()
	form.conditions_list.choices = [ (x['id'], x['name']) for x in possible_conditions.conditions]
	
	return render_template('conditions.html', title=title, form=form, probability_mapping=probability_mapping)
	