import re
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.rates import rates_service
from db import save_conversion, get_history

router = Router()
TARGETS = ["USD", "EUR", "RUB", "UZS", "GBP"]

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я конвертер валют с AI.\n\n"
        "Напиши сумму и валюту, например:\n"
        "  100 USD\n"
        "  50 EUR\n\n"
        "Или /help — все команды."
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Курсы валют", callback_data="show_rates"),
            InlineKeyboardButton(text="История", callback_data="show_history"),
        ],
        [
            InlineKeyboardButton(text="Алерты", callback_data="show_alerts"),
            InlineKeyboardButton(text="AI ассистент", callback_data="show_ai"),
        ],
    ])
    await message.answer(
        "Что умеет этот бот:\n\n"
        "Конвертация валют\n"
        "  Напиши: 100 USD или 50 EUR\n\n"
        "Команды:\n"
        "  /rates — текущие курсы\n"
        "  /history — история конвертаций\n"
        "  /alert 90 EUR — алерт на курс\n"
        "  /clear — очистить AI чат",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "show_rates")
async def cb_rates(callback: CallbackQuery):
    rates = await rates_service.get_rates()
    lines = ["Курсы к USD:\n"]
    for cur in TARGETS:
        if cur != "USD" and cur in rates:
            lines.append(f"1 USD = {rates[cur]:,.2f} {cur}")
    await callback.message.answer("\n".join(lines))
    await callback.answer()

@router.callback_query(lambda c: c.data == "show_history")
async def cb_history(callback: CallbackQuery):
    rows = get_history(callback.from_user.id)
    if not rows:
        await callback.message.answer("История пуста — сконвертируй что-нибудь!")
    else:
        lines = ["Последние конвертации:\n"]
        for amount, from_cur, result, to_cur, date in rows:
            lines.append(f"{amount:,} {from_cur} = {result:,} {to_cur}  ({date})")
        await callback.message.answer("\n".join(lines))
    await callback.answer()

@router.callback_query(lambda c: c.data == "show_alerts")
async def cb_alerts(callback: CallbackQuery):
    await callback.message.answer("Алерты: используй /alert 90 EUR")
    await callback.answer()

@router.callback_query(lambda c: c.data == "show_ai")
async def cb_ai(callback: CallbackQuery):
    await callback.message.answer("Просто напиши любой вопрос!")
    await callback.answer()

@router.message(Command("rates"))
async def cmd_rates(message: Message):
    rates = await rates_service.get_rates()
    lines = ["Курсы к USD:\n"]
    for cur in TARGETS:
        if cur != "USD" and cur in rates:
            lines.append(f"1 USD = {rates[cur]:,.2f} {cur}")
    await message.answer("\n".join(lines))

@router.message(Command("history"))
async def cmd_history(message: Message):
    rows = get_history(message.from_user.id)
    if not rows:
        await message.answer("История пуста — сконвертируй что-нибудь!")
    else:
        lines = ["Последние конвертации:\n"]
        for amount, from_cur, result, to_cur, date in rows:
            lines.append(f"{amount:,} {from_cur} = {result:,} {to_cur}  ({date})")
        await message.answer("\n".join(lines))

@router.message(lambda msg: bool(re.match(r'^\d+\.?\d*\s+[A-Za-z]{3}', msg.text or '')))
async def handle_convert(message: Message):
    parts = message.text.strip().split()
    amount = float(parts[0])
    from_cur = parts[1].upper()

    rates = await rates_service.get_rates()
    if from_cur not in rates:
        await message.answer(f"Валюта {from_cur} не найдена.")
        return

    lines = [f"{amount:,} {from_cur} =\n"]
    for cur in TARGETS:
        if cur != from_cur:
            result = await rates_service.convert(amount, from_cur, cur)
            if result is not None:
                save_conversion(message.from_user.id, amount, from_cur, result, cur)
                lines.append(f"  {result:,} {cur}")

    await message.answer("\n".join(lines))