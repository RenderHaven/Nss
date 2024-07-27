from flask import Flask, jsonify, request

from collections import OrderedDict
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import desc
from sqlalchemy import or_
from sqlalchemy import case
import base64
#----------------------------------------------------------------------

#-----------------------------------------------------------------------

app = Flask(__name__)
CORS(app)

# Configure SQLite connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    user_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    roll = db.Column(db.String(100), nullable=False)
    attendance = db.Column(db.Float)
    ment_id = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.LargeBinary)
    isok=db.Column(Boolean,default=False)
    password=db.Column(db.String(100), nullable=False)
    fcm_token = db.Column(db.String(256), nullable=True)
    # Relationships
    my_note = relationship("Note", back_populates="user")
    my_evt = relationship("MyEvt", back_populates="user")


    def __repr__(self):
        return f'<User {self.user_id}>'

# Define Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('user.user_id'))
    type = db.Column(db.String(10))  #NewEvt ,#EvtSubm ,#NewUser
    owner_id = db.Column(db.String(100))
    event_id = db.Column(db.String(100))
    note = db.Column(db.String, nullable=False)
    hours=db.Column(db.Float)
    user = relationship("User", back_populates="my_note")

    def to_dict(self):
        return {
            'NoteId': self.id,
            'UserId': self.user_id,
            'OwnerId': self.owner_id,
            'EventId': self.event_id,
            'Note': self.note,
            'Hours': self.hours,
            'Type':self.type,
        }


    def __repr__(self):
        return f'<Note {self.note}>'

# Define Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(500), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    wing = db.Column(db.String(100))
    time = db.Column(db.String(100))
    isnew = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Event {self.event_id}>'

# Define MyEvt model (Many-to-many relationship between User and Event)
class MyEvt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('user.user_id'))
    event_id = db.Column(db.Integer, ForeignKey('event.event_id'))
    image = db.Column(db.LargeBinary)
    comment = db.Column(db.String(100))
    isok=db.Column(Boolean,default=False)
    user = relationship("User", back_populates="my_evt")
    event = relationship("Event")
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------


@app.route('/update_token', methods=['POST'])
def update_token():
    user_id = request.json.get('user_id')
    fcm_token = request.json.get('fcm_token')

    user = User.query.get(user_id)
    if user:
        user.fcm_token = fcm_token
        db.session.commit()
        return jsonify({'message': 'FCM token updated successfully'}), 200
    return jsonify({'message': 'User not found'}), 404
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------

def user_by_id(id):
    try:
        user = User.query.filter_by(user_id=id).first()
        if not user:return False
        mystu = User.query.filter_by(ment_id=user.user_id).all()
        data = {
            'UserId': user.user_id,
            'Pass':user.password,
            'MyInfo': {
                'Name': user.name,
                'Roll': user.roll,
                'MentorId': user.ment_id,
                'Attendance': user.attendance,
                'IsOk':user.isok,
                'ProfileImage':base64.b64encode(user.profile_image).decode('utf-8')if user.profile_image is not None else None,
            },
            'MyNote': [note.note for note in user.my_note],
            'MyEvt': [evt.event.event_id for evt in user.my_evt],
            'MyStu': [stu.user_id for stu in mystu]
        }
        return data
    except Exception as e:
        return {'error': str(e)}

# Routes for Users
@app.route('/userslist/<string:ment_id>/<string:like>', methods=['GET'])
def handle_users(ment_id, like):
    if ment_id == 'all':
        users = User.query.with_entities(User.user_id, User.name, User.ment_id,User.isok).filter(User.user_id.like(like + '%')).order_by(
        case(
            (User.isok == False, 1), 
            else_=0
        ).desc(), 
        User.name
    ).all()
    else:
        users = User.query.with_entities(User.user_id, User.name, User.ment_id,User.isok).filter(User.ment_id == ment_id).order_by(
        case(
            (User.isok == False, 1), 
            else_=0
        ).desc(), 
        User.name
    ).all()
    
    # Convert the result to a list of dictionaries
    users_dict = [dict(UserId=user.user_id, Name=user.name, Ment=user.ment_id,IsOk=user.isok) for user in users]
    
    return jsonify(users_dict)

