from app.db.crud import OtrazhenieDB
from app.db.models import Role, Permission
from app.auth.rbac.constants import ROLES, PERMISSIONS


class RBACSeeder:
    """
    Инициализация ролей и прав.
    """

    def __init__(self):
        self.db = OtrazhenieDB()

    def seed(self):
        with self.db.get_session() as session:

            permissions = self._create_permissions(session)

            self._create_roles(
                session=session,
                permissions=permissions
            )

            session.commit()

    def _create_permissions(self, session):
        """
        Создает все permissions.
        """

        permissions = {}

        for name, description in PERMISSIONS.items():

            permission = (
                session.query(Permission)
                .filter_by(name=name)
                .first()
            )

            if not permission:
                permission = Permission(
                    name=name,
                    description=description,
                )

                session.add(permission)

            permissions[name] = permission

        session.flush()

        return permissions

    def _create_roles(
        self,
        session,
        permissions: dict
    ):
        """
        Создает роли и связывает их с permissions.
        """

        for role_name, role_data in ROLES.items():

            role = (
                session.query(Role)
                .filter_by(name=role_name)
                .first()
            )

            if not role:
                role = Role(
                    name=role_name,
                    description=role_data["description"]
                )

                session.add(role)

            for permission_name in role_data["permissions"]:

                permission = permissions[permission_name]

                if permission not in role.permissions:
                    role.permissions.append(permission)

if __name__ == "__main__":
    seed_roles_permissions = RBACSeeder()
    seed_roles_permissions.seed()