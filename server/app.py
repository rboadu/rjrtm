from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return {'status': 'ok', 'service': 'rjrtm-api', 'version': '0.1'}

if __name__ == '__main__':
    app.run(debug=True)
