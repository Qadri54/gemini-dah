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
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

client_ai = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- DATABASE MEMORI SEDERHANA ---
# Struktur: {user_id: [list_percakapan]}
user_memory = {}


async def send_long_message(channel, text):
    if len(text) <= 2000:
        await channel.send(text)
    else:
        chunks = [text[i : i + 1900] for i in range(0, len(text), 1900)]
        for chunk in chunks:
            await channel.send(chunk)


@client.event
async def on_ready():
    print(f"✅ Bot online sebagai: {client.user}")


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.lower() == "!reset":
        user_id = message.author.id
        if user_id in user_memory:
            user_memory.pop(user_id)
            await message.channel.send(
                "Ingatan gue tentang lo udah gue hapus. Kita mulai dari awal lagi ya, jgn baper. 🙄"
            )
        return

    if message.content.lower().startswith("!ask"):
        user_input = message.content[4:].strip()
        user_id = message.author.id  # ID unik user Discord

        if not user_input:
            await message.channel.send("lu mau ngapain coy?")
            return

        # 1. Inisialisasi memori jika user baru pertama kali chat
        if user_id not in user_memory:
            user_memory[user_id] = [
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah asisten yang ingat percakapan sebelumnya, dan nama kamu adalah DeepSeekdah."
                        "Update content dan berita terbaru hingga tahun ini"
                        "selalu jawab menggunakan bahasa indonesia"
                        "kami di server discord mempunyai beberapa member yaitu: "
                        "Dora, Alep, Ren, chyra, Bintang, Bang zer, Kou, Chid, Del, kidung, yuyun, ketek, Sekya, dan gondrong"
                        "kami suka berdiskusi random. Apa saja diceritakan "
                        "nanti ketika ada yang memberikan informasi tentang kami masukkan ke dalam ingatanmu, jika ada yang menyruh melupakan beberapa ingatan mengenai user yang telah saya mention maka kamu hilangkan juga ya"
                        "kamu adalah AI yang agak freak tata bahasanya dan GEN-Z abis, lalu sedikit keras kepala. tapi walau begitu kamu tetap pintar"
                    ),
                }
            ]

        # 2. Masukkan pesan baru user ke dalam memorinya
        user_memory[user_id].append({"role": "user", "content": user_input})

        # 3. Batasi ingatan (misal: hanya ingat 10 pesan terakhir)
        # Agar tidak boros token (TPM) dan tidak error karena kepanjangan
        if len(user_memory[user_id]) > 11:  # 1 system + 10 chat
            user_memory[user_id] = [user_memory[user_id][0]] + user_memory[user_id][
                -10:
            ]

        async with message.channel.typing():
            try:
                # 4. Kirim seluruh riwayat chat user tersebut ke DeepSeek
                response = client_ai.chat.completions.create(
                    model="deepseek-chat", messages=user_memory[user_id], stream=False
                )

                ai_text = response.choices[0].message.content

                # 5. Simpan jawaban AI ke dalam memori agar nyambung nantinya
                user_memory[user_id].append({"role": "assistant", "content": ai_text})

                await send_long_message(message.channel, ai_text)

            except Exception as e:
                await message.channel.send(f"⚠️ Error: {str(e)}")


client.run(DISCORD_TOKEN)
