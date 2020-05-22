# pandora-finance


### Installing:

1. Clone (or download) the repository
```
$ git clone https://github.com/kuronosu/pandora-finance.git
$ cd pandora-finance
```
2. Create a virtualenv and install the dependencies for python and node
```
$ virtualenv env
For linux
$ ./env/bin/activate
For windows
$ ./env/Scripts/activate
$ pip install -r requirements.txt
```
3. Migrate the database
```
$ python manage.py migrate
```
4. Create superuser
```
$ python manage.py createsuperuser
```
5. Run Django server
```
$ python manage.py runserver
```
