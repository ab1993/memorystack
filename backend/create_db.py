# create_db.py
from app.database import engine, Base
# Important: Import all your models here so SQLAlchemy knows about them
from app.models import AtomicNote, UserRevision, User

print("🔥 Dropping old tables...")
Base.metadata.drop_all(bind=engine)

print("🏗️ Creating new tables in Postgres...")
Base.metadata.create_all(bind=engine)

print("✅ Tables recreated successfully with the new schema!")