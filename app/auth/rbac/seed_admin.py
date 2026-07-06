from app.db.crud import OtrazhenieDB
from app.db.models import User

from app.auth.rbac.service import RBACService


class AdminSeeder:

    def __init__(self):
        self.db = OtrazhenieDB()

    def seed(self, email: str):

        with self.db.get_session() as session:

            user = (
                session.query(User)
                .filter_by(email=email)
                .first()
            )

            if not user:
                raise RuntimeError(
                    f"Пользователь {email} не найден"
                )

            RBACService.assign_role(
                session=session,
                user=user,
                role_name="admin",
            )

            session.commit()

if __name__ == '__main__':
    admin = AdminSeeder()
    admin.seed(email="")
