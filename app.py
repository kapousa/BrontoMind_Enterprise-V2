from flask import Flask

app = Flask(__name__)

# Set the session timeout to 5 minutes (300 seconds)
app.config['PERMANENT_SESSION_LIFETIME'] = 30

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
