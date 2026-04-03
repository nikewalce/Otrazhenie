# """
# Telegram bot for Otrazhenie MVP
# Features implemented:
# - /start, /help
# - /register (simple user creation)
# - /analyze (user sends product composition text for analysis)
# - /addproduct (save product to user's DB)
# - /favorites (list user's favorites)
# - /history (list user's analyses)
#
# Tech: aiogram, SQLAlchemy (SQLite for MVP), pandas for CSV loading
#
# Requirements:
# aiogram==3.*
# SQLAlchemy
# pandas
# python-dotenv
#
# Set environment variable BOT_TOKEN or create a .env with BOT_TOKEN=...
#
# Place CSV ingredient database at ./db/csv_files/inci_data.csv with columns: name,function,safety_score,description,allergen_flag
# """
#
# import asyncio
# import os
# from datetime import datetime
#
# import pandas as pd
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Command
# from aiogram.types import FSInputFile, Message
# from aiogram.utils.keyboard import ReplyKeyboardBuilder
# from dotenv import load_dotenv
#
# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# if not BOT_TOKEN:
#     raise RuntimeError("Please set BOT_TOKEN environment variable")
#
# # --- Bot setup ---
# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()
#
# # keyboards
# kb = ReplyKeyboardBuilder()
# kb.button(text="/analyze")
# kb.button(text="/addproduct")
# kb.button(text="/favorites")
# kb.button(text="/history")
# kb.button(text="/help")
# kb = kb.as_markup(resize_keyboard=True)
#
#
# @dp.message(Command("start"))
# async def cmd_start(msg: Message):
#     text = (
#         "Привет! Я бот Otrazhenie — анализатор косметики.\n"
#         "Отправьте /analyze и вставьте состав продукта (через запятую).\n"
#         "Используйте /addproduct чтобы сохранить продукт в свою бьюти-базу."
#     )
#     await msg.answer(text, reply_markup=kb)
#
#
# @dp.message(Command("help"))
# async def cmd_help(msg: Message):
#     text = (
#         "/analyze — проанализировать состав (после команды вставьте состав через запятую)\n"
#         "/addproduct — добавить продукт в базу (формат: имя | бренд | состав)\n"
#         "/favorites — список избранных\n"
#         "/history — история ваших анализов\n"
#         "/register — зарегистрироваться (email | skin_type | goals | allergies)"
#     )
#     await msg.answer(text)
#
#
# @dp.message(Command("register"))
# async def cmd_register(msg: Message):
#     payload = msg.text.partition(" ")[2].strip()
#     if not payload:
#         await msg.answer(
#             "Чтобы зарегистрироваться отправьте: /register email | skin_type | goals | allergies\nПример: /register test@example.com | dry | увлажнение | нет"
#         )
#         return
#     parts = [p.strip() for p in payload.split("|")]
#     email = parts[0] if len(parts) > 0 else None
#     skin_type = parts[1] if len(parts) > 1 else None
#     goals = parts[2] if len(parts) > 2 else None
#     allergies = parts[3] if len(parts) > 3 else None
#     with SessionLocal() as s:
#         user = s.query(User).filter_by(tg_id=msg.from_user.id).first()
#         if not user:
#             user = User(
#                 tg_id=msg.from_user.id,
#                 email=email,
#                 skin_type=skin_type,
#                 goals=goals,
#                 allergies=allergies,
#             )
#             s.add(user)
#             s.commit()
#             await msg.answer("Регистрация завершена ✅")
#         else:
#             user.email = email or user.email
#             user.skin_type = skin_type or user.skin_type
#             user.goals = goals or user.goals
#             user.allergies = allergies or user.allergies
#             s.commit()
#             await msg.answer("Данные обновлены ✅")
#
#
# # Analyze: the user sends command '/analyze' followed by composition in the same message or next message
# user_pending_analyze = {}  # tg_id -> True
#
#
# @dp.message(Command("analyze"))
# async def cmd_analyze(msg: Message):
#     payload = msg.text.partition(" ")[2].strip()
#     if payload:
#         await perform_analysis(msg, payload)
#         return
#     # ask user to send composition
#     user_pending_analyze[msg.from_user.id] = True
#     await msg.answer(
#         "Отправьте состав продукта текстом (через запятую), например: Water, Glycerin, Parfum..."
#     )
#
#
# @dp.message()
# async def catch_all(msg: Message):
#     uid = msg.from_user.id
#     if user_pending_analyze.get(uid):
#         payload = msg.text.strip()
#         user_pending_analyze.pop(uid, None)
#         await perform_analysis(msg, payload)
#         return
#     # fallback
#     await msg.answer("Не понял. Используйте /help для списка команд.", reply_markup=kb)
#
#
# async def perform_analysis(msg: Message, composition_text: str):
#     parts = parse_composition(composition_text)
#     with SessionLocal() as s:
#         analysis = analyze_ingredients(s, parts)
#         score = compute_product_score(analysis)
#         lines = [f"Общий рейтинг: {score}\n"]
#         for a in analysis:
#             if a.found:
#                 allerg = " (аллерген)" if a.allergen else ""
#                 lines.append(
#                     f"{a.name} — {a.function or 'неизвестно'} — {a.safety}{allerg}"
#                 )
#             else:
#                 lines.append(f"{a.name} — ❓ Не найдено в базе")
#         text = "\n".join(lines)
#         await msg.answer(text)
#         # save product as temporary entry in products and user_products.history
#         prod = Product(
#             name=f"Анализ {datetime.utcnow().isoformat()[:19]}",
#             composition_raw=composition_text,
#         )
#         s.add(prod)
#         s.commit()
#         # attach to user if exists
#         user = s.query(User).filter_by(tg_id=msg.from_user.id).first()
#         if user:
#             up = UserProduct(user_id=user.id, product_id=prod.id, custom_name=prod.name)
#             s.add(up)
#             s.commit()
#
#
# @dp.message(Command("addproduct"))
# async def cmd_addproduct(msg: Message):
#     payload = msg.text.partition(" ")[2].strip()
#     if not payload:
#         await msg.answer(
#             "Чтобы добавить продукт: /addproduct Название | Бренд | состав (через запятую)"
#         )
#         return
#     parts = [p.strip() for p in payload.split("|")]
#     if len(parts) < 3:
#         await msg.answer(
#             "Неверный формат. Пример: /addproduct MyCream | BrandX | Water, Glycerin, ..."
#         )
#         return
#     name, brand, composition = parts[0], parts[1], parts[2]
#     with SessionLocal() as s:
#         prod = Product(name=name, brand=brand, composition_raw=composition)
#         s.add(prod)
#         s.commit()
#         user = s.query(User).filter_by(tg_id=msg.from_user.id).first()
#         if user:
#             up = UserProduct(user_id=user.id, product_id=prod.id, custom_name=name)
#             s.add(up)
#             s.commit()
#         await msg.answer(f'Продукт "{name}" добавлен в базу ✅')
#
#
# @dp.message(Command("favorites"))
# async def cmd_favorites(msg: Message):
#     with SessionLocal() as s:
#         user = s.query(User).filter_by(tg_id=msg.from_user.id).first()
#         if not user:
#             await msg.answer("Вы не зарегистрированы. Используйте /register")
#             return
#         ups = s.query(UserProduct).filter_by(user_id=user.id, favorite=True).all()
#         if not ups:
#             await msg.answer("У вас нет избранных продуктов")
#             return
#         texts = []
#         for up in ups:
#             p = s.query(Product).filter_by(id=up.product_id).first()
#             texts.append(
#                 f"{up.custom_name or p.name} — добавлен {up.date_added.date()}"
#             )
#         await msg.answer("\n".join(texts))
#
#
# @dp.message(Command("history"))
# async def cmd_history(msg: Message):
#     with SessionLocal() as s:
#         user = s.query(User).filter_by(tg_id=msg.from_user.id).first()
#         if not user:
#             await msg.answer("Вы не зарегистрированы. Используйте /register")
#             return
#         ups = (
#             s.query(UserProduct)
#             .filter_by(user_id=user.id)
#             .order_by(UserProduct.date_added.desc())
#             .limit(50)
#             .all()
#         )
#         if not ups:
#             await msg.answer("История пустая")
#             return
#         out = []
#         for up in ups:
#             p = s.query(Product).filter_by(id=up.product_id).first()
#             out.append(
#                 f'{up.custom_name or p.name} — {up.date_added.strftime("%Y-%m-%d %H:%M")}'
#             )
#         await msg.answer("\n".join(out))
#
#
# # Run
# async def main():
#     try:
#         print("Starting bot...")
#         await dp.start_polling(bot)
#     finally:
#         await bot.session.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
