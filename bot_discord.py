# import os
# import discord
# import google.generativeai as genai
# from dotenv import load_dotenv

# # --- KONFIGURASI ---
# load_dotenv()
# DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# # Konfigurasi Gemini
# genai.configure(api_key=GEMINI_API_KEY)

# # Menggunakan model "gemini-1.5-flash" (Cepat & Gratis)
# # Bisa diganti "gemini-1.5-pro" jika ingin jawaban lebih mendalam
# model = genai.GenerativeModel('models/gemini-flash-latest')

# # Konfigurasi Discord
# intents = discord.Intents.default()
# intents.message_content = True # Wajib aktif
# client = discord.Client(intents=intents)

# # --- FUNGSI PEMECAH PESAN ---
# # Discord punya limit 2000 karakter per pesan.
# # Fungsi ini memecah jawaban panjang menjadi beberapa bagian.
# async def send_long_message(channel, text):
#     if len(text) <= 2000:
#         await channel.send(text)
#     else:
#         # Pecah teks per 1900 karakter (biar aman)
#         chunks = [text[i:i+1900] for i in range(0, len(text), 1900)]
#         for chunk in chunks:
#             await channel.send(chunk)

# # --- EVENT BOT ---
# @client.event
# async def on_ready():
#     print(f'✅ Bot online sebagai: {client.user}')
#     print('Siap menerima perintah !gemini')

# @client.event
# async def on_message(message):
#     # Abaikan pesan dari bot sendiri
#     if message.author == client.user:
#         return

#     # Trigger: Pesan harus diawali "!gemini"
#     if message.content.lower().startswith('!gemini'):
#         user_input = message.content[7:].strip() # Ambil teks setelah command

#         if not user_input:
#             await message.channel.send("Mau tanya apa? Ketik: `!gemini [pertanyaan]`")
#             return

#         # Indikator "Bot is typing..."
#         async with message.channel.typing():
#             try:
#                 # Kirim ke Google Gemini
#                 response = model.generate_content(user_input)

#                 # Ambil teks jawaban
#                 ai_text = response.text

#                 # Kirim balik ke Discord (pakai fungsi pemecah pesan)
#                 await send_long_message(message.channel, ai_text)

#             except Exception as e:
#                 # Tangani error (misal konten tidak aman atau server down)
#                 error_msg = f"⚠️ Maaf, terjadi kesalahan: {str(e)}"
#                 await message.channel.send(error_msg)
#                 print(error_msg)

# # Jalankan Bot
# client.run(DISCORD_TOKEN)

import os
import discord
from openai import OpenAI  # DeepSeek menggunakan library OpenAI
from dotenv import load_dotenv

# --- KONFIGURASI ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Inisialisasi Client DeepSeek
# Base URL wajib diarahkan ke server DeepSeek
client_ai = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Konfigurasi Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# --- FUNGSI PEMECAH PESAN ---
async def send_long_message(channel, text):
    if len(text) <= 2000:
        await channel.send(text)
    else:
        chunks = [text[i : i + 1900] for i in range(0, len(text), 1900)]
        for chunk in chunks:
            await channel.send(chunk)


# --- EVENT BOT ---
@client.event
async def on_ready():
    print(f"✅ Bot DeepSeek online sebagai: {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith("!ask"):  # Saya ubah trigger ke !ask
        user_input = message.content[4:].strip()

        if not user_input:
            await message.channel.send(
                "Mau tanya apa ke DeepSeek? Ketik: `!ask [pertanyaan]`"
            )
            return

        async with message.channel.typing():
            try:
                # Panggilan API ke DeepSeek
                response = client_ai.chat.completions.create(
                    model="deepseek-chat",  # Gunakan deepseek-reasoner jika ingin fitur thinking
                    messages=[
                        {
                            "role": "system",
                            "content": "Kamu adalah asisten AI yang cerdas dan membantu.",
                        },
                        {"role": "user", "content": user_input},
                    ],
                    stream=False,
                )

                ai_text = response.choices[0].message.content
                await send_long_message(message.channel, ai_text)

            except Exception as e:
                error_msg = f"⚠️ DeepSeek Error: {str(e)}"
                await message.channel.send(error_msg)
                print(error_msg)


client.run(DISCORD_TOKEN)
