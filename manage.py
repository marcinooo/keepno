import click
import random
from flask.cli import FlaskGroup
from flask_migrate import Migrate
from faker import Faker
from datetime import datetime

from app import create_app, db, notes_models

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
def create_notes(number_of_notes):
    for _ in range(int(number_of_notes)):
        note = notes_models.Note(
            title=faker.text(max_nb_chars=50).title(),
            description=faker.text(max_nb_chars=150),
            created=faker.date_time_between(),
            updated=faker.date_time_between()
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


if __name__ == "__main__":
    cli()
