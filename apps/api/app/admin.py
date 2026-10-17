from typing import Annotated

from fastapi import Depends, HTTPException

from app.config import get_settings
from app.models import User
from app.security import require_user


def require_admin(user: Annotated[User, Depends(require_user)]) -> User:
    admin_email = (get_settings().admin_email or "").strip().lower()
    if not admin_email or user.email.strip().lower() != admin_email:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


AdminUserDep = Annotated[User, Depends(require_admin)]
