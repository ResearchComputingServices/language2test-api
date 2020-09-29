import json

def populate(db, models):
    Authorization = models.authorization.Authorization
    with open('data/authorization.json') as file:
        data = json.load(file)
        for datum in data:
            new_data = Authorization(datum)
            db.session.add(new_data)