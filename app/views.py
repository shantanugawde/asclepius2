from app import app, db, mail
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_required, current_user, logout_user, login_user
from config import api
from .forms import SymptomsForm, ConditionsForm, SearchPhrasesForm, RegistrationForm, LoginForm, SearchFamilyForm, RisksForm
from .models import User, Condition, Symptom, Risk
import infermedica_api
from config import gmaps
from urllib.request import urlopen
import json
import sys
from flask_mail import Message

selected_symptoms = list()


@app.route('/searchphrases', methods=['GET', 'POST'])
@login_required
def searchphrases():
    form = SearchPhrasesForm()

    if form.validate_on_submit():
        return redirect(url_for('symptoms', phrase=form.phrases.data))

    return render_template('searchphrases.html', title='Search Phrases', form=form)


@app.route('/symptoms/<phrase>', methods=['GET', 'POST'])
@login_required
def symptoms(phrase):
    title = phrase + " Symptoms"
    tmp_list = phrase.strip().split('%20')
    possible_symptoms = list()
    for p in tmp_list:
        possible_symptoms = possible_symptoms + api.search(p, sex=g.user.gender)

    for x in possible_symptoms:
        if Symptom.query.filter_by(id=x['id']).scalar() is None:
            db.session.add(Symptom(id=x['id'], label=x['label']))

    db.session.commit()

    form = SymptomsForm()
    form.symptoms_list.choices = [(x['id'], x['label']) for x in possible_symptoms]

    if form.validate_on_submit():
        selected_symptoms.clear()
        for symp in form.symptoms_list:
            if symp.checked:
                selected_symptoms.append(symp.data)
        return redirect(url_for('conditions', phrase=phrase))
    return render_template('symptoms.html', title=title, form=form)


@app.route('/conditions/<phrase>', methods=['GET', 'POST'])
@login_required
def conditions(phrase):
    title = phrase + " Conditions"
    possible_conditions = infermedica_api.Diagnosis(sex=g.user.gender, age=g.user.age)
    for symp in selected_symptoms:
        possible_conditions.add_symptom(symp, 'present')

    return_risks = g.user.get_risk()
    for r in return_risks:
        possible_conditions.add_risk_factor(r.id, 'present')
    possible_conditions = api.diagnosis(possible_conditions)

    if len(possible_conditions.conditions) < 5:
        MAX_CONDITIONS = len(possible_conditions.conditions)
    else:
        MAX_CONDITIONS = 5

    probability_mapping = {x['id']: x['probability'] for x in possible_conditions.conditions[:MAX_CONDITIONS]}

    for x in possible_conditions.conditions[:MAX_CONDITIONS]:
        cond = Condition(id=x['id'], name=x['name'])
        if len(Condition.query.filter_by(id=cond.id).all()) == 0:
            db.session.add(cond)
        g.user.add_condition(cond)

    db.session.commit()
    for_mail = ""
    i=1
    for x in possible_conditions.conditions[:MAX_CONDITIONS]:
        cond = Condition.query.filter_by(id=x['id']).first()
        for_mail = for_mail + str(i) + "." + x['name'] + "\n"
        i = i + 1
        for y in selected_symptoms:
            symp = Symptom.query.filter_by(id=y).first()
            if symp is not None:
                cond.add_symptom(symp)

    db.session.commit()
    if g.user.age < 18:
        if g.user.has_family: 
            family_list = g.user.get_family()
            for fam in family_list:
                
                body = """
                       Dear %(f_name)s, your family member, %(name)s, has been diagnosed with the following conditions in descending order of
					   probability by Asclipius.
					   %(conditions_string)s
			           """%{"f_name":fam.name, "name":g.user.name, "conditions_string":for_mail}
                subject='Family Diagnosis'
                sender = 'Asclepius'
                recipients = [fam.email]
                send_email(subject,sender,recipients,body)
    form = ConditionsForm()
    form.conditions_list.choices = [(x['id'], x['name']) for x in possible_conditions.conditions[:MAX_CONDITIONS]]

    return render_template('conditions.html', title=title, form=form, probability_mapping=probability_mapping)


@app.route('/family', methods=['GET', 'POST'])
@login_required
def family():
    form = SearchFamilyForm()
    if g.user.family_id != 0:
        allmembers = User.query.filter_by(family_id=0).all()
    else:
        allmembers = User.query.all()
    form.members.choices = [(x.id, x.name) for x in allmembers if x.id != g.user.id]
    my_family = User.query.filter_by(family_id=g.user.family_id).all()
    form.my_members.choices = [(x.id, x.name) for x in my_family if x.id != 0]
    if form.validate_on_submit:
        selected_member = User.query.filter_by(id=form.members.data).first()
        if selected_member is not None:
            g.user.add_member(selected_member)
            db.session.commit()
        flash(form.members.data)

    return render_template('family.html', title='family', form=form)

@app.route('/risk/<email>',methods=['GET','POST'])
def risk(email):
    form = RisksForm()
    selected_risks = Risk.query.all()
    form.risks_list.choices = [(x.id,x.name) for x in selected_risks]
    user1 = User.query.filter_by(email = email).first()
    #flash(user1)
    if form.validate_on_submit():
        selected_risks.clear()
        for r in form.risks_list:
            if r.checked:
                user1.add_risk(Risk.query.filter_by(id = r.data).first())
                selected_risks.append(r.data)
        db.session.commit()	
        return redirect(url_for('login'))
    return render_template('risks.html',email = email,form = form,i = 0)
@app.route('/conditionhistory')
@login_required
def conditionhistory():
    return render_template('conditionhistory.html', conditions=g.user.get_conditions())


@app.route('/globalhistory')
@login_required
def globalhistory():
    # condition_map = dict()
    all_conditions = Condition.query.all()
    # for x in all_conditions:
    #     condition_map[x.name] = x.get_symptoms()

    return render_template('globalhistory.html', all_conditions=all_conditions)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    title = "Registration"
    form = RegistrationForm()

    if form.validate_on_submit():
        u = User(name=form.name.data, email=form.email.data, age=form.age.data, gender=form.gender.data)
        u.password = form.password.data
        db.session.add(u)
        db.session.commit()
        flash('Registration Successful')
        body = "Welcome to Asclepius!"
        subject="Welcome!"
        sender = 'Asclepius'
        recipients = [form.email.data]
        send_email(subject,sender,recipients,body)
        return redirect(url_for('risk',email = form.email.data))
    return render_template('registration.html', title=title, form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('searchphrases'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('searchphrases'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/doctor/<typed>',methods=['GET'])
def doctor(typed):
    geocode_result = gmaps.geocode('four bungalows,andheri')
    lat = geocode_result[0][u'geometry'][u'location'][u'lat']
    lng = geocode_result[0][u'geometry'][u'location'][u'lng']
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(lat)+","+str(lng)+"&radius=500&type="+typed+"&key=AIzaSyDVK5ynnDSJZ0MWKRYtKZZKhxTMqTg1rl0"
    response_body = urlopen(url).read().decode()
    return render_template('markers.html',typed=typed,obj=json.loads(response_body))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('searchphrases'))


@app.before_request
def before_request():
    g.user = current_user


def send_email(subject,sender,recipients,body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = body
    mail.send(msg)