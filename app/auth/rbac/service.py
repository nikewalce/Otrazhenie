from app.db.models import User, Role


class RBACService:

    @staticmethod
    def assign_role(
        session,
        user: User,
        role_name: str
    ):
        role = (
            session.query(Role)
            .filter_by(name=role_name)
            .first()
        )

        if not role:
            raise ValueError(
                f"Роль '{role_name}' не найдена"
            )

        if role not in user.roles:
            user.roles.append(role)

    @staticmethod
    def remove_role(
        user: User,
        role_name: str
    ):
        user.roles = [
            role
            for role in user.roles
            if role.name != role_name
        ]

if __name__ == "__main__":
    user = RBACService.assign_role(session='', user='', role_name='')
