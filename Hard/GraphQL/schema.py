import graphene
import requests
import re
import secrets
from flask import session
from models import users, posts, comments

class UserType(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    role = graphene.String()

class PostType(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    user_id = graphene.Int()

class CommentType(graphene.ObjectType):
    id = graphene.ID()
    text = graphene.String()
    post_id = graphene.Int()

# In-memory session storage (for simplicity)
sessions = {}

# List of restricted substrings for usernames
RESTRICTED_USERNAMES = ['admin', 'administrator', 'test', 'user']

class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(), username=graphene.String())
    post = graphene.Field(PostType, id=graphene.Int(), title=graphene.String())
    comment = graphene.Field(CommentType, id=graphene.Int(), text=graphene.String())
    fetch_data = graphene.String(url=graphene.String(required=True))  # Query for SSRF

    def resolve_user(self, info, id=None, username=None):
        if id:
            return next((user for user in users if user['id'] == id), None)
        if username:
            return next((user for user in users if user['username'] == username), None)
        return None

    def resolve_post(self, info, id=None, title=None):
        # Only allow admins to view posts
        user_id = session.get('token')  # Access the session token directly
        user = next((u for u in users if sessions.get(user_id) == u['id']), None)
        
        if user and user['role'] == 'admin':
            if id:
                return next((post for post in posts if post['id'] == id), None)
            if title:
                return next((post for post in posts if post['title'] == title), None)
        else:
            raise Exception("Unauthorized")

    def resolve_comment(self, info, id=None, text=None):
        if id:
            return next((comment for comment in comments if comment['id'] == id), None)
        if text:
            return next((comment for comment in comments if comment['text'] == text), None)
        return None

    def resolve_fetch_data(self, info, url):
        # Check if the user is an admin
        user_id = session.get('token')  # Access the session token directly
        user = next((u for u in users if sessions.get(user_id) == u['id']), None)
        
        if user and user['role'] == 'admin':
            response = requests.get(url)  # No validation of the URL (SSRF vulnerability)
            return response.text  # Return the fetched data as a string
        else:
            raise Exception("Unauthorized access. Admins only.")

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        role = graphene.String(required=True)

    user = graphene.Field(lambda: UserType)

    def mutate(self, info, username, email, password, role):
        # Check if the username contains any restricted substrings
        for restricted in RESTRICTED_USERNAMES:
            if re.search(restricted, username, re.IGNORECASE):
                raise Exception(f"The username '{username}' contains a restricted word: '{restricted}'")
        
        user_id = len(users) + 1  # Increment the user ID based on the current list length
        new_user = {
            'id': user_id,
            'username': username,
            'email': email,
            'password': password,  # In a real app, you'd hash this
            'role': role,
        }
        users.append(new_user)
        return CreateUser(user=new_user)

class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()

    def mutate(self, info, username, password):
        user = next((user for user in users if user['username'] == username and user['password'] == password), None)

        if user:
            token = secrets.token_hex(16)
            sessions[token] = user['id']  # Store user id in the session
            return Login(token=token)
        return Login(token=None)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login = Login.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