# Route for updating user profile image and other details
@app.route('/users/update/<string:user_id>', methods=['POST'])
def update_user(user_id):
    data = request.json
    print(data)
    
    user = User.query.filter_by(user_id=user_id).first()
    if 'Delete' in data:
        if user:
            db.session.merge(user)
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Event Deleted'}), 200
        else:
            return jsonify({'message': 'Event Not Found'}), 404
    if not user:
        # Create a new user if not found
        user = User(user_id=user_id)
        db.session.add(user)
        
    if 'Name' in data:
        user.name = data['Name']
    if 'Roll' in data:
        user.roll = data['Roll']
    if 'Pass' in data:
        user.password=data['Pass']
    if 'Attendance' in data:
        user.attendance = data['Attendance']
    else:
        user.attendance = 0
    if 'MentorId' in data:
        user.ment_id = data['MentorId']
    if 'ProfileImage' in data:
        image_blob = base64.b64decode(data['ProfileImage'])
        user.profile_image = image_blob
    if 'IsOk' in data:
        user.isok=data['IsOk']

    db.session.commit()

    return jsonify({'message': 'User updated successfully', 'user': user_by_id(user_id)}), 200

@app.route('/users/<string:user_id>', methods=['GET'])
def handle_user(user_id):
    if user_id.lower() == 'all':
        users = User.query.all()
        user_data = {}
        for user in users:
            user_data[user.user_id] = user_by_id(user.user_id)
        return jsonify(user_data)
    else:
        return jsonify(user_by_id(user_id))
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------


def event_by_id(id):
    try:
        event = Event.query.filter_by(event_id=id).first()
        data = {
            'EvtId': event.event_id,
            'name': event.name,
            'date': event.date,
            'wing': event.wing,
            'isnew': event.isnew,
            'description': event.description,
        }
        return data
    except Exception as e:
        return {'error': str(e)}
# Routes for Events
@app.route('/myeventslist/<string:user_id>', methods=['GET'])
def handle_myevents(user_id):
    My_events = MyEvt.query.filter_by(user_id=user_id).all()

    # Convert the result to a list of dictionaries
    users_dict = [
        {
            'EvtId':My_event.event_id,
            'Name': My_event.event.name,
            'Wing': My_event.event.wing,
            'IsOk': My_event.isok,
            'Date': My_event.event.date
        }
        for My_event in My_events
    ]

    return jsonify(users_dict)

@app.route('/eventuserslist/<string:event_id>', methods=['GET'])
def handle_myeventusers(event_id):
    My_events = MyEvt.query.filter_by(event_id=event_id).all()

    # Convert the result to a list of dictionaries
    users_dict = {
        My_event.user_id:{
            'EvtId':My_event.event_id,
            'Name': My_event.user.name,
            'UserId': My_event.user_id,
            'IsOk': My_event.isok,
            'IsNew':My_event.event.isnew,
            #'Date': My_event.event.date
        }
        for My_event in My_events
    }

    return jsonify(users_dict)

@app.route('/eventslist/<string:ByWing>', methods=['GET'])
def handle_events(ByWing):
    users = Event.query.with_entities(
        Event.event_id, 
        Event.name, 
        Event.date, 
        Event.isnew, 
        Event.wing
    ).order_by(
        case(
            (Event.wing == ByWing, 1), 
            else_=0
        ).desc(), 
        Event.date
    ).all()

    # Convert the result to a list of dictionaries
    users_dict = [dict(EvtId=user.event_id, Name=user.name, Date=user.date, IsNew=user.isnew, Wing=user.wing) for user in users]

    return users_dict

@app.route('/events/<string:event_id>', methods=['GET'])
def handle_event(event_id):
    if event_id.lower() == 'all':
        events = Event.query.order_by(Event.name).all()
        event_data = OrderedDict()
        event_data = {event.event_id: event_by_id(event.event_id) for event in events}
        return jsonify(event_data)
    else:
        return jsonify(event_by_id(event_id))

