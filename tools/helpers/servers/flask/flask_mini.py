from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return 'Index Page'


@app.route('/hello/')
def hello():
    return render_template("hello_world.html", name="world")


@app.route('/hello/<name>')
def hello_custom(name: str):
    return render_template("hello_world.html", name=name)


@app.route('/sample/<int:score>')
def rendering_sample(score: int):
    dico = {"g": 21, "i": 25, "o": 15}
    name = "Bob"
    return render_template("rendering_template.html", score=score, dico=dico, name=name)


@app.route('/sample/')
def redirect_to_rendering_template():
    return rendering_sample(score=0)


@app.route('/content/<path:page_name>')
def load_page(page_name: str):
    return page_name


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug="development")
