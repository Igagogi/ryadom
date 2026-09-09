from app.db.database import Base, engine
from app.db.models import User

Base.metadata.create_all(engine)