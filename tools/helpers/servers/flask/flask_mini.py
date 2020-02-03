from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Index Page'


@app.route('/hello')
def hello():
    return 'Hello, World'


@app.route('/content/<path:page_name>')
def load_page(page_name):
    return page_name


if __name__ == '__main__':
    app.run(host="localhost", debug="development")
