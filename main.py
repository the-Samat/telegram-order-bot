import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from anthropic import Anthropic
import json
import re

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')

# Инициализация Claude
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)

# Инициализация Google Sheets
def init_google_sheets():
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        return sheet
    except Exception as e:
        logger.error(f"Ошибка подключения к Google Sheets: {e}")
        return None

# Функция для извлечения данных заказа с помощью Claude
def extract_order_data(message_text):
    try:
        prompt = f"""Проанализируй это сообщение о заказе и извлеки данные в формате JSON.

Сообщение:
{message_text}

Извлеки следующие поля (если поле отсутствует, используй пустую строку ""):
- Продавец (менеджер который принял заказ)
- Товар
- Номер (телефон клиента)
- Адрес
- Выкуп (сумма выкупа)
- Предоплата
- Доставка

Верни ТОЛЬКО JSON в таком формате (без дополнительного текста):
{{
    "продавец": "",
    "товар": "",
    "номер": "",
    "адрес": "",
    "выкуп": "",
    "предоплата": "",
    "доставка": ""
}}"""

        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Убираем markdown форматирование если есть
        response_text = re.sub(r'```json\s*|\s*```', '', response_text)
        
        # Парсим JSON
        order_data = json.loads(response_text)
        return order_data
        
    except Exception as e:
        logger.error(f"Ошибка извлечения данных: {e}")
        return None

# Функция для записи в Google Sheets
def write_to_sheet(sheet, order_data):
    try:
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        row = [
            current_time,  # Дата и время
            order_data.get('продавец', ''),
            order_data.get('товар', ''),
            order_data.get('номер', ''),
            order_data.get('адрес', ''),
            order_data.get('выкуп', ''),
            order_data.get('предоплата', ''),
            order_data.get('доставка', ''),
            'Заказ принят'  # Статус по умолчанию
        ]
        
        sheet.append_row(row)
        return True
    except Exception as e:
        logger.error(f"Ошибка записи в таблицу: {e}")
        return False

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """👋 Добро пожаловать в систему учета заказов!

Просто отправьте мне сообщение с заказом в формате:

*Заказ*
• Продавец: Имя
• Товар: Название товара
• Номер: +996 XXX XXX XXX
• Адрес: Адрес доставки
• Выкуп: Сумма
• Предоплата: Сумма
• Доставка: Сумма

Бот автоматически:
✅ Добавит дату и время
✅ Поставит статус "Заказ принят"
✅ Запишет в Google Таблицу

Команды:
/start - это сообщение
/help - помощь"""
    
    await update.message.reply_text(welcome_message)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📋 Помощь по использованию бота:

1️⃣ Отправьте заказ в любом формате
2️⃣ Бот обработает и запишет в таблицу
3️⃣ Получите подтверждение

Пример заказа:
*Заказ*
• Продавец: Наргиз
• Товар: Подарочный бокс
• Номер: +996 502 995 421
• Адрес: ул.Тирек 36
• Выкуп: 1590
• Предоплата: 500
• Доставка: 200

Бот понимает разные варианты написания! 🤖"""
    
    await update.message.reply_text(help_text)

# Обработчик сообщений с заказами
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    
    # Проверяем что сообщение похоже на заказ
    if 'заказ' not in message_text.lower():
        await update.message.reply_text(
            "⚠️ Отправьте сообщение с заказом (должно содержать слово 'Заказ')\n\n"
            "Используйте /help для примера"
        )
        return
    
    # Отправляем сообщение о начале обработки
    processing_msg = await update.message.reply_text("⏳ Обрабатываю заказ...")
    
    try:
        # Извлекаем данные заказа с помощью Claude
        order_data = extract_order_data(message_text)
        
        if not order_data:
            await processing_msg.edit_text("❌ Ошибка обработки заказа. Попробуйте еще раз.")
            return
        
        # Инициализируем Google Sheets
        sheet = init_google_sheets()
        if not sheet:
            await processing_msg.edit_text("❌ Ошибка подключения к Google Таблице.")
            return
        
        # Записываем в таблицу
        if write_to_sheet(sheet, order_data):
            success_message = f"""✅ Заказ успешно принят и записан!

📊 Данные:
• Продавец: {order_data.get('продавец', 'Не указано')}
• Товар: {order_data.get('товар', 'Не указано')}
• Номер: {order_data.get('номер', 'Не указано')}
• Адрес: {order_data.get('адрес', 'Не указано')}
• Выкуп: {order_data.get('выкуп', 'Не указано')}
• Предоплата: {order_data.get('предоплата', 'Не указано')}
• Доставка: {order_data.get('доставка', 'Не указано')}

Статус: Заказ принят ✅"""
            
            await processing_msg.edit_text(success_message)
        else:
            await processing_msg.edit_text("❌ Ошибка записи в таблицу.")
            
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await processing_msg.edit_text("❌ Произошла ошибка. Попробуйте еще раз.")

# Главная функция
def main():
    # Проверяем наличие необходимых переменных
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не найден!")
        return
    if not CLAUDE_API_KEY:
        logger.error("CLAUDE_API_KEY не найден!")
        return
    if not GOOGLE_SHEET_ID:
        logger.error("GOOGLE_SHEET_ID не найден!")
        return
    if not GOOGLE_CREDENTIALS:
        logger.error("GOOGLE_CREDENTIALS не найдены!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
