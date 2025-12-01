from vercel_wsgi import handle

from website import create_app

app = create_app()


def handler(event, context):
    return handle(app, event, context)
