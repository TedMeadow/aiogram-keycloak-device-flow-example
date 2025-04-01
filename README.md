# 🤖 Keycloak Device Authorization with Aiogram (Telegram Bot Example)

This project demonstrates how to integrate **Keycloak OAuth2 Device Flow** into a Telegram bot using **Aiogram 3.x** and **aiohttp**.

> 🔐 Device Authorization Flow is perfect for bots or IoT devices where users can't enter credentials directly in the app.

---

## ✨ Features

- ✅ Uses [Keycloak](https://www.keycloak.org/) for user authentication
- ✅ Device Authorization Flow (RFC 8628)
- ✅ JWT decoding to extract user identity
- ✅ Works with Telegram via Aiogram
- ✅ Stateless session (in-memory for demo)

---

## 🚀 Getting Started

### 1. Setup Keycloak

Make sure you have:

- Public Keycloak instance
- Realm
- Client with:
  - `client_id`, `client_secret`
  - `Service Account Enabled`
  - `OAuth2 Device Flow` enabled

### 2. Clone and Configure

```bash
git clone https://github.com/TedMeadow/aiogram-keycloak-device-flow-example.git
cd aiogram-keycloak-device-flow-example
cp .env.example .env
```

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Run the Bot

python bot.py
