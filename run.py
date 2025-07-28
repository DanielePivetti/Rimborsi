from app import create_app, db
from app.models.user import User
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
