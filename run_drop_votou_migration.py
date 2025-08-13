import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.append(project_root)

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

def run_migration():
    # Read the migration SQL file
    migration_file = os.path.join(project_root, "migrations", "drop_votou_column.sql")
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    # Create a database connection
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Execute the migration in a transaction
            with connection.begin():
                print("Running migration to remove 'votou' column...")
                connection.execute(text(migration_sql))
                print("Migration completed successfully!")
    except Exception as e:
        print(f"Error running migration: {e}")
        raise

if __name__ == "__main__":
    run_migration()
