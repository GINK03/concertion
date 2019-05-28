cd project
gunicorn -w 4 --bind 0.0.0.0:7000 wsgi
