def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    from .studyMaterialGen import studyMaterialGen
    from .interactWithText import interactWithText
    from .handleUpload import handleUpload
    from .reactiveTest import reactiveTest
    from .userLog import userLog
    app.register_blueprint(studyMaterialGen, url_prefix='/')
    app.register_blueprint(interactWithText, url_prefix='/')
    app.register_blueprint(handleUpload, url_prefix='/')
    app.register_blueprint(reactiveTest, url_prefix='/')
    app.register_blueprint(userLog, url_prefix='/')
    return app