@app.route('/events/add', methods=['POST'])
def add_event():
    data = request.json
    print(data)
    name = data.get('name')
    date = data.get('date')
    wing = data.get('wing')
    time = data.get('time')
    description = data.get('description')
    if not name or not date:
        return jsonify({'error': 'Missing required fields: name, date'}), 400

    last_event = Event.query.order_by(Event.id.desc()).first()
    if last_event:
        event_id = 'Evt' + str(last_event.id + 1)
    else:
        event_id = 'Evt1'  # Initial event_id if no events exist

    new_event = Event(
        event_id=event_id,
        time=time,
        name=name,
        date=date,
        wing=wing,
        isnew=True,  # Assuming new events are always marked as new
        description=description
    )
    with app.app_context():
        db.session.add(new_event)
        db.session.commit()

        event_data = {
            'event_id': new_event.event_id,
            'name': new_event.name,
            'date': new_event.date,
            'wing': new_event.wing,
            'isnew': new_event.isnew
        }
        return jsonify(event_data), 200

@app.route('/events/addimg', methods=['POST'])
def add_image():
    data = request.json
    print(data)
    user_id = data.get('UserId')
    event_id = data.get('EventId')
    if not user_id or not event_id:
        return jsonify({'error': 'Missing required fields: user_id, event_id'}), 400
    My_event = MyEvt.query.filter_by(user_id=user_id ,event_id=event_id).first()

    print(My_event)
    if not My_event :
        with app.app_context():
            My_event=MyEvt(user_id=user_id,event_id=event_id)
            db.session.add(My_event)
            db.session.commit()
    My_event = MyEvt.query.filter_by(user_id=user_id ,event_id=event_id).first()
    if 'Image' in data:
        image_blob = base64.b64decode(data['Image'])
        My_event.image = image_blob
    if 'Comment' in data:
        My_event.comment = data['Comment']
    if 'IsOk' in data:
        My_event.isok=True
    db.session.commit()
    return jsonify({'message': 'Image added successfully'}), 200

@app.route('/events/getimg', methods=['POST'])
def get_event_img():
    data = request.json
    event_id = data['EventId']
    user_id = data['UserId']
    try:
        my_event = MyEvt.query.filter_by(event_id=event_id, user_id=user_id).first()
        if my_event is None:
            return jsonify({'error': 'Event not found'}), 404
        final_data = {
            'EventName': my_event.event.name,
            'UserName': my_event.user.name,
            'Image': base64.b64encode(my_event.image).decode('utf-8') if my_event.image is not None else None,
            'Comment': my_event.comment,
            'IsOk':my_event.isok,
        }
        return jsonify(final_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/deletemyevent/<string:UserId>/<string:EventId>', methods=['GET', 'POST'])
def delete(UserId, EventId):
    try:
        item = MyEvt.query.filter_by(user_id=UserId, event_id=EventId).first()
        if item:
            db.session.merge(item)
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': 'Event Deleted'}), 200
        else:
            return jsonify({'message': 'Event Not Found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------

    
#for Notifications
@app.route('/notes/add', methods=['POST'])
def add_note():
    data = request.get_json()
    prefixes = data.get('Receiver')
    owner_id = data.get('Sender')
    event_id = data.get('EventId')
    note_content = data.get('Note')
    hours = data.get('Hours')
    type_=data.get('Type')
    print(prefixes)
    users = db.session.query(User).filter(
    or_(*[User.user_id.like(prefix) for prefix in prefixes])).all()
    print(users)
    for user in users:
        print(user.user_id)
        new_note = Note(
            user_id=user.user_id,
            owner_id=owner_id,
            event_id=event_id,
            note=note_content,
            hours=hours,
            type=type_,
        )

        db.session.add(new_note)
    db.session.commit()

    return jsonify({"message": "Note added successfully!"}), 201

@app.route('/notes/get/<string:UserId>', methods=['GET'])
def get_note(UserId):
    # Query to get all notes for the given UserId
    notes = Note.query.filter_by(user_id=UserId).all()
    
    # Convert notes to a list of dictionaries
    notes_data = [note.to_dict() for note in notes]

    return jsonify(notes_data), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
