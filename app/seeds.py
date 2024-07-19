from flask_seeder import Seeder, Faker, generator
from app.models import User, Note
from app.config import app, db
import uuid
from faker import Faker as DataFaker


app.app_context().push()

class UserSeeder(Seeder):
    def run(self):
        faker = DataFaker()

        for _ in range(10):
            user = User(
                public_id=str(uuid.uuid4()),
                login=faker.email(),
                password=faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
                admin=faker.boolean()
            )
            db.session.add(user)
        db.session.commit()

class NoteSeeder(Seeder):
    def run(self):
        faker = DataFaker()

        for _ in range(20):
            note = Note(
                title=faker.sentence(nb_words=6),
                content=faker.text(max_nb_chars=200),
                user_id=faker.random_int(min=1, max=10)
            )
            db.session.add(note)
        db.session.commit()



user_seeder = UserSeeder(app)
note_seeder = NoteSeeder(app)

user_seeder.run()
note_seeder.run()
