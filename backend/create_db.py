from app.database import engine, Base
from app.models import AtomicNote, UserRevision

print("Creating tables in Postgres...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")