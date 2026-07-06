# RBAC (Role-Based Access Control)

Система разграничения доступа пользователей через роли и права.

## Архитектура

RBAC строится по следующей схеме:

```text
User
 ↓
Role
 ↓
Permission
```

Пример:

```text
User
 └── admin
      ├── ingredients:create
      ├── ingredients:update
      ├── ingredients:delete
      └── admin:panel
```

Если у пользователя есть роль `admin`, то он автоматически получает все permissions, связанные с этой ролью.

---

# Структура проекта

```text
app/
└── auth/
    └── rbac/
        ├── constants.py
        ├── seed_roles_permissions.py
        ├── service.py
        ├── permissions.py
        └── README.md
```

---

# Файлы

## constants.py

Содержит все роли и права системы.

### Permissions

```python
PERMISSIONS = {
    "ingredients:create": "Создание ингредиентов",
    "ingredients:update": "Редактирование ингредиентов",
    "ingredients:delete": "Удаление ингредиентов",
    "admin:panel": "Доступ в админ-панель",
}
```

### Roles

```python
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
```

---

## seed_roles_permissions.py

Создает роли и права в базе данных.

Класс:

```python
RBACSeeder
```

Основные методы:

| Метод                 | Назначение                            |
| --------------------- | ------------------------------------- |
| seed()                | Полная инициализация ролей и прав     |
| _create_permissions() | Создание permissions                  |
| _create_roles()       | Создание ролей и привязка permissions |

---

## service.py

Сервис управления ролями пользователей.

Класс:

```python
RBACService
```

Методы:

```python
assign_role()
remove_role()
```

Пример:

```python
RBACService.assign_role(
    session=session,
    user=user,
    role_name="admin"
)
```

---

## decorators.py

Декораторы защиты Flask View.

Пример:

```python
@permission_required(
    "ingredients:create"
)
def create_ingredient():
    ...
```

Если у пользователя отсутствует permission:

```text
403 Forbidden
```

---

# Инициализация системы

После создания таблиц необходимо создать роли и права.

```python
from app.auth.rbac.seed_roles_permissions import RBACSeeder

RBACSeeder().seed()
```

Что произойдет:

1. Создадутся все permissions.
2. Создадутся все roles.
3. Создадутся связи role → permission.
4. Дубликаты создаваться не будут.

---

# Назначение роли пользователю

Пример выдачи роли администратора:

```python
from app.auth.rbac.service import RBACService

RBACService.assign_role(
    session=session,
    user=user,
    role_name="admin"
)
```

После commit роль будет сохранена в таблице `user_roles`.

---

# Автоматическая роль при регистрации

Рекомендуется автоматически назначать роль `user` каждому новому пользователю.

Пример:

```python
user = User(
    username=username,
    email=email,
    password_hash=password_hash
)

session.add(user)
session.flush()

RBACService.assign_role(
    session=session,
    user=user,
    role_name="user"
)

session.commit()
```

---

# Проверка ролей

В модели User:

```python
user.has_role("admin")
```

Пример:

```python
if current_user.has_role("admin"):
    ...
```

---

# Проверка permissions

В модели User:

```python
user.has_permission(
    "ingredients:create"
)
```

Пример:

```python
if current_user.has_permission(
    "ingredients:create"
):
    ...
```

---

# Защита маршрутов

Пример защиты Flask View:

```python
@app.route("/ingredients/create")
@permission_required(
    "ingredients:create"
)
def create_ingredient():
    ...
```

Только пользователи с permission `ingredients:create` смогут открыть данный маршрут.

---

# Создание администратора

Пример сидера:

```python
AdminSeeder().seed(
    "admin@mail.com"
)
```

Что делает:

1. Находит пользователя.
2. Назначает роль `admin`.
3. Сохраняет изменения.

---

# Добавление нового permission

Добавить в `PERMISSIONS`:

```python
PERMISSIONS["users:ban"] = (
    "Блокировка пользователей"
)
```

После этого выполнить:

```python
RBACSeeder().seed()
```

---

# Добавление новой роли

Добавить в `ROLES`:

```python
ROLES["moderator"] = {
    "description": "Модератор",
    "permissions": [
        "users:ban",
    ]
}
```

После этого выполнить:

```python
RBACSeeder().seed()
```

---

# Рекомендуемые роли для BeautyCycle

### user

Базовый пользователь.

Права:

* просмотр продуктов
* история сканирований

---

### ingredient_manager

Управление ингредиентами.

Права:

* ingredients:create
* ingredients:update

---

### content_manager

Управление статьями и контентом.

---

### moderator

Модерация пользователей.

Права:

* users:ban
* users:update

---

### admin

Полный доступ к системе.

---

# Рекомендации

Используйте permissions вместо проверки ролей.

Хорошо:

```python
@permission_required(
    "ingredients:update"
)
```

Плохо:

```python
if current_user.has_role("admin"):
```

Причина:

* роли могут меняться;
* permissions остаются стабильными;
* код становится более гибким;
* проще расширять систему.

```
```
