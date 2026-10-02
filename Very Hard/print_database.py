from app import app, db, User, Chat, Message  # Importing models and app from the main application

def print_users():
    """Print all users in the database."""
    users = User.query.all()
    print("\nUsers:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Password: {user.password}")

def print_chats():
    """Print all chats in the database."""
    chats = Chat.query.all()
    print("\nChats:")
    for chat in chats:
        visibility = "Public" if chat.visible else "Private"
        print(f"ID: {chat.id}, Title: {chat.title}, Owner ID: {chat.owner_id}, Visibility: {visibility}")

def print_messages():
    """Print all messages in the database."""
    messages = Message.query.all()
    print("\nMessages:")
    for message in messages:
        print(f"ID: {message.id}, Chat ID: {message.chat_id}, User ID: {message.user_id}, Content: {message.content}")

if __name__ == "__main__":
    # Use the Flask application context for database operations
    with app.app_context():
        print("Printing database contents...")
        print_users()
        print_chats()
        print_messages()
        print("\nDatabase printing completed.")
