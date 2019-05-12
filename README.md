# photoalbum
Python Django Photoalbum

Created By: Fogalmam Sincs Team (Meszaros Patrik, Berki Tamas)

Setting up:

0. pip install -r requirements.txt

Setting up from "photoalbum/" folder
1. Oracle database setup in photoalbum/photoalbum/setting.py at the database section.
2. python manage.py collectstatic
3. python manage.py makemigrations imagesapp users photoalbum (for all app ) //
    OR 
   python manage.py makemigrations (maybe collect all model)
4. python manage.py migrate (run migration files and create tables in database)
5. python manage.py loaddata db.json (may UTF-8 incompatible can be)
6. django-admin creatsuperuser
7. python manage.py runserver
