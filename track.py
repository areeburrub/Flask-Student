from models import db, Contact, User, Remarks,Att, Attendance, Att_T
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from resource import get_bucket, get_buckets_list
import csv
import os
import boto3
import secrets

AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

s3 = boto3.client(
            's3',
            aws_access_key_id= AWS_ACCESS_KEY_ID,
            aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
            region_name= AWS_DEFAULT_REGION
        )
Tracked =  Att_T.query.all()
for every in Tracked:
  #Delete Previeous data
  db.session.delete(every)
  db.session.commit()
batche = Contact.query.with_entities(Contact.batch).distinct()
for batch in batche:
  List = Contact.query.filter_by(batch = batch[0]).order_by(Contact.fullname).all()
  for i in List:
    Trackq =  Att_T.query.filter_by(uid = i.uid ).first()
    
    
# ###############Refresh Data#################
    P = Att.query.filter_by(of = i.fullname ,status=True).count()
    A = Att.query.filter_by(of = i.fullname , status= False).count()
    if (Trackq):
      Pr = int(Trackq.present)
      Ab = int(Trackq.absent)
      Pr += P
      Ab += A
      Track.present = Pr
      Track.absent = Ab
      db.session.commit()
      print('from record for '+i.fullname + ' Count: '+str(Pr+Ab))

    else:
      Add_Att_T = Att_T(
          present = P,
          absent = A,
          uid = i.uid
      )
      db.session.add(Add_Att_T)
      db.session.commit()
      print('from record for '+i.fullname + ' Count: '+str(P+A))
    print('init for '+i.fullname)
  C_All = Attendance.query.filter_by(batch = batch[0]).order_by(Attendance.date).all()

  for c in C_All:
    co = 0
    print('---------'+str(c.date)+'--------')
    Atd_Lists = Att.query.filter_by(attid = c.attendid).first()
    if(Atd_Lists):
      print('Att Already exist')
      continue
    else:
      token = secrets.token_urlsafe(8)
      s3.download_file(S3_BUCKET_NAME,'r30/csv/exported/'+ c.attendid + '.csv', 'static/csv/aws/'+ token + '.csv')
      with open( 'static/csv/aws/'+ token + '.csv', newline='') as csvfile:
        read = csv.DictReader(csvfile)
        for row in read:
          for i in List:
            try:
              if(row[i.fullname]=='True'):
                P = 1
                A = 0
            
              else:
                P = 0
                A = 1
            except:
                P = 0
                A = 1
            

            Track =  Att_T.query.filter_by(uid = i.uid ).first()
            
            if (Track):
              Pr = int(Track.present)
              Ab = int(Track.absent)
              Pr += P
              Ab += A
              Track.present = Pr
              Track.absent = Ab
              db.session.commit()
              co += 1
              print(str(co)+'from aws[ex] for '+i.fullname + ' Count: '+str(Pr+Ab))
            else:
              Add_Att_T = Att_T(
                  present = P,
                  absent = A,
                  uid = i.uid
              )
              db.session.add(Add_Att_T)
              db.session.commit()
              co += 1
              print(str(co)+'from aws[new] for '+i.fullname + ' Count: '+str(P+A))
            
      os.remove('static/csv/aws/'+ token + '.csv')
    