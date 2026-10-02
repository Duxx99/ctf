from app import app, db, User, Chat, Message  # Import models and app from the main application
from sqlalchemy.exc import IntegrityError

# Specific user and chat details
user1_data = {"username": "user1", "password": "4a4e166c06659911881f383d4473e94f"}
user2_data = {"username": "user2", "password": "ef92b778bafe771e89245b89ecbc08a4"}
chat_data = {
    "title": "Chat Between Two Users",  # Title of the chat room
    "owner_username": "user1",  # Initially set the owner to the first user
    "visibility": False,  # Set True for public, False for private
}

def create_user(user_data):
    """Creates a specific user if not already in the database."""
    print(f"Creating user {user_data['username']}...")
    user = User(username=user_data["username"], password=user_data["password"])
    db.session.add(user)
    try:
        db.session.commit()
        print(f"User {user.username} created.")
    except IntegrityError:
        db.session.rollback()
        print(f"User {user.username} already exists.")

def create_specific_chat():
    """Creates a specific chat room between two users and populates it with messages."""
    print("Creating specific chat room...")

    # Retrieve or create the owner and participant users
    owner = User.query.filter_by(username=chat_data["owner_username"]).first()
    participant = User.query.filter_by(username=user2_data["username"]).first()

    if not owner or not participant:
        print(f"One or both users do not exist. Exiting.")
        return

    # Create the chat room with the first user as the owner
    chat = Chat(owner_id=owner.id, title=chat_data["title"], visible=chat_data["visibility"])
    db.session.add(chat)
    db.session.commit()
    print(f"Chat '{chat.title}' created between {owner.username} and {participant.username} as {'public' if chat.visible else 'private'}.")

    # Add messages between the two users
    add_messages(chat, owner, participant)

def add_messages(chat, user1, user2):
    """Add messages to the chat between the two specified users."""
    print("Adding messages to the chat...")
    # Example messages from both users
    messages = [
        {"user_id": user1.id, "content": "Hello! We want to move from traditional authentication to more sophisticated one. Any ideas?"},
        {"user_id": user2.id, "content": "Hi, sure. I guess Keycloak is the best option"},
        {"user_id": user1.id, "content": "Good. Can you start developing it?"},
        {"user_id": user2.id, "content": "Sure. I'm on it!"},
        {"user_id": user2.id, "content": "Update: It is currently in development. API can be accessed on http://172.20.0.3:8080/"},
        # Add more messages as needed
    ]

    for msg in messages:
        message = Message(chat_id=chat.id, user_id=msg["user_id"], content=msg["content"])
        db.session.add(message)

    try:
        db.session.commit()
        print(f"Messages added to chat '{chat.title}'.")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to add messages: {e}")

if __name__ == "__main__":
    # Use the Flask application context for database operations
    with app.app_context():
        db.create_all()  # Ensure all tables exist
        create_user(user1_data)
        create_user(user2_data)
        create_specific_chat()
        print("Database population with specific chat between two users completed.")
