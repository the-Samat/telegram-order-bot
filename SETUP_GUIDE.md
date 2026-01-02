# 📖 Пошаговая инструкция по настройке

## Шаг 1: Загрузка файлов в GitHub

1. Откройте ваш репозиторий `telegram-order-bot` на GitHub
2. Нажмите кнопку **"Add file"** → **"Upload files"**
3. Загрузите следующие файлы:
   - `main.py`
   - `requirements.txt`
   - `README.md`
4. Переименуйте `gitignore.txt` в `.gitignore` при загрузке
5. Нажмите **"Commit changes"**

## Шаг 2: Настройка Google Service Account

1. Перейдите на: https://console.cloud.google.com/
2. Создайте новый проект (или выберите существующий)
3. Включите **Google Sheets API**:
   - Перейдите в "APIs & Services" → "Enable APIs and Services"
   - Найдите "Google Sheets API"
   - Нажмите "Enable"
4. Создайте Service Account:
   - "APIs & Services" → "Credentials"
   - "Create Credentials" → "Service Account"
   - Заполните имя (например: telegram-bot)
   - Нажмите "Create and Continue"
   - Пропустите остальные шаги
5. Создайте JSON ключ:
   - Нажмите на созданный Service Account
   - Вкладка "Keys"
   - "Add Key" → "Create new key"
   - Выберите JSON
   - Скачайте файл
6. Откройте скачанный JSON файл блокнотом
7. Скопируйте ВСЁ содержимое (весь JSON текст)

## Шаг 3: Дайте доступ к таблице

1. В JSON файле найдите поле `"client_email"`
2. Скопируйте email (выглядит как: `telegram-bot@...iam.gserviceaccount.com`)
3. Откройте вашу Google Таблицу `Orders Database`
4. Нажмите "Поделиться" (Share)
5. Вставьте скопированный email
6. Дайте права "Редактор"
7. Нажмите "Готово"

## Шаг 4: Настройка Render.com

1. Откройте Render.com (вы уже вошли)
2. Нажмите **"New +"** → **"Web Service"**
3. Выберите **"Build and deploy from a Git repository"**
4. Нажмите **"Connect account"** для GitHub (если еще не подключили)
5. Найдите репозиторий `telegram-order-bot`
6. Нажмите **"Connect"**

### Настройки сервиса:

- **Name:** `telegram-order-bot` (или любое имя)
- **Region:** выберите ближайший
- **Branch:** `main`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Instance Type:** `Free`

## Шаг 5: Добавление Environment Variables

На странице настройки Render.com прокрутите до раздела **"Environment Variables"**.

Добавьте 4 переменные:

### 1. TELEGRAM_TOKEN
- **Key:** `TELEGRAM_TOKEN`
- **Value:** (ваш токен бота от BotFather)

### 2. CLAUDE_API_KEY
- **Key:** `CLAUDE_API_KEY`
- **Value:** (ваш Claude API ключ, начинается с `sk-ant-api03-...`)

### 3. GOOGLE_SHEET_ID
- **Key:** `GOOGLE_SHEET_ID`
- **Value:** (ID вашей таблицы из URL)

### 4. GOOGLE_CREDENTIALS
- **Key:** `GOOGLE_CREDENTIALS`
- **Value:** (весь JSON из скачанного файла Google Service Account)
  - Скопируйте ВСЕ содержимое JSON файла
  - Вставьте как есть (весь текст)

## Шаг 6: Запуск

1. Нажмите **"Create Web Service"**
2. Render начнет деплой (займет 2-5 минут)
3. Дождитесь статуса **"Live"** (зеленый)
4. Бот готов к работе! 🎉

## Проверка работы

1. Откройте Telegram
2. Найдите вашего бота: `@zakazy_kg_bot`
3. Нажмите /start
4. Отправьте тестовый заказ:

```
*Заказ*
• Продавец: Тест
• Товар: Тестовый товар
• Номер: +996 555 123456
• Адрес: Тестовый адрес
• Выкуп: 1000
• Предоплата: 500
• Доставка: 100
```

5. Проверьте Google Таблицу - должна появиться новая строка!

## 🎯 Готово!

Ваш бот работает 24/7 и автоматически принимает заказы!

## 💰 Стоимость

- ✅ Telegram Bot - бесплатно
- ✅ Render.com - бесплатно (750 часов/месяц)
- ✅ Google Sheets - бесплатно
- ✅ Claude API - $5 бесплатно (хватит на 2000+ заказов)

## 🆘 Помощь

Если что-то не работает:
1. Проверьте логи в Render.com (вкладка "Logs")
2. Убедитесь что все Environment Variables заполнены правильно
3. Проверьте что Service Account имеет доступ к таблице
