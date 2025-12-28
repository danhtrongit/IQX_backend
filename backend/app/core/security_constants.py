"""Security constants."""
import re

# Password policy
PASSWORD_MIN_LENGTH = 8
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")
PASSWORD_POLICY_MESSAGE = "Password must be at least 8 characters with letters and numbers"

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Roles
ROLE_USER = "USER"
ROLE_ADMIN = "ADMIN"
VALID_ROLES = {ROLE_USER, ROLE_ADMIN}
