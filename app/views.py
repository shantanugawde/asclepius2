from app import app, db, mail
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import login_required, current_user, logout_user, login_user
from config import api
from .forms import SymptomsForm, ConditionsForm, SearchPhrasesForm, RegistrationForm, LoginForm, SearchFamilyForm, \
    RisksForm, SearchDoctorForm
from .models import User, Condition, Symptom, Risk
import infermedica_api
from config import gmaps
from urllib.request import urlopen
import json
from flask_mail import Message
import sys

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
    mytitle = phrase.replace("%20", " ")
    title = mytitle + " Symptoms"
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
    mytitle = phrase.replace("%20", " ")
    title = mytitle + " Conditions"
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

    probability_mapping = {x['id']: x['probability'] * 100 for x in possible_conditions.conditions[:MAX_CONDITIONS]}

    for x in possible_conditions.conditions[:MAX_CONDITIONS]:
        cond = Condition(id=x['id'], name=x['name'])
        if len(Condition.query.filter_by(id=cond.id).all()) == 0:
            db.session.add(cond)
        g.user.add_condition(cond)

    db.session.commit()

    for x in possible_conditions.conditions[:MAX_CONDITIONS]:
        cond = Condition.query.filter_by(id=x['id']).first()
        for y in selected_symptoms:
            symp = Symptom.query.filter_by(id=y).first()
            if symp is not None:
                cond.add_symptom(symp)

    db.session.commit()
    if g.user.age < 18:
        if g.user.has_family:
            family_list = g.user.get_family()
            for fam in family_list:
                text_body = render_template("diagnosis_mail.txt", parent=fam.name, minor=g.user.name,
                                            conditions=possible_conditions.conditions[:MAX_CONDITIONS])
                html_body = render_template("diagnosis_mail.html", parent=fam.name, minor=g.user.name,
                                            conditions=possible_conditions.conditions[:MAX_CONDITIONS])
                subject = 'Family Diagnosis'
                sender = 'Asclepius'
                recipients = [fam.email]
                send_email(subject, sender, recipients, text_body, html_body)
    form = ConditionsForm()
    form.conditions_list.choices = [(x['id'], x['name']) for x in possible_conditions.conditions[:MAX_CONDITIONS]]

    return render_template('conditions.html', title=title, form=form, probability_mapping=probability_mapping)


@app.route('/_myfamily')
def myfamily():
    my_family = User.query.filter_by(family_id=g.user.family_id).all()
    famdict = {x.id: x.name for x in my_family if x.family_id != 0}
    return jsonify(famdict)


@app.route('/_familychoices')
def familychoices():
    selected_id = request.args.get('sel_id', type=int)
    selected_member = User.query.filter_by(id=selected_id).first()
    if selected_member is not None:
        g.user.add_member(selected_member)
        db.session.commit()
    if g.user.family_id != 0:
        allmembers = User.query.filter_by(family_id=0).all()
    else:
        allmembers = User.query.all()
    famdict = {x.id: x.name for x in allmembers if x.id != g.user.id}
    return jsonify(famdict)


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
    form.my_members.choices = [(x.id, x.name) for x in my_family if x.family_id != 0]

    return render_template('family.html', title='Family', form=form)


@app.route('/addfamily', methods=['GET', 'POST'])
@login_required
def addfamily():
    form = SearchFamilyForm()
    if g.user.family_id != 0:
        allmembers = User.query.filter_by(family_id=0).all()
    else:
        allmembers = User.query.all()
    form.members.choices = [(x.id, x.name) for x in allmembers if x.id != g.user.id]

    if form.validate_on_submit:
        selected_member = User.query.filter_by(id=form.members.data).first()
        if selected_member is not None:
            g.user.add_member(selected_member)
            db.session.commit()
            return redirect(url_for('viewfamily'))

    return render_template('addfamily.html', title='Add to Family', form=form)


@app.route('/viewfamily', methods=['GET', 'POST'])
@login_required
def viewfamily():
    form = SearchFamilyForm()
    if g.user.family_id != 0:
        allmembers = User.query.filter_by(family_id=0).all()
    else:
        allmembers = User.query.all()
    form.members.choices = [(x.id, x.name) for x in allmembers if x.family_id != g.user.family_id]
    my_family = User.query.filter_by(family_id=g.user.family_id).all()
    form.my_members.choices = [(x.id, x.name) for x in my_family if
                               x.family_id != 0 and x.id != g.user.id]
    return render_template('viewfamily.html', title='View Family', form=form)


@app.route('/risk/<email>', methods=['GET', 'POST'])
def risk(email):
    form = RisksForm()
    selected_risks = Risk.query.all()
    form.risks_list.choices = [(x.id, x.name) for x in selected_risks]
    user1 = User.query.filter_by(email=email).first()
    # flash(user1)
    if form.validate_on_submit():
        selected_risks.clear()
        for r in form.risks_list:
            if r.checked:
                user1.add_risk(Risk.query.filter_by(id=r.data).first())
                selected_risks.append(r.data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('risks.html', email=email, form=form, i=0)


@app.route('/conditionhistory')
@login_required
def conditionhistory():
    return render_template('conditionhistory.html', conditions=g.user.get_conditions())


@app.route('/globalhistory')
@login_required
def globalhistory():
    all_conditions = Condition.query.all()
    return render_template('globalhistory.html', all_conditions=all_conditions)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # title = "Registration"
    form = RegistrationForm()

    if form.validate_on_submit():
        u = User(name=form.name.data, email=form.email.data, age=form.age.data, gender=form.gender.data,
                 locality=form.locality.data)
        u.password = form.password.data
        db.session.add(u)
        db.session.commit()
        flash('Registration Successful')
        return redirect(url_for('risk', email=form.email.data))
    return render_template('registration.html', form=form)


@app.route('/')
@app.route('/index')
def index():
    if g.user.is_authenticated:
        return redirect(url_for('consult'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@app.route('/searchdoctor', methods=['GET', 'POST'])
def searchdoctor():
    form = SearchDoctorForm()
    if form.validate_on_submit():
        return redirect(url_for('doctormap', typed=form.doctortype.data))
    return render_template('searchdoctor.html', title='Search Doctor', form=form)


@app.route('/map/<typed>', methods=['GET'])
@login_required
def doctormap(typed):
    geocode_result = gmaps.geocode(g.user.locality)
    lat = geocode_result[0][u'geometry'][u'location'][u'lat']
    lng = geocode_result[0][u'geometry'][u'location'][u'lng']
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(lat) + "," + str(
        lng) + "&radius=500&type=" + typed + "&key=AIzaSyDVK5ynnDSJZ0MWKRYtKZZKhxTMqTg1rl0"
    response_body = urlopen(url).read().decode()
    return render_template('markers.html', typed=typed, obj=json.loads(response_body))


@app.route('/consult')
@login_required
def consult():
    return render_template('consult.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
