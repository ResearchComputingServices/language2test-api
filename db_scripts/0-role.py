import json

def populate(db, models):

    Authorization = models.authorization.Authorization
    Role = models.role.Role

    #Creates admnistrator role with all authorizations
    authorizations = Authorization.query.all()
    data = {
        'id': 1,
        'name': 'Administrator',
        'authorizations': [],
        'immutable' : True
    }
    role = Role(data)
    for authorization_item in authorizations:
       role.authorizations.append(authorization_item)
    db.session.add(role)

    #Creates test taker role
    data = {
        'id': 2,
        'name' : 'Test Taker',
        'authorizations' : [],
        'immutable': True
    }

    role = Role(data)

    with open('data/test_taker_authorization.json') as file:
        data = json.load(file)
        for datum in data:
            auth =  Authorization.query.filter_by(name=datum.get('name')).first()
            role.authorizations.append(auth)
    db.session.add(role)

    # Creates test developer role
    data = {
        'id': 3,
        'name': 'Test Developer',
        'authorizations': [],
        'immutable': False
    }

    role = Role(data)

    with open('data/test_developer_authorization.json') as file:
        data = json.load(file)
        for datum in data:
            auth = Authorization.query.filter_by(name=datum.get('name')).first()
            role.authorizations.append(auth)
    db.session.add(role)

    # Creates Researcher Role
    data = {
        'id': 4,
        'name': 'Researcher',
        'authorizations': [],
        'immutable': False
    }

    role = Role(data)

    with open('data/researcher_authorization.json') as file:
        data = json.load(file)
        for datum in data:
            auth = Authorization.query.filter_by(name=datum.get('name')).first()
            role.authorizations.append(auth)
    db.session.add(role)

    # Creates Teacher Role
    data = {
        'id': 5,
        'name': 'Teacher',
        'authorizations': [],
        'immutable': False
    }

    role = Role(data)

    with open('data/teacher_authorization.json') as file:
        data = json.load(file)
        for datum in data:
            auth = Authorization.query.filter_by(name=datum.get('name')).first()
            role.authorizations.append(auth)
    db.session.add(role)

    # Creates Instructor Role
    data = {
        'id': 6,
        'name': 'Instructor',
        'authorizations': [],
        'immutable': False
    }

    role = Role(data)

    with open('data/instructor_authorization.json') as file:
        data = json.load(file)
        for datum in data:
            auth = Authorization.query.filter_by(name=datum.get('name')).first()
            role.authorizations.append(auth)
    db.session.add(role)

    db.session.commit()