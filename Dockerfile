FROM ubuntu

RUN apt update && \
    apt install python3-pip -y

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# CMD python3 app.py
CMD gunicorn --bind 0.0.0.0:5000 app:app