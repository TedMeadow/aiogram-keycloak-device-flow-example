import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import jwt  # For decoding the JWT (ensure proper validation in production)
from dotenv import load_dotenv
import os
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# In-memory storage for device authorization data keyed by chat ID
device_auth_data = {}

@dp.message(Command("start"))
async def start_auth(message: types.Message):
    """Initiate Keycloak Device Authorization on /start command."""
    async with aiohttp.ClientSession() as session:
        device_auth_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/auth/device"
        data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
        async with session.post(device_auth_url, data=data) as resp:
            device_data = await resp.json()

    user_code = device_data.get("user_code")
    verification_uri_complete = device_data.get("verification_uri_complete")
    expires_in = device_data.get("expires_in", 600)

    # Save the device data associated with this Telegram chat
    device_auth_data[message.chat.id] = device_data

    # Create an inline button for manual authentication check
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "I've completed authentication", callback_data="check_auth")]
    ])

    await message.answer(
        f"To use this bot, please authenticate first:\n"
        f"1. Visit: {verification_uri_complete}\n"
        f"2. Enter the user code: {user_code}\n"
        f"Note: This code expires in {expires_in} seconds.",
        reply_markup=markup
    )

@dp.callback_query(lambda c: c.data == "check_auth")
async def check_auth(callback: types.CallbackQuery):
    """Check if the user has completed authentication when the button is pressed."""
    chat_id = callback.message.chat.id
    print(device_auth_data)
    if chat_id not in device_auth_data:
        await bot.answer_callback_query(callback.id, text="No pending authentication. Please /start again.")
        return

    device_data = device_auth_data[chat_id]
    device_code = device_data.get("device_code")
    token_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": CLIENT_ID,
        "device_code": device_code,
        "client_secret": CLIENT_SECRET
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, data=data) as resp:
            token_response = await resp.json()
    print(token_response)
    if "access_token" in token_response:
        access_token = token_response["access_token"]

        # Decode the token to extract Keycloak user information (in production, verify signature)
        keycloak_user = jwt.decode(access_token, options={"verify_signature": False})
        print(keycloak_user)
        user_id = keycloak_user.get("sub")  # Unique identifier for the Keycloak user
        username = keycloak_user.get('preferred_username')

        await bot.send_message(chat_id, f"Authentication successful! Keycloak user ID: {username}")
        # Optionally, map and store the association between Telegram user and Keycloak user here.
        device_auth_data.pop(chat_id, None)  # Clear the temporary device data

    elif token_response.get("error") == "authorization_pending":
        await bot.answer_callback_query(callback.id, text="Authentication not complete yet. Please try again later.", show_alert=True)
    else:
        error_desc = token_response.get("error_description", token_response.get("error"))
        await bot.send_message(chat_id, f"Authentication error: {error_desc}")
        device_auth_data.pop(chat_id, None)  # Clear data if error is terminal

    # Acknowledge the callback query to remove the loading state in the client UI
    await bot.answer_callback_query(callback.id)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
