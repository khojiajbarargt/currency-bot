from groq import AsyncGroq
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)
router = Router()
chat_histories = {}

@router.message(Command("ai"))
async def cmd_ai_help(message: Message):
    await message.answer(
        "AI-ассистент готов!\n\n"
        "Напиши любой вопрос — отвечу.\n"
        "/clear — очистить историю."
    )

@router.message(Command("clear"))
async def cmd_clear(message: Message):
    chat_histories.pop(message.from_user.id, None)
    await message.answer("История очищена!")

@router.message()
async def handle_ai(message: Message):
    user_id = message.from_user.id
    user_text = message.text or ""

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_histories[user_id].append({
        "role": "user",
        "content": user_text
    })

    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_histories[user_id],
            max_tokens=1024,
        )
        reply = response.choices[0].message.content

        chat_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await message.answer(reply)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")