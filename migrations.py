from models import db, Contact, User, Remarks, Att, Attendance, Att_T, Allow
from werkzeug.security import generate_password_hash, check_password_hash

# db.drop_all()
db.create_all()
users = User.query.all()

batches = Contact.query.with_entities(Contact.batch).distinct()
for user in users:
    for a in batches:
        new_allow = Allow(
            user=user.username,
            allowed=a[0]
        )
        db.session.add(new_allow)
        db.session.commit()


# all = Contact.query.order_by(Contact.fullname).all()

# for i in all:
#   Add_Att_T = Att_T(
#                   present = Att.query.filter_by(of = i.fullname ,status=True).count(),
#                   absent = Att.query.filter_by(of = i.fullname , status= False).count(),
#                   uid = i.uid
#               )
#   db.session.add(Add_Att_T)
#   db.session.commit()

# Default User
hashed_password = generate_password_hash('1234', method='sha256')
new_user = User(
    adid='DefaultUser',
    username='Admin',
    email='admin@domain.xyz',
    admin=True,
    userad=True,
    password=hashed_password)
db.session.add(new_user)
db.session.commit()
