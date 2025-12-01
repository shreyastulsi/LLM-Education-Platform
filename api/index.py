from website import create_app

app = create_app()


def handler(event, context):
    import serverless_wsgi

    return serverless_wsgi.handle_request(app, event, context)
