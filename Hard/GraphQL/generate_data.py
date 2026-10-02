# generate_data.py
from faker import Faker
import random
import string

faker = Faker()

# Configuration
NUM_USERS = 100
POSTS_PER_USER = 5
COMMENTS_PER_POST = 3

# Generate dummy data
users = []
posts = []
comments = []

# Hidden flag
flag = "CTF{GraphQL_Injection_Flag}"

# Randomly choose where to insert the flag
flag_location = random.choice(['user', 'post', 'comment'])

roles = ['admin', 'user']

def generate_random_password(length=10):
    # Generate a random password using letters, digits, and punctuation
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

for i in range(1, NUM_USERS + 1):
    role = random.choice(roles)
    password = generate_random_password()  # Generate random password for each user
    user = {
        'id': i,
        'username': faker.user_name(),
        'email': faker.email(),
        'password': password,  # Store the plaintext password
        'role': role,
    }
    
    if flag_location == 'user' and random.random() < 0.01:
        user['email'] = f"{faker.user_name()}@{flag}.com"
    
    users.append(user)
    
    for j in range(1, POSTS_PER_USER + 1):
        post_id = len(posts) + 1
        post = {
            'id': post_id,
            'title': faker.sentence(),
            'content': faker.text(),
            'user_id': i,
        }
        
        if flag_location == 'post' and random.random() < 0.01:
            post['content'] += f"\n\n{flag}"
        
        posts.append(post)
        
        for k in range(1, COMMENTS_PER_POST + 1):
            comment_id = len(comments) + 1
            comment = {
                'id': comment_id,
                'text': faker.sentence(),
                'post_id': post_id,
            }
            
            if flag_location == 'comment' and random.random() < 0.01:
                comment['text'] += f" {flag}"
            
            comments.append(comment)

# Write to the models.py file
with open('models.py', 'w') as f:
    f.write("# models.py\n\n")
    f.write("users = [\n")
    for user in users:
        f.write(f"    {user},\n")
    f.write("]\n\n")
    
    f.write("posts = [\n")
    for post in posts:
        f.write(f"    {post},\n")
    f.write("]\n\n")
    
    f.write("comments = [\n")
    for comment in comments:
        f.write(f"    {comment},\n")
    f.write("]\n")

print(f"Data generated with the flag hidden in a {flag_location}.")
