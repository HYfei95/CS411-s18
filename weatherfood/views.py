import flask
from weatherfood import api
from weatherfood import application

app = application.app
google = application.google_login
temp = {}

@app.route('/home', methods=['GET'])
def index():
    return flask.render_template('index.html')

@app.route('/weather', methods=['GET','POST'])
def weather():
    f = open("username.txt", "r")
    username = f.read()

    if( api.get_weather_pretty(flask.request.form.get("zipcode")) != "Unavailable" ):
        current_weather = api.get_weather_pretty(
            flask.request.form.get("zipcode"))
    else:
        current_weather = api.retreive_user(username)["Weather"]

    api.update_zipcode(username, flask.request.form.get("zipcode"))
    api.update_weather(username, current_weather)
    
    return flask.render_template('result.html', weather=current_weather)

@app.route('/', methods=['GET'])
def login():
    return flask.render_template('home.html', url=google.authorization_url())

@google.login_success
def login_success(token, profile):
    result = flask.jsonify(token=token, profile=profile)
    username = result.get_json()["profile"]["email"]
    api.create_user(username)
    f = open("username.txt", "w")
    f.write("{}".format(username))
    return flask.render_template('index.html')

@google.login_failure
def login_failure(e):
    return flask.jsonify(error=str(e))

@app.route('/customrecipe', methods=['POST'])
def show_recipe():
    current_recipe = api.Recipe_from_input(
        flask.request.form.get("recipe"))
    temp.clear()
    temp.update(current_recipe)
    return flask.render_template('custom_recipe.html', recipe=current_recipe)

@app.route('/viewfavorites', methods=['GET'])
def show_favorites():
    f = open("username.txt", "r")
    username = f.read()
    return flask.render_template( 'favorites.html', favorites = api.retreive_user(username)["Fav_Recipes"] )

@app.route("/del_fav", methods=["GET"])
def delete_favorite():
    f = open("username.txt", "r")
    username = f.read()
    api.delete_favorite(username, flask.request.values.get('delete'))
    return flask.render_template( 'favorites.html', favorites = api.retreive_user(username)["Fav_Recipes"] )

@app.route('/fav_recipe', methods=['GET'])
def favorite_recipe():
    f = open("username.txt", "r")
    username = f.read()
    api.update_recipe(username, flask.request.values.get('key'), flask.request.values.get('favorite') )
    return flask.render_template('custom_recipe.html', recipe=temp)
