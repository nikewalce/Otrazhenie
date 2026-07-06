# Константы для разрешений и ролей

PERMISSIONS = {
    "ingredients:create": "Создание ингредиентов",
    "ingredients:update": "Редактирование ингредиентов",
    "ingredients:delete": "Удаление ингредиентов",

    "admin:panel": "Доступ в админку",
}


ROLES = {
    "user": {
        "description": "Обычный пользователь",
        "permissions": [],
    },

    "ingredient_manager": {
        "description": "Управление ингредиентами",
        "permissions": [
            "ingredients:create",
            "ingredients:update",
        ],
    },

    "admin": {
        "description": "Полный доступ",
        "permissions": list(PERMISSIONS.keys()),
    },
}
