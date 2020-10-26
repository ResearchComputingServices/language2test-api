import json

def populate(db, models):

    Enumeration = models.enumeration.Enumeration
    EnumerationValue = models.enumeration.EnumerationValue

    #Creates Language Enumeration
    data = {
        'id': 1,
        'name' : 'Language',
        'values' : [],
    }

    enumeration = Enumeration(data)
    db.session.add(enumeration)

    #Add Language Enumeration Values
    with open('data/languages.txt') as file:
        for line in file:
             d={}
             d['text'] = line
             d['enumeration_id'] = enumeration.id
             value = EnumerationValue(d)
             db.session.add(value)
             enumeration.values.append(value)

    #Creates Countries Enumeration
    data = {
        'id': 2,
        'name': 'Country',
        'values': [],
    }

    enumeration = Enumeration(data)
    db.session.add(enumeration)

    # Add Country Enumeration Values
    with open('data/countries.txt') as file:
        for line in file:
            d = {}
            d['text'] = line
            d['enumeration_id'] = enumeration.id
            value = EnumerationValue(d)
            db.session.add(value)
            enumeration.values.append(value)

    # Creates Education Enumeration
    data = {
        'id': 3,
        'name': 'Education',
        'values': [],
    }

    enumeration = Enumeration(data)
    db.session.add(enumeration)

    # Add Country Enumeration Values
    with open('data/education.txt') as file:
        for line in file:
            d = {}
            d['text'] = line
            d['enumeration_id'] = enumeration.id
            value = EnumerationValue(d)
            db.session.add(value)
            enumeration.values.append(value)
    db.session.commit()
