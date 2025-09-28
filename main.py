import telebot
import random
from telebot import types
import requests
import sqlite3
import threading
import time
from datetime import datetime
from bs4 import BeautifulSoup
import asyncio
from aiogram import Bot



bot = telebot.TeleBot('') #твой токен здесь


conn = sqlite3.connect('weather_forecast.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS forecast (
    date TEXT PRIMARY KEY,
    today_temp INTEGER,
    tomorrow_temp INTEGER
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER PRIMARY KEY
)
''')
conn.commit()



def save_forecast(date, today, tomorrow):
    cursor.execute('REPLACE INTO forecast (date, today_temp, tomorrow_temp) VALUES (?, ?, ?)', (date, today, tomorrow))
    conn.commit()

def get_eco_news():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        news_url = "https://ria.ru/ecology/"  
        r = requests.get(news_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        news_elements = soup.select('a.list-item__title.color-font-hover-only')[:5]

        news_list = []
        for item in news_elements:
            title = item.get_text(strip=True)
            link = item['href']
            news_list.append(f"📰 {title}\n🔗 {link}")

        return "\n\n".join(news_list) if news_list else "Новости не найдены."
    except Exception as e:
        print("Ошибка при парсинге новостей:", e)
        return "Ошибка при загрузке новостей."

def get_potep_news():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        news_url = "https://ria.ru/keyword_globalnoe_poteplenie/"  
        r = requests.get(news_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        news_elements = soup.select('a.list-item__title.color-font-hover-only')[:5]

        news_list = []
        for item in news_elements:
            title = item.get_text(strip=True)
            link = item['href']
            news_list.append(f"📰 {title}\n🔗 {link}")

        return "\n\n".join(news_list) if news_list else "Новости не найдены."
    except Exception as e:
        print("Ошибка при парсинге новостей:", e)
        return "Ошибка при загрузке новостей."


def global_warming_info():
    return ("🌍 Что такое глобальное потепление?\n"
            "Глобальное потепление — это увеличение средней температуры Земли из-за парниковых газов.\n\n"
            "🌡 Причины:\n"
            "1. Сжигание топлива\n2. Вырубка лесов\n3. Индустриализация\n\n"
            "🌿 Как помочь:\n"
            "1. Снизьте выбросы\n2. Используйте зелёную энергию\n3. Экономьте ресурсы\n4. Поддерживайте природу.")



@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Глобальное потепление")
    markup.add("Полезные советы", "Углеродный след", "Эко-новости", 'Новости Глобального потепления')

    bot.send_message(message.chat.id, f"Привет! Я бот про погоду и климат. Выбери действие 👇", reply_markup=markup)


def daily_forecast_job():
    while True:
        now = datetime.now()
        if now.hour == 8:
        
                
            time.sleep(3600)
        else:
            time.sleep(300)

threading.Thread(target=daily_forecast_job, daemon=True).start()

# Углеродный след
user_carbon_progress = {}

@bot.message_handler(func=lambda message: message.text == "Углеродный след")
def carbon_start(message):
    user_carbon_progress[message.chat.id] = {"step": 1, "score": 0}
    bot.send_message(message.chat.id, "🚗 Вопрос 1: Как часто используете личный транспорт?\n1. Каждый день\n2. Иногда\n3. Никогда")

@bot.message_handler(func=lambda message: message.chat.id in user_carbon_progress)
def carbon_calc(message):
    state = user_carbon_progress[message.chat.id]
    step = state["step"]
    text = message.text.strip()
    if step == 1:
        state["score"] += {"1": 3, "2": 2, "3": 0}.get(text, 0)
        state["step"] = 2
        bot.send_message(message.chat.id, "💡 Вопрос 2: Вы выключаете свет, уходя из комнаты?\n1. Всегда\n2. Иногда\n3. Никогда")
    elif step == 2:
        state["score"] += {"1": 0, "2": 1, "3": 2}.get(text, 0)
        state["step"] = 3
        bot.send_message(message.chat.id, "🍽 Вопрос 3: Как часто вы едите мясо?\n1. Каждый день\n2. Иногда\n3. Редко или никогда")
    elif step == 3:
        state["score"] += {"1": 3, "2": 2, "3": 0}.get(text, 0)
        total = state["score"]
        del user_carbon_progress[message.chat.id]
        if total <= 3:
            msg = "🟢 Ваш углеродный след низкий — вы молодец!"
        elif total <= 6:
            msg = "🟡 Средний след — можно улучшить."
        else:
            msg = "🔴 Высокий углеродный след — подумайте о переменах!"
        bot.send_message(message.chat.id, f"🌍 Ваш результат: {total} баллов\n{msg}")



@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Глобальное потепление":
        bot.send_message(message.chat.id, global_warming_info())
    elif message.text == "Полезные советы":
        bot.send_message(message.chat.id, "✅ Советы:\n1. Экономьте энергию⚡\n2. Общественный транспорт🚌\n3. Сортировка мусора♻️\n4. Меньше пластика🌍")
    elif message.text == "Эко-новости":
        news = get_eco_news()
        bot.send_message(message.chat.id, news)
    elif message.text == "Новости Глобального потепления":
        news = get_potep_news()
        bot.send_message(message.chat.id, news)

    else:
        bot.send_message(message.chat.id, "❓ Я не понял. Пожалуйста, выбери кнопку или команду.")


bot.polling()
