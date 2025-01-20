from app import create_app
from gevent.pywsgi import WSGIServer

app = create_app()
http_server = WSGIServer(("localhost", 8001), app)
http_server.serve_forever()
