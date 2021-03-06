FROM python:3.8-alpine

WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "idcard:app"]
