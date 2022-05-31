import click
import random
from flask.cli import FlaskGroup
from flask_migrate import Migrate
from faker import Faker
from datetime import datetime

from app import create_app, db, notes_models, accounts_models

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)
Faker.seed(0)
faker = Faker()


@app.shell_context_processor
def make_shell_context() -> dict:
    return dict(app=app,
                db=db,
                Note=notes_models.Note,
                Entry=notes_models.Entry)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command('create_notes')
@click.argument('number_of_notes')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_notes(number_of_notes, username, email, password):
    user = accounts_models.User.find_by_username(username)
    if not user:
        hashed_password = accounts_models.User.generate_password_hash(password)
        user = accounts_models.User(username=username, email=email, password=hashed_password, active=True)
        user.save_to_db()
        profile = accounts_models.Profile(user=user)
        profile.generate_gravatar_url()
        profile.save_to_db()
    for _ in range(int(number_of_notes)):
        note = notes_models.Note(
            title=faker.text(max_nb_chars=50).title(),
            description=faker.text(max_nb_chars=150),
            created=faker.date_time_between(),
            updated=faker.date_time_between(),
            user_id=user.id,
        )
        note.save_to_db()


@cli.command('create_entries')
@click.argument('number_of_entries')
def create_entries(number_of_entries):
    notes_ids = [note.id for note in notes_models.Note.get_all()]
    for _ in range(int(number_of_entries)):
        entry = notes_models.Entry(
            content = faker.text(max_nb_chars=1000),
            note_id = random.choice(notes_ids),
            created = faker.date_time_between(),
            updated = faker.date_time_between()
        )
        entry.save_to_db()


@cli.command('create_development_user')
@click.argument('email')
def delete_user(email):
    user = accounts_models.User.find_by_email(email)
    if not user:
        user.profile.delete_from_db()
        user.delete_from_db()
        print('User was deleted.')
    else:
        print('No user for given e-mail.')


@cli.command('create_js')
def create_js():
    import subprocess
    subprocess.run(["npm", "run", "build"], cwd='frontend_scripts')


if __name__ == "__main__":
    cli()
