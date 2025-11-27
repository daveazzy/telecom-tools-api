"""Initialize database with tables and sample data"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import init_db, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from datetime import datetime


def create_superuser():
    """Create a default superuser"""
    db = SessionLocal()
    
    try:
        # Check if superuser already exists
        existing = db.query(User).filter(User.is_superuser == True).first()
        if existing:
            print("✓ Superuser already exists")
            return
        
        # Create superuser with a simple password
        password = "admin123"
        superuser = User(
            email="admin@telecom.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        
        db.add(superuser)
        db.commit()
        print("✓ Superuser created successfully")
        print("  Email: admin@telecom.com")
        print("  Password: admin123")
        print("  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")
        
    except Exception as e:
        print(f"✗ Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Initialize database"""
    print("🗄️  Initializing database...")
    
    # Create tables
    init_db()
    print("✓ Database tables created")
    
    # Create superuser
    create_superuser()
    
    print("✅ Database initialization complete!")


if __name__ == "__main__":
    main()

