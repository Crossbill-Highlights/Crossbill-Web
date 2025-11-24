from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.database import DatabaseSession
from src.models import User
from src.schemas.user_schemas import UserDetailsResponse, UserUpdateRequest
from src.services.auth_service import get_current_user, hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserDetailsResponse:
    """Get the current user's profile information."""
    return UserDetailsResponse(name=current_user.name, id=current_user.id)


@router.post("/me")
async def update_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: DatabaseSession,
    update_data: UserUpdateRequest,
) -> UserDetailsResponse:
    """
    Update the current user's profile.

    - To change name: provide `name` field
    - To change password: provide both `current_password` and `new_password` fields
    """
    # Validate password change request
    if update_data.new_password is not None:
        if update_data.current_password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required when changing password",
            )
        # Verify current password
        if not current_user.hashed_password or not verify_password(
            update_data.current_password, current_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

    # Update name if provided
    if update_data.name is not None:
        current_user.name = update_data.name

    # Update password if provided
    if update_data.new_password is not None:
        current_user.hashed_password = hash_password(update_data.new_password)

    db.commit()
    db.refresh(current_user)

    return UserDetailsResponse(name=current_user.name, id=current_user.id)
