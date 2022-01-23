import re
from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from models import db, Contact, User, Remarks, Att, Attendance, Att_T, Allow
from forms import ContactForm, LoginForm, RegisterForm
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
import os
import secrets
import csv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import desc
from filters import datetimeformat
from flask_marshmallow import Marshmallow


# Flask
app = Flask(__name__)


app.jinja_env.filters['datetimeformat'] = datetimeformat

app.config['SECRET_KEY'] = 'my secret'
app.config['DEBUG'] = False

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Bootstarp for Flask
Bootstrap(app)

# Flask Marshmallow to convert SQL alchemy to JSON
ma = Marshmallow(app)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Marshmallow Schema
class AttSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Attendance
    id = ma.auto_field()
    date = ma.auto_field()
    batch = ma.auto_field()
    present = ma.auto_field()
    absent = ma.auto_field()
    attendid = ma.auto_field()
    Class = ma.auto_field()


# Loading users to Flask Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


## ROOUTES TO DIFFERENT PAGES ##

# HomePage
@app.route("/")
@login_required
def index():
    '''
    Home page
    '''
    return redirect(url_for('batches'))


# Error Page
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('web/404.html'), 404


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # importing forms from forms.py created using Flask Forms
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(request.args.get("next") or url_for('batches'))
        flash('Invalid Username or Password', 'danger')
        return redirect(url_for('index'))

    return render_template('web/login.html', form=form)


