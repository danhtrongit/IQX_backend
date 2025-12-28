"""Password hashing implementation."""
import bcrypt


class PasswordHasher:
    """Bcrypt password hasher."""
    
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
    
    def hash(self, password: str) -> str:
        """Hash a password."""
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    def verify(self, password: str, hash: str) -> bool:
        """Verify a password against a hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hash.encode("utf-8"))
        except Exception:
            return False
