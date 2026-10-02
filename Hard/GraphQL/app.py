from flask import Flask, render_template, request, redirect, url_for, session
from flask_graphql import GraphQLView
from schema import schema, sessions

app = Flask(__name__)
app.secret_key = 'e706386a58190ee13247ffc85c07f5fee617aed1e339cd935e64bab32bfe8fc8'  # Change this to a random key for production

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=False, context={'session': session})
)

@app.route('/')
def index():
    if 'token' in session:
        user_id = sessions.get(session['token'])
        if user_id:
            # Fetch user info using GraphQL to determine where to redirect
            query = """
            {
              user(id: %d) {
                role
              }
            }
            """ % user_id
            
            response = app.test_client().post(
                '/graphql',
                json={'query': query},
                headers={'Content-Type': 'application/json'}
            )
            user_data = response.get_json().get('data', {}).get('user')

            if user_data:
                # Redirect based on user role
                if user_data['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
    
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    query = """
    mutation login($username: String!, $password: String!) {
      login(username: $username, password: $password) {
        token
      }
    }
    """
    username = request.form.get('username')
    password = request.form.get('password')
    variables = {'username': username, 'password': password}

    # Make a POST request to /graphql endpoint
    response = app.test_client().post(
        '/graphql',
        json={'query': query, 'variables': variables},
        headers={'Content-Type': 'application/json'}
    )
    data = response.get_json()

    token = data['data']['login']['token']
    if token:
        session['token'] = token
        return redirect(url_for('index'))  # Redirect to index, which will handle further redirection
    else:
        return "Invalid credentials", 401

@app.route('/admin')
def admin_dashboard():
    if 'token' not in session:
        return redirect(url_for('index'))
    
    user_id = sessions.get(session['token'])
    if not user_id:
        return redirect(url_for('index'))  # Redirect to index if the session is invalid
    
    # Fetch user info to check the role
    query = """
    {
      user(id: %d) {
        role
      }
    }
    """ % user_id
    
    response = app.test_client().post(
        '/graphql',
        json={'query': query},
        headers={'Content-Type': 'application/json'}
    )
    user_data = response.get_json()['data']['user']
    
    if user_data['role'] != 'admin':
        return "Unauthorized access", 403
    
    return render_template('admin.html')

@app.route('/user')
def user_dashboard():
    if 'token' not in session:
        return redirect(url_for('index'))
    
    user_id = sessions.get(session['token'])
    if not user_id:
        return redirect(url_for('index'))  # Redirect to index if the session is invalid
    
    # Fetch user info to check the role
    query = """
    {
      user(id: %d) {
        role
      }
    }
    """ % user_id
    
    response = app.test_client().post(
        '/graphql',
        json={'query': query},
        headers={'Content-Type': 'application/json'}
    )
    user_data = response.get_json()['data']['user']
    
    if user_data['role'] != 'user':
        return "Unauthorized access", 403
    
    return render_template('user.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=80)
