# Yatube

### Yatube - social network. Here users can create posts, comment on them, subscribe to each other.

*This is final project of the 5th sprint (the third month of training from nothing).*

### Example:
##  https://my-ya.xyz/

Uses:
- Download this repo
```
git@github.com:Xewus/Yatube.git
```
- Go to the directory with this
```
cd Yatube/
```
- Create virtual environment
```
python3 -m venv venv
```
- Activate virtual environment
```
. venv/bin/activate
```
- Install requirements:
```
pip install -r requirements.txt
```
- Apply migrations (SQLite will be created):
```
python yatube/manage.py migrate
```
- Create superuser:
```
python yatube/manage.py createsuperuser
```
- Finally, run
```
python yatube/manage.py runserver
```

