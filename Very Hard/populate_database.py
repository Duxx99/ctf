from app import app, db, User, Chat, Message  # Importing models and app from the main application
from sqlalchemy.exc import IntegrityError
from random import choice, randint

# Sample data for users, chat titles, and messages
users_data = [
    {"username": "elliot", "password": "fsociety"},
    {"username": "darlene", "password": "wh1t3r0se"},
    {"username": "mrrobot", "password": "revolution"},
]

# Mr. Robot-themed chat titles
chat_titles = [
    "fsociety Meeting",
    "Hack the Planet",
    "Dark Army Discussions",
    "Root Access",
    "Operation Berenstain",
    "Zero-Day Exchange",
    "Revolution Planning",
]

# Mr. Robot-themed messages
messages = [
    "The world is a lie.",
    "Are you in?",
    "We're in control now.",
    "Time to delete the debt.",
    "The revolution is coming.",
    "You're just a glitch in the system.",
    "I see the world differently.",
    "They can't stop us.",
    "We are fsociety.",
    "The Dark Army is watching.",
    "Delete all the data. Burn it all.",
    "We're the ones we've been waiting for.",
    "Power belongs to those who take it.",
    "Encryption is our shield.",
    "It's time to wake up.",
]

def create_users():
    """Creates sample users."""
    print("Creating users...")
    for user_data in users_data:
        user = User(username=user_data["username"], password=user_data["password"])
        db.session.add(user)
        try:
            db.session.commit()
            print(f"User {user.username} created.")
        except IntegrityError:
            db.session.rollback()
            print(f"User {user.username} already exists.")

def create_chats():
    """Creates sample public and private chats."""
    print("Creating chats...")
    users = User.query.all()
    for title in chat_titles:
        owner = choice(users)
        # Randomly decide if the chat is public or private
        is_public = choice([True, False])
        chat = Chat(owner_id=owner.id, title=title, visible=is_public)
        db.session.add(chat)
        db.session.commit()
        print(f"Chat '{title}' created by {owner.username} as {'public' if is_public else 'private'}.")

def populate_messages():
    """Populates each chat with random messages."""
    print("Adding messages to chats...")
    users = User.query.all()
    chats = Chat.query.all()
    for chat in chats:
        for _ in range(randint(3, 7)):  # Add a random number of messages to each chat
            user = choice(users)
            message_content = choice(messages)
            message = Message(chat_id=chat.id, user_id=user.id, content=message_content)
            db.session.add(message)
        db.session.commit()
        print(f"Messages added to chat '{chat.title}'.")

if __name__ == "__main__":
    # Use the Flask application context for database operations
    with app.app_context():
        db.create_all()  # Ensure all tables exist
        create_users()
        create_chats()
        populate_messages()
        print("Database population completed.")
