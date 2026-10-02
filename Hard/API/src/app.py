from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/user', methods=['GET'])
def get_user_data():
    # Get the 'id' parameter from the request
    user_id = request.args.get('id')
    
    # Connect to the SQLite database
    conn = sqlite3.connect('./db/user_data.db')
    cursor = conn.cursor()

    # SQL query vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    # Execute the query
    try:
        cursor.execute(query)
        user_data = cursor.fetchone()
        if user_data:
            return {
                "id": user_data[0],
                "username": user_data[1]
            }
        else:
            return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Close the database connection
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)
