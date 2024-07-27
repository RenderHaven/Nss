from app import db, User, Event, MyEvt, Note, app

# Define user and event data
users_data = {
    'Stu_2201cs76_vikram@iitp.ac.in': {
        'UserId': 'Stu_2201cs76_vikram@iitp.ac.in',
        'MyInfo': {
            'Name': 'Vikram Balai',
            'Roll': '2201CS76',
            'Attendance': 10.0,
            'Ment_id': 'Men_2201cb76_utkarsh@iitp.ac.in'
        },
        'MyNote': [],
        'MyEvt': [],
        'MyStu': [],
    },
    'Stu_2201cb65_vipin@iitp.ac.in': {
        'UserId': 'Stu_2201cb65_vipin@iitp.ac.in',
        'MyInfo': {
            'Name': 'Vipin Gupta',
            'Roll': '2201CB65',
            'Attendance': 10.0,
            'Ment_id': 'Men_2201cb76'
        },
        'MyNote': [],
        'MyEvt': [],
        'MyStu': [],
    },
    'Stu_2201mm40_manoj@iitp.ac.in': {
        'UserId': 'Stu_2201mm40_manoj@iitp.ac.in',
        'MyInfo': {
            'Name': 'Manoj Kumar',
            'Roll': '2201CS76',
            'Attendance': 6.0,
            'Ment_id': 'Men_2201cb76_utkarsh@iitp.ac.in'
        },
        'MyNote': [],
        'MyEvt': [],
        'MyStu': [],
    },
    'Stu_2201ee67': {
        'UserId': 'Stu_2201ee67',
        'MyInfo': {
            'Name': 'Shiva Singh',
            'Roll': '2201EE67',
            'Attendance': 10.0,
            'Ment_id': 'Men_2201cb65'
        },
        'MyNote': [],
        'MyEvt': [],
        'MyStu': [],
    },
    'Stu_2201ph25': {
        'UserId': 'Stu_2201ph25',
        'MyInfo': {
            'Name': 'Sataym Jhat',
            'Roll': '2201PH25',
            'Attendance': 10.0,
            'Ment_id': 'Men_2201cb76_utkarsh@iitp.ac.in'
        },
        'MyNote': [],
        'MyEvt': [],
        'MyStu': [],
    },
    'Stu_2201ce69': {
        'UserId': 'Stu_2201ce69',
        'MyInfo': {
            'Name': 'Rohit ji',
            'Roll': '2201CE69',
            'Attendance': 10.0,
            'Ment_id': 'Men_2201cb76_utkarsh@iitp.ac.in'
        },
        'MyNote': [],
        'MyEvt': [],
        'MyStu': [],
    },
    'Men_2201cb76_utkarsh@iitp.ac.in': {
        'UserId': 'Men_2201cb76_utkarsh@iitp.ac.in',
        'MyInfo': {
            'Name': 'Utkarsh Bhai',
            'Roll': '2101EE76',
            'Attendance': 0,
        },
        'MyNote': [],
        'MyStu': ['Stu_2201cs65'],
        'MyEvt': [],
    },
    'Men_2201cb65_muskan@iitp.ac.in': {
        'UserId': 'Men_2201cb65_muskan@iitp.ac.in',
        'MyInfo': {
            'Name': 'Muskan Jha',
            'Roll': '2101CB65',
            'Attendance': 0,
        },
        'MyNote': [],
        'MyStu': ['Stu_2201cs76'],
        'MyEvt': [],
    },
    'Gen_2201cb65': {
        'UserId': 'Gen_2201cb65',
        'MyInfo': {
            'Name': 'Bala Krishna',
            'Roll': '2101CB65',
            'Attendance': 0,
        },
        'MyNote': [],
        'MyStu': [],
        'MyEvt': [],
    }
}

event_data = {
    "Evt1": {
        "EvtId": 'Evt1',
        "name": "Cloth Distribution",
        "date": "19-07-24",
        "wing": "Rural Development",
        "isnew": True,
    },
    "Evt2": {
        "EvtId": 'Evt2',
        "name": "Another Event",
        "date": "19-07-24",
        "wing": "Technical Skills",
        "isnew": False,
    },
    "Evt3": {
        "EvtId": 'Evt3',
        "name": "Upcoming",
        "date": "9-05-24",
        "wing": "Technical Skills",
        "isnew": True,
    }
}

def insert_data():
    db.create_all()

    # Insert events
    for evt_id, evt_info in event_data.items():
        new_event = Event(
            event_id=evt_info['EvtId'],
            name=evt_info['name'],
            date=evt_info['date'],
            wing=evt_info['wing'],
            isnew=evt_info['isnew']
        )
        db.session.add(new_event)

    # Insert users and related data
    for user_id, user_info in users_data.items():
        new_user = User(
            user_id=user_info['UserId'],
            name=user_info['MyInfo']['Name'],
            roll=user_info['MyInfo']['Roll'],
            attendance=user_info['MyInfo'].get('Attendance', 0),
            ment_id=user_info['MyInfo'].get('Ment_id', ''),
            isok=True,
            password='1234567890',
        )
        db.session.add(new_user)

        # Insert notes
        for note in user_info['MyNote']:
            new_note = Note(
                note=note,
                user=new_user
            )
            db.session.add(new_note)

        # Insert MyEvt relationships
        for evt_id in user_info['MyEvt']:
            event = Event.query.filter_by(event_id=evt_id).first()
            if event:
                new_my_evt = MyEvt(
                    user=new_user,
                    event=event
                )
                db.session.add(new_my_evt)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_data()
    print("Data inserted successfully")
