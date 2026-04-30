# import secrets
#
# # Генерирует 32 случайных байта и переводит в hex (64 символа)
# token = secrets.token_hex(32)
# print(token)

# import os
#
# for root, dirs, files in os.walk('.'):
#     for name in dirs:
#         print(os.path.join(root, name))


d1 = {"username": None}
d2 = {"username": 123}
d3 = {"username": []}
d4 = {"username": "ab"}
d5 = {"username": "   "}
d6 = {"email": None}
d7 = {"email": 123}
d8 = {"password": None}
print(isinstance(d1["username"], str))
