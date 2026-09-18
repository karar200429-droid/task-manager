import argparse

from sqlmodel import Session, select

from app.database import engine
from app.enums import Role
from app.models import User
from app.security import hash_password


def create_admin(
    username: str,
    email: str,
    password: str
):

    with Session(engine) as session:

        existing_username = session.exec(
            select(User).where(
                User.username == username
            )
        ).first()

        if existing_username:

            print("Username already exists.")
            return

        existing_email = session.exec(
            select(User).where(
                User.email == email
            )
        ).first()

        if existing_email:

            print("Email already exists.")
            return

        existing_admin = session.exec(
            select(User).where(
                User.role == Role.admin
            )
        ).first()

        if existing_admin:

            print(
                "An admin already exists. "
                "The first-admin script will not create another one."
            )

            return

        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=Role.admin,
            is_active=True
        )

        session.add(admin)
        session.commit()

        print("Admin created successfully.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Create the first Task Manager admin"
    )

    parser.add_argument(
        "--username",
        required=True
    )

    parser.add_argument(
        "--email",
        required=True
    )

    parser.add_argument(
        "--password",
        required=True
    )

    args = parser.parse_args()

    create_admin(
        args.username,
        args.email,
        args.password
    )