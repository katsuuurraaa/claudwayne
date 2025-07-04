import asyncio
import random
import time
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Настройки бота
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# База данных (в памяти)
users_db = {}

# Карточки
cards = {
    "common": [
        "Шляпник (Hage Village Elder)", "Ребекка Скарлет", "Кашон", 
        "Дрот", "Гордон Агриппа", "Эн", "Либон", "Руя", "Ниер", 
        "Джуджо", "Шалль", "Фраггил", "Буффал", "Лумиер", "Прад",
        "Сисси", "Джелс", "Ронне", "Холл", "Шукур"
    ],
    "uncommon": [
        "Гауче Адлай", "Лэнгрис Водьё", "Летолил Бейко", 
        "Сол Маррон", "Рилл Бойсвит", "Фезе Тайрелл", "Кифф", 
        "Барто", "Зора Идеале", "Грея", "Гаджи", "Маркс Франсуа",
        "Дэвид Свон", "Румо", "Хамон"
    ],
    "rare": [
        "Ноэль Сильва", "Финрал Рулкейси", "Леопольд Вермиллион", 
        "Мимоза Вермиллион", "Кирин", "Шарм Папиттсон", "Радес Спирито",
        "Валтос", "Фана", "Лето", "Сиф", "Гордон"
    ],
    "legendary": [
        "Ями Сукэхиро", "Шарлотта Розели", "Джек Ужасный", 
        "Вильям Вангеанс", "Дороти Ансворт", "Генри Легат",
        "Юлиус Новахроно", "Мерелеона Вермиллион"
    ],
    "limited": ["Аста", "Юно"]
}

# Шансы выпадения
drop_rates = {
    "common": 98.989,  # Увеличена вероятность
    "uncommon": 0.1,   # Уменьшена
    "rare": 0.01,       # Уменьшена
    "legendary": 0.0001, # Сильно уменьшена
    "limited": 0.000001   # Крайне редкие
}

# Достижения
achievements = {
    "limited_drop": "Получить лимитированную карту",
    "all_common": "Собрать все обычные карты",
    "all_rarities": "Получить карты всех редкостей",
    "three_legendary": "Получить 3 легендарные карты",
    "first_drop": "Получить первую карту"
}

# Обработчики команд
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {
            "cards": [], 
            "last_drop": 0, 
            "achievements": [],
            "first_drop": False
        }
        await message.answer(
            "🎴 Добро пожаловать в коллекционера карточек 'Чёрный Клевер'!\n\n"
            "Доступные команды:\n"
            "• карта - получить новую карту (раз в 3 часа)\n"
            "• профиль - посмотреть свой профиль\n"
            "• мои карты - список всех ваших карт\n"
            "• обычные - показать обычные карты\n"
            "• необычные - показать необычные карты\n"
            "• редкие - показать редкие карты\n"
            "• легендарные - показать легендарные карты\n"
            "• лимит - показать лимитированные карты\n"
            "• достижения - список ваших достижений"
        )
        # Даем первую карту сразу
        await give_random_card(user_id, message)
    else:
        await message.answer(
            "🎴 С возвращением в коллекционера карточек 'Чёрный Клевер'!\n\n"
            "Доступные команды:\n"
            "• карта - получить новую карту (раз в 3 часа)\n"
            "• профиль - посмотреть свой профиль\n"
            "• мои карты - список всех ваших карт\n"
            "• обычные - показать обычные карты\n"
            "• необычные - показать необычные карты\n"
            "• редкие - показать редкие карты\n"
            "• легендарные - показать легендарные карты\n"
            "• лимит - показать лимитированные карты\n"
            "• достижения - список ваших достижений"
        )

