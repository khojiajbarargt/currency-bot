import asyncio
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.rates import rates_service

router = Router()
user_alerts = {}

@router.message(Command("alert"))
async def cmd_alert(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 3:
        await message.answer(
            "Формат: /alert 90 EUR\n"
            "Бот уведомит когда 1 USD будет стоить меньше этой суммы в EUR"
        )
        return

    try:
        target = float(parts[1])
        currency = parts[2].upper()
    except ValueError:
        await message.answer("Неверный формат. Пример: /alert 90 EUR")
        return

    rates = await rates_service.get_rates()
    if currency not in rates:
        await message.answer(f"Валюта {currency} не найдена.")
        return

    user_id = message.from_user.id
    if user_id not in user_alerts:
        user_alerts[user_id] = []

    user_alerts[user_id].append({
        "currency": currency,
        "target": target,
        "chat_id": message.chat.id
    })

    current = rates.get(currency, 0)
    await message.answer(
        f"Алерт установлен!\n\n"
        f"Валюта: {currency}\n"
        f"Целевой курс: {target}\n"
        f"Текущий курс: {current:.2f}\n\n"
        f"Уведомлю когда 1 USD = {target} {currency}"
    )

@router.message(Command("myalerts"))
async def cmd_myalerts(message: Message):
    user_id = message.from_user.id
    alerts = user_alerts.get(user_id, [])
    if not alerts:
        await message.answer("У тебя нет активных алертов.\nДобавь: /alert 90 EUR")
        return
    lines = ["Твои алерты:\n"]
    for a in alerts:
        lines.append(f"1 USD = {a['target']} {a['currency']}")
    await message.answer("\n".join(lines))

async def check_alerts(bot):
    while True:
        await asyncio.sleep(60)
        if not user_alerts:
            continue
        rates = await rates_service.get_rates()
        for user_id, alerts in list(user_alerts.items()):
            for alert in list(alerts):
                currency = alert["currency"]
                target = alert["target"]
                current = rates.get(currency, 0)
                if current <= target:
                    await bot.send_message(
                        alert["chat_id"],
                        f"Алерт сработал!\n\n"
                        f"1 USD = {current:.2f} {currency}\n"
                        f"Достигнут твой целевой курс: {target}"
                    )
                    alerts.remove(alert)