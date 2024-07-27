from app import app, db, User, Event

# Function to print all users
def print_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"User ID: {user.user_id}, Name: {user.name}, Roll: {user.roll}")

# Function to print all events
def print_events():
    with app.app_context():
        events = Event.query.all()
        for event in events:
            print(f"Event ID: {event.event_id}, Name: {event.name}, Date: {event.date}")

if __name__ == '__main__':
    print("Users:")
    print_users()
    
    print("\nEvents:")
    print_events()
