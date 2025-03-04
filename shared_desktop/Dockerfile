FROM python:3.11

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN python manage.py collectstatic --noinput

COPY tools/restart_web_admin /app/tools/restart_web_admin

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "shared_desktop.wsgi"]
