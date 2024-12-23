import json
from glom import assign  # Import only the required function
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GDtfDCFYjD'

current_user = None

class User:
  def __init__(self, data):
    self.id = data.get('id')
    self.userInfo = {
        'name': data.get('name'),
        'email': data.get('email'),
        'age': data.get('age')
    }

def update_user(user, key, value):
  global current_user
  current_user = assign(user, key, value)

@app.route('/register', methods=['POST'])
def register():
  data = json.loads(request.data)
  user = User(data)
  global current_user
  current_user = user
  return jsonify({'message': 'User registered successfully', 'userInfo': current_user.userInfo})

@app.route('/update', methods=['POST'])
def update():
  data = json.loads(request.data)
  key = data.get('key')
  value = data.get('value')

  try:
    global current_user
    update_user(current_user, key, value)
    return jsonify({'message': 'User updated successfully', 'userInfo': current_user.userInfo})
  except KeyError as e:
    return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run()