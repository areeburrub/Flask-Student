FROM python:3.9

WORKDIR /att

COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY models.py .

COPY migrations.py .

ENV DATABASE_URL sqlite:////database.db

RUN python models.py

RUN python migrations.py

COPY ./ /att/

CMD ["python","app.py"]