# superuser
@app.route('/addsuperuser', methods=['GET', 'POST'])
@login_required
def signup():
    if(current_user.userad == True):
        form = RegisterForm()  # importing forms from forms.py created using Flask Forms
        if form.validate_on_submit():
            hashed_password = generate_password_hash(
                form.password.data, method='sha256')
            new_user = User(adid=secrets.token_urlsafe(
                8), username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            allow = request.form.getlist('allow')
            for a in allow:
                new_allow = Allow(
                    user=form.username.data,
                    allowed=a
                )
                db.session.add(new_allow)
                db.session.commit()
            flash(form.username.data + ' is added as a superuser', 'success')
            return redirect(url_for('index'))
        batches = Contact.query.with_entities(Contact.batch).distinct()
        return render_template('web/signup.html', form=form, batches=batches)
    else:
        flash('This action is disabled for you (' +
              current_user.username+')', 'danger')
        return redirect(url_for('index'))


# Logout URL
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Student add using csv
@app.route("/csv", methods=['GET', 'POST'])
@login_required
def csvread():
    if (request.method == 'POST'):
        csvf = request.files['file']
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(csvf.filename)
        filename = random_hex + f_ext
        file_path = os.path.join(app.root_path, 'static/csv', filename)
        csvf.save(file_path)
        with open(file_path, newline='') as csvfile:
            read = csv.DictReader(csvfile)
            for row in read:
                name = row['name']
                email = row['email']
                G_name = row['G_name']
                G_W = row['G_W']
                C_W = row['C_W']
                phone = row['phone']
                batch = row['batch']

                exist = Contact.query.filter_by(email=email).first()
                if (exist):
                    flash('Some error occured while adding ' + name, 'danger')
                else:
                    new_contact = Contact(
                        fullname=name,
                        uid=secrets.token_urlsafe(8),
                        email=email,
                        G_name=G_name,
                        G_W=G_W,
                        C_W=C_W,
                        phone=phone,
                        batch=batch
                    )

                    db.session.add(new_contact)
                    db.session.commit()

            allow = request.form.getlist('allow')

            for a in allow:
                new_allow = Allow(
                    user=a,
                    allowed=batch
                )
                db.session.add(new_allow)
                db.session.commit()

            flash('Contacts added successfully', 'success')
            return redirect(url_for('batches'))
    else:
        supuser = User.query.order_by(User.username).all()
        return render_template('web/csv.html', user=current_user, supuser=supuser)


# Eporting Specific Attendance Sheet
@app.route("/export/<string:attid>")
@login_required
def export(attid):
    fieldnames = ['date', 'class']
    Attend = Attendance.query.filter_by(attendid=attid).first()
    batches = Contact.query.filter_by(
        batch=Attend.batch).order_by(Contact.fullname).all()
    for each in batches:
        fieldnames.append(each.fullname)

    data_set = {}
    f_path = 'static/csv/exported/'
    f_name = Attend.attendid + '.csv'

    with open(f_path + f_name, 'w', newline="") as f:
        data_set = {}
        Stu_ATD = Att.query.filter_by(
            attid=Attend.attendid).order_by(Att.of).all()
        data_set['date'] = Attend.date
        data_set['class'] = Attend.Class

        for n in Stu_ATD:
            if (n.status == False):
                r = False
            else:
                r = True
            data_set[n.of] = r
        writter = csv.DictWriter(f, fieldnames=fieldnames)
        writter.writeheader()
        writter.writerow(data_set)

    return redirect(url_for('static', filename='csv/exported/'+f_name))


# new student manualluy
@app.route("/new_contact", methods=('GET', 'POST'))
@login_required
def new_contact():
    '''
    Create new contact
    '''
    supuser = User.query.order_by(User.username).all()
    form = ContactForm()
    if form.validate_on_submit():
        my_contact = Contact()
        form.populate_obj(my_contact)
        my_contact.batch = request.form.get('batch')
        batch = my_contact.batch
        my_contact.uid = secrets.token_urlsafe(8)
        db.session.add(my_contact)
        allow = request.form.getlist('allow')
        for a in allow:
            new_allow = Allow(
                user=a,
                allowed=batch
            )
            db.session.add(new_allow)
            db.session.commit()
        try:
            db.session.commit()
            # User info
            flash('Added Successfully', 'success')
            return redirect(url_for('contacts', batch=batch))
        except:
            db.session.rollback()
            flash('Error while adding this entry', 'danger')

    batches = Contact.query.with_entities(Contact.batch).distinct()
    return render_template('web/new_contact.html', form=form, supuser=supuser, batches=batches, user=current_user)


# Edit Student Profile
@app.route("/edit_contact/<id>", methods=('GET', 'POST'))
@login_required
def edit_contact(id):
    '''
    Edit contact

    :param id: Id from contact
    '''
    my_contact = Contact.query.filter_by(id=id).first()
    form = ContactForm(obj=my_contact)
    if form.validate_on_submit():
        try:
            # Update contact
            form.populate_obj(my_contact)
            db.session.add(my_contact)
            db.session.commit()
            # User info
            flash('Saved successfully', 'success')
        except:
            db.session.rollback()
            flash('Error update contact.', 'danger')
    return render_template('web/edit_contact.html', form=form, student=my_contact, user=current_user)


# List All Batches a user allowed to see
@app.route("/contacts")
@login_required
def batches():
    '''
    Show alls contacts
    '''
    batches = Allow.query.filter_by(
        user=current_user.username).order_by(Allow.allowed).all()
    return render_template('web/batchs.html', batches=batches, user=current_user)


# List of Student in a Specific Batch
@app.route("/contacts/<string:batch>")
@login_required
def contacts(batch):
    '''
    Show alls contacts
    '''
    allow = Allow.query.filter_by(user=current_user.username).all()
    for a in allow:
        if(a.allowed == batch):
            contacts = Contact.query.filter_by(
                batch=batch).order_by(Contact.fullname).all()
            return render_template('web/contacts.html', b=batch, contacts=contacts, user=current_user)

    return redirect(url_for('index'))


# Search URL
@app.route("/search")
@login_required
def search():
    '''
    Search
    '''
    name = request.args.get('name')
    all_contacts = Contact.query.filter(
        Contact.fullname.contains(name)
    ).order_by(Contact.fullname).all()
    return render_template('web/contacts.html', s=name, contacts=all_contacts, user=current_user)


# Delete Student Profile
@app.route("/contacts/delete", methods=('POST',))
@login_required
def contacts_delete():
    '''
    Delete contact
    '''
    try:
        mi_contacto = Contact.query.filter_by(id=request.form['id']).first()
        batch = mi_contacto.batch
        db.session.delete(mi_contacto)
        db.session.commit()

        flash('Delete successfully.', 'danger')
    except:
        db.session.rollback()
        flash('Error delete  contact.', 'danger')

    return redirect(url_for('contacts', batch=batch))


# Page for every student Profile
@app.route("/contacts/student/<string:uid>")
@login_required
def student(uid):
    stu = Contact.query.filter_by(uid=uid).first()
    remarks = Remarks.query.filter_by(
        to=uid).order_by(desc(Remarks.date)).all()
    try:
        Track = Att_T.query.filter_by(uid=uid).first()
        P = int(Track.present)
        A = int(Track.absent)
        Total_class = P + A
        Pres = round(P*100/Total_class)
        Abse = round(A*100/Total_class)
    except:
        P = 0
        A = 0
        Pres = 0
        Abse = 0
        Total_class = 1
        flash('No Attendance Data Found', 'danger')

    return render_template('web/student.html', remarks=remarks, TClass=int(Total_class), P=Pres, A=Abse, student=stu, user=current_user)


# superuser setting page
@app.route("/superuser/<string:adid>")
@login_required
def user(adid):
    usr = User.query.filter_by(adid=adid).first()
    all_user = User.query.order_by(User.username).all()
    if (usr):
        if (usr.adid == current_user.adid):
            return render_template('web/user.html', All=all_user, user=current_user)
    else:
        return 'This URL doesen\'t exist'

# Add remark to a student profile


@app.route("/remark", methods=('GET', 'POST'))
@login_required
def remark():
    if (request.method == 'POST'):
        by = request.form.get('by')
        byname = request.form.get('byname')
        to = request.form.get('to')
        text = request.form.get('remark')
        new_remark = Remarks(
            rid=secrets.token_urlsafe(8),
            by=by,
            byname=byname,
            to=to,
            text=text
        )
        db.session.add(new_remark)
        db.session.commit()
        return redirect(url_for('student', uid=to))
    else:
        return 'This URL doesen\'t exist'

# delete remark from student profile


@app.route("/remark/delete/<string:rid>")
@login_required
def delremark(rid):
    rem = Remarks.query.filter_by(rid=rid).first()
    to = rem.to
    db.session.delete(rem)
    db.session.commit()
    return redirect(url_for('student', uid=to))


# Batch Checklist and Attrendance Submit URL
@app.route("/checklist/<string:batch>", methods=('GET', 'POST'))
@login_required
def att(batch):

    allow = Allow.query.filter_by(user=current_user.username).all()
    for a in allow:
        if(a.allowed == batch):
            if (request.method == 'POST'):
                if(request.form.get('purpose') == 'att'):
                    List = Contact.query.filter_by(
                        batch=batch).order_by(Contact.fullname).all()
                    for S in List:
                        Add = Att(
                            attid=request.form.get('atid'),
                            byname=current_user.username,
                            of=S.fullname,
                            purpose=request.form.get('purpose'),
                            status=False
                        )
                        db.session.add(Add)
                        db.session.commit()
                    Ticked = request.form.getlist('names')
                    for A in Ticked:
                        Marked = Att.query.filter_by(
                            of=A, attid=request.form.get('atid')).first()
                        Marked.status = True
                        db.session.commit()
                    Add_Att = Attendance(
                        attendid=request.form.get('atid'),
                        byname=current_user.username,
                        Class=request.form.get('class'),
                        present=Att.query.filter_by(
                            attid=request.form.get('atid'), status=True).count(),
                        absent=Att.query.filter_by(
                            attid=request.form.get('atid'), status=False).count(),
                        batch=batch
                    )
                    db.session.add(Add_Att)
                    db.session.commit()

                    for i in List:
                        Track = Att_T.query.filter_by(uid=i.uid).first()
                        status = Att.query.filter_by(
                            of=i.fullname, attid=request.form.get('atid')).first()

                        if (Track):
                            Pr = int(Track.present)
                            Ab = int(Track.absent)
                            if(status.status == True):
                                Pr += 1
                            else:
                                Ab += 1
                            Track.present = Pr
                            Track.absent = Ab
                            db.session.commit()
                        else:
                            if(status.status == True):
                                Pr = 1 
                                Ab = 0  
                            else:
                                Pr = 0  
                                Ab = 1  
                            Add_Att_T = Att_T(
                                present=Pr,
                                absent=Ab,
                                uid=i.uid
                            )
                            db.session.add(Add_Att_T)
                            db.session.commit()

                    return redirect(url_for('attlis', batch=batch))
                else:
                    flash(
                        'Nothing Recorded from previous list, because you seleected "JUST LIST"', 'danger')
                    return redirect(url_for('index'))
            else:
                stu = Contact.query.filter_by(
                    batch=batch).order_by(Contact.fullname).all()
                return render_template('web/att.html', attid=secrets.token_urlsafe(8), b=batch, user=current_user, names=stu)
    return redirect(url_for('index'))


# Attendance Analysis Page
@app.route("/<string:batch>/checklist")
def attlis(batch):
    try:
        abs = []
        Atd_Lists = Attendance.query.filter_by(
            batch=batch).order_by(desc(Attendance.date)).all()

        List = Contact.query.filter_by(
            batch=batch).order_by(Contact.fullname).all()
        for Ab in List:
            ab = Att_T.query.filter_by(uid=Ab.uid).first()
            abs.append({'name': Ab.fullname, 'uid': ab.uid,
                       'present': ab.present, 'absent': int(ab.absent)})
        abst = (sorted(abs, key=lambda i: i['absent'], reverse=True))
    except:
        abs.append({'name': 'No Attendance', 'uid': '#',
                   'present': '0', 'absent': '0'})
        abst = []
        Atd_Lists = []
        Track = 0
        Total_class = 1
        flash('No Attendance Data Found', 'danger')
    return render_template('web/attlist.html',
                           b=batch,
                           most=abst,
                           Datas=Atd_Lists[:5],
                           user=current_user
                           )

# All attendance List


@app.route("/<string:batch>/checklist/more")
def attlismore(batch):
    try:
        abs = []
        Atd_Lists = Attendance.query.filter_by(
            batch=batch).order_by(desc(Attendance.date)).all()
    except:
        abs.append({'name': 'No Attendance', 'uid': '#',
                   'present': '0', 'absent': '0'})
        Atd_Lists = []
        Track = 0
        Total_class = 1
        flash('No Attendance Data Found', 'danger')
    return render_template('web/attlistmore.html',
                           b=batch,
                           Datas=Atd_Lists,
                           user=current_user
                           )

# View Attendance Page


@app.route("/<string:attid>/checklist/view")
def attview(attid):

    Atd = Attendance.query.filter_by(attendid=attid).first()
    Atd_Lists = Att.query.filter_by(attid=attid).order_by(Att.of).all()
    if(Atd_Lists):
        return render_template('web/attview.html', csv=False, file=attid, list=Atd, names=Atd_Lists, user=current_user)
    else:
        with open('static/csv/aws/' + attid + '.csv', newline='') as csvfile:
            read = csv.DictReader(csvfile)
            stud = []
            Atd_L = []
            batches = Contact.query.filter_by(
                batch=Atd.batch).order_by(Contact.fullname).all()
            for row in read:
                for each in batches:
                    try:
                        Atd_L.append(
                            {'name': each.fullname, 'status': row[each.fullname]})
                    except:
                        Atd_L.append({'name': each.fullname, 'status': 'none'})

        os.remove('static/csv/aws/' + attid + '.csv')
        return render_template('web/attview.html', csv=True, file=attid, list=Atd, names=Atd_L, user=current_user)


# API for Attendance Graph
@app.route("/attgraph", methods=['GET', 'POST'])
def attgraph():
    batch = request.form.get('batch')
    Atte = Attendance.query.filter_by(batch=batch).order_by(
        desc(Attendance.date)).limit(10)
    att_schema = AttSchema(many=True)
    result = att_schema.dump(Atte)
    return jsonify(result)


# Using Flask Admin to Manage Database Online also
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):

        if (current_user.is_anonymous == False):
            UserRole = current_user.admin
            if (UserRole == True):
                return True
            elif(UserRole == False):
                return False
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


class MyModelView(ModelView):
    def is_accessible(self):

        if (current_user.is_anonymous == False):
            UserRole = current_user.admin
            if (UserRole == True):
                return True
            elif(UserRole == False):
                return False
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


admin = Admin(app, index_view=MyAdminIndexView())

admin.add_view(MyModelView(Contact, db.session))
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Remarks, db.session))
admin.add_view(MyModelView(Att, db.session))
admin.add_view(MyModelView(Att_T, db.session))
admin.add_view(MyModelView(Attendance, db.session))
admin.add_view(MyModelView(Allow, db.session))

if __name__ == "__main__":
    app.run(debug=False, port=8000, host="0.0.0.0")
