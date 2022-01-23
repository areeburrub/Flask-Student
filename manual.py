from models import db, Contact, User, Remarks, Att, Attendance, Att_T
from datetime import datetime, timedelta
from resource import get_bucket, get_buckets_list
import csv
import os
import boto3

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


batches = Contact.query.with_entities(Contact.batch).distinct()
for batch in batches:
    fieldnames = ['date','class']
    studentz = Contact.query.filter_by(batch = batch[0]).order_by(Contact.fullname).all()
    for each in studentz:
        fieldnames.append(each.fullname)
    data_set = {}
    CLASSES = Attendance.query.filter_by(batch = batch[0]).order_by(Attendance.date).all()


    for clas in CLASSES:
        f_path = 'static/csv/exported/'
        f_name = clas.attendid + '.csv'
        Stu_ATD = Att.query.filter_by(attid=clas.attendid).order_by(Att.of).all()

        if (Stu_ATD):
            with open(f_path + f_name,'w',newline="") as f:
                data_set = {}
                data_set['date'] = clas.date
                data_set['class'] = clas.Class

                for n in Stu_ATD:
                    if (n.status == False):
                        r = False
                    else:
                        r = True
                    data_set[n.of] = r
                    db.session.delete(n)
                    db.session.commit()
                writter = csv.DictWriter(f,fieldnames=fieldnames)
                writter.writeheader()
                writter.writerow(data_set)
            
            s3.upload_file(f_path + f_name, S3_BUCKET_NAME ,'r30/csv/exported/'+f_name, ExtraArgs={'ACL':'public-read'})
            os.remove(f_path + f_name)
            print('exported: ' + f_name + ' to aws')
