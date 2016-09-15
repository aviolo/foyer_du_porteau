# foyer_du_porteau

Site de l'association foyer du porteau

## Dependencies

* python3-django
* python3-django-web-utils
* python3-pil
* uwsgi
* uwsgi-plugin-python3

## Database initialisation

	python3 manage.py migrate

## Superuser account creation

	python3 manage.py shell
	from django.contrib.auth import models
	models.User.objects.create_superuser(username='admin', email='admin@server.com', password='admin')
