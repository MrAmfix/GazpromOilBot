# GazpromOilBot

## Как запустить бота + приложение?

1. Склонируйте репозиторий
```commandline
git clone https://github.com/MrAmfix/GazpromOilBot.git
cd GazpromOilBot
```
2. Настройте `.env`:
```commandline
cp .env-example .env
```
Все переменные, что указаны в {} заполните своими данными
* BOT_TOKEN - токен вашего бота, получите его у [Bot Father](https://t.me/BotFather)
* BOT_USERNAME — username бота без @
* POSTGRES_USER — имя пользователя для базы данных
* POSTGRES_PASSWORD — пароль пользователя
* POSTGRES_DB — название базы данных
* WEB_HOST - публичный адрес веб-приложения (например: `https://bot.mysuperbot.com`)
`❗️ Важно: localhost не подойдёт — Telegram требует публичный HTTPS`

3. Настройте домен у [Bot Father](https://t.me/BotFather)
* Напишите `/setdomain`
* Выберите вашего бота
* Введите ваш домен без https://, например: `bot.mysuperbot.com`

4. Запустите бота
```commandline
docker-compose up --build
```

Контакты:
![telegram](https://t.me/favicon.ico) [Я в Telegram](https://t.me/mramfix)
![github](https://github.com/favicon.ico) [Я на GitHub](https://github.com/MrAmfix)
