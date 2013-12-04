from bottle import route, run, template

@route("/keep-alive")
def keep_alive():
    return "Alive"