async def give_random_card(user_id, message):
    """Выдача случайной карты с учетом повторок"""
    user_data = users_db[user_id]
    
    # Выбор карты
    rarity = random.choices(
        list(drop_rates.keys()),
        weights=list(drop_rates.values()),
        k=1
    )[0]
    card = random.choice(cards[rarity])
    
    # Проверка на повтор
    is_duplicate = card in user_data["cards"]
    
    if not is_duplicate:
        user_data["cards"].append(card)
    
    user_data["last_drop"] = time.time()
    
    # Проверка достижений
    check_achievements(user_id)
    
    # Формирование сообщения
    message_text = ""
    if rarity == "limited":
        message_text = (
            f"🎉 <b>НЕВЕРОЯТНО! ЛИМИТИРОВАННАЯ КАРТА!</b> 🎉\n"
            f"🔥 <b>{card}</b> теперь в твоей коллекции!\n"
            f"⭐ Шанс: 0.001%!"
        )
    else:
        if is_duplicate:
            message_text = (
                f"🃏 Выпала повторная карта:\n"
                f"<b>{card}</b> ({rarity})\n"
                f"Эта карта уже есть в вашей коллекции!"
            )
        else:
            message_text = (
                f"🎴 Ты получил: <b>{card}</b> ({rarity})\n"
                "Теперь ты можешь получать новые карты раз в 3 часа!"
            )
    
    await message.answer(message_text, parse_mode="HTML")
    
    # Первая карта
    if not user_data["first_drop"] and not is_duplicate:
        user_data["first_drop"] = True
        user_data["achievements"].append("first_drop")
        await message.answer(
            "🎉 <b>Поздравляем с первой картой!</b>\n"
            "Ты получил достижение: <b>Получить первую карту</b>",
            parse_mode="HTML"
        )

@dp.message(lambda message: message.text.lower() == "профиль")
async def profile(message: types.Message):
    user_data = users_db.get(message.from_user.id, {"cards": [], "achievements": []})
    has_limited = any(card in cards["limited"] for card in user_data["cards"])
    
    text = (
        f"👤 <b>Профиль:</b> {message.from_user.full_name}\n"
        f"🎴 <b>Карточек:</b> {len(user_data['cards'])}\n"
        f"🏆 <b>Достижений:</b> {len(user_data['achievements'])}\n\n"
        "Используйте команды:\n"
        "• обычные - показать обычные карты\n"
        "• необычные - показать необычные карты\n"
        "• редкие - показать редкие карты\n"
        "• легендарные - показать легендарные карты\n"
        "• лимит - показать лимитированные карты\n"
        "• достижения - список ваших достижений"
    )
    
    if has_limited:
        text += "\n\n⭐ <b>У вас есть LIMITED карты!</b> ⭐"
    
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda message: message.text.lower() == "карта")
async def get_card(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.setdefault(user_id, {
        "cards": [], 
        "last_drop": 0, 
        "achievements": [],
        "first_drop": False
    })
    
    current_time = time.time()
    cooldown = 3 * 60 * 60  # 3 часа в секундах
    
    if current_time - user_data["last_drop"] < cooldown:
        remaining = cooldown - (current_time - user_data["last_drop"])
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await message.answer(f"⏳ Подожди еще {hours}ч {minutes}мин")
        return
    
    await give_random_card(user_id, message)

@dp.message(lambda message: message.text.lower() == "мои карты")
async def show_all_cards(message: types.Message):
    user_data = users_db.get(message.from_user.id, {"cards": []})
    
    if not user_data["cards"]:
        await message.answer("У тебя пока нет карточек!")
        return
    
    # Группируем карты по редкости
    cards_by_rarity = {rarity: [] for rarity in cards}
    for card in user_data["cards"]:
        for rarity in cards:
            if card in cards[rarity]:
                cards_by_rarity[rarity].append(card)
                break
    
    text = "📊 <b>Все ваши карты:</b>\n"
    for rarity, card_list in cards_by_rarity.items():
        if card_list:
            text += f"\n<b>{rarity.capitalize()} ({len(card_list)}):</b>\n"
            text += ", ".join(card_list) + "\n"
    
    await message.answer(text, parse_mode="HTML")

# Команды для просмотра карт по категориям
@dp.message(lambda message: message.text.lower() == "обычные")
async def show_common_cards(message: types.Message):
    await show_cards_by_rarity(message, "common")

@dp.message(lambda message: message.text.lower() == "необычные")
async def show_uncommon_cards(message: types.Message):
    await show_cards_by_rarity(message, "uncommon")

@dp.message(lambda message: message.text.lower() == "редкие")
async def show_rare_cards(message: types.Message):
    await show_cards_by_rarity(message, "rare")

@dp.message(lambda message: message.text.lower() == "легендарные")
async def show_legendary_cards(message: types.Message):
    await show_cards_by_rarity(message, "legendary")

@dp.message(lambda message: message.text.lower() == "лимит")
async def show_limited_cards(message: types.Message):
    await show_cards_by_rarity(message, "limited")

async def show_cards_by_rarity(message: types.Message, rarity: str):
    user_data = users_db.get(message.from_user.id, {"cards": []})
    user_cards = [card for card in user_data["cards"] if card in cards[rarity]]
    
    if not user_cards:
        await message.answer(f"У вас пока нет {rarity} карт!")
        return
    
    text = f"<b>Ваши {rarity} карты ({len(user_cards)}):</b>\n"
    text += "\n".join(f"• {card}" for card in user_cards)
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda message: message.text.lower() == "достижения")
async def show_achievements(message: types.Message):
    user_data = users_db.get(message.from_user.id, {"achievements": []})
    
    if not user_data["achievements"]:
        await message.answer("У тебя пока нет достижений!")
        return
    
    text = "🏆 <b>Твои достижения:</b>\n"
    for achievement in user_data["achievements"]:
        text += f"• {achievements[achievement]}\n"
    
    await message.answer(text, parse_mode="HTML")

