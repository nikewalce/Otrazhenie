import secrets

# Генерирует 32 случайных байта и переводит в hex (64 символа)
token = secrets.token_hex(32)
print(token)
