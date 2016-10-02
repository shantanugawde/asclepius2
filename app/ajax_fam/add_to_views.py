@app.route('/_myfamily')
def myfamily():
    my_family = User.query.filter_by(family_id=g.user.family_id).all()
    famdict = {x.id: x.name for x in my_family}

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
