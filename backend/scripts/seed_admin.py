"""Seed admin user script."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.db.session import async_session_factory, init_db
from app.infrastructure.repositories.user_repo import SQLAlchemyUserRepository
from app.infrastructure.security.password import PasswordHasher
from app.core.security_constants import ROLE_ADMIN


async def seed_admin():
    """Create default admin user."""
    await init_db()
    
    async with async_session_factory() as session:
        user_repo = SQLAlchemyUserRepository(session)
        password_hasher = PasswordHasher()
        
        # Check if admin exists
        admin_email = "admin@iqx.local"
        if await user_repo.email_exists(admin_email):
            print(f"Admin user {admin_email} already exists.")
            return
        
        # Create admin
        password_hash = password_hasher.hash("Admin@12345")
        admin = await user_repo.create(
            email=admin_email,
            password_hash=password_hash,
            role=ROLE_ADMIN,
            fullname="Administrator",
        )
        
        await session.commit()
        print(f"Admin user created: {admin.email} (ID: {admin.id})")


if __name__ == "__main__":
    asyncio.run(seed_admin())