def check_achievements(user_id):
    user_data = users_db[user_id]
    cards_list = user_data["cards"]
    
    conditions = {
        "limited_drop": any(card in cards["limited"] for card in cards_list),
        "all_common": all(card in cards_list for card in cards["common"]),
        "three_legendary": sum(1 for card in cards_list if card in cards["legendary"]) >= 3,
        "all_rarities": (
            any(card in cards["common"] for card in cards_list) and
            any(card in cards["uncommon"] for card in cards_list) and
            any(card in cards["rare"] for card in cards_list) and
            any(card in cards["legendary"] for card in cards_list) and
            any(card in cards["limited"] for card in cards_list)
        )
    }
    
    for achievement, condition in conditions.items():
        if condition and achievement not in user_data["achievements"]:
            user_data["achievements"].append(achievement)

# Админ-команды
ADMINS = [1909652995]  # Ваш ID телеграма

@dp.message(lambda message: message.from_user.id in ADMINS and message.text.lower() == "админ")
async def admin_panel(message: types.Message):
    await message.answer(
        "Панель администратора:\n"
        "• открыть карты [число] - открыть указанное количество карт\n"
        "• сбросить кд - сбросить кулдаун для получения карт"
    )

# ... (остальной код остается без изменений до админ-команд)

@dp.message(lambda message: message.from_user.id in ADMINS and message.text.lower().startswith("открыть карты"))
async def open_multiple_cards(message: types.Message):
    try:
        num = int(message.text.split()[-1])
        if num <= 0:
            await message.answer("Число должно быть больше 0!")
            return
            
        user_id = message.from_user.id
        user_data = users_db.setdefault(user_id, {"cards": [], "achievements": []})
        
        results = {
            "common": {"new": [], "duplicates": []},
            "uncommon": {"new": [], "duplicates": []},
            "rare": {"new": [], "duplicates": []},
            "legendary": {"new": [], "duplicates": []},
            "limited": {"new": [], "duplicates": []}
        }
        
        for _ in range(num):
            rarity = random.choices(
                list(drop_rates.keys()),
                weights=list(drop_rates.values()),
                k=1
            )[0]
            card = random.choice(cards[rarity])
            
            if card in user_data["cards"]:
                results[rarity]["duplicates"].append(card)
            else:
                results[rarity]["new"].append(card)
                user_data["cards"].append(card)
            
            check_achievements(user_id)
        
        # Формируем сообщение с результатами
        result_message = f"<b>Открыто {num} карт:</b>\n\n"
        total_new = 0
        total_duplicates = 0
        
        for rarity in results:
            new_count = len(results[rarity]["new"])
            dup_count = len(results[rarity]["duplicates"])
            
            if new_count + dup_count > 0:
                result_message += (
                    f"<b>{rarity.capitalize()}:</b>\n"
                    f"• Новые: {new_count}\n"
                    f"• Повторы: {dup_count}\n\n"
                )
            
            total_new += new_count
            total_duplicates += dup_count
        
        result_message += (
            f"<b>Итого:</b>\n"
            f"• Всего новых карт: {total_new}\n"
            f"• Всего повторок: {total_duplicates}\n"
            f"• Всего карт в коллекции: {len(user_data['cards'])}"
        )
        
        await message.answer(result_message, parse_mode="HTML")
        
    except (ValueError, IndexError):
        await message.answer("Используйте: 'открыть карты [число]'")

# ... (остальной код остается без изменений)

@dp.message(lambda message: message.from_user.id in ADMINS and message.text.lower() == "сбросить кд")
async def reset_cooldown(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_db:
        users_db[user_id]["last_drop"] = 0
    await message.answer("Кулдаун сброшен!")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())