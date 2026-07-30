from fastapi import HTTPException

from app.models.user import User


def establishment_ids(user: User):

    if user.role == "superadmin":
        return None

    return [
        e.id
        for e in user.establishments
    ]


def ensure_establishment_access(
    establishment_id,
    user: User,
):

    if user.role == "superadmin":
        return

    ids = establishment_ids(user)

    if establishment_id not in ids:
        raise HTTPException(
            403,
            "Você não possui acesso a este estabelecimento."
        )