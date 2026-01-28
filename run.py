import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')


@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')


@app.cli.command('drop-db')
def drop_db():
    """Drop all database tables."""
    if input('Are you sure you want to drop all tables? (y/N): ').lower() == 'y':
        db.drop_all()
        print('Database tables dropped.')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
