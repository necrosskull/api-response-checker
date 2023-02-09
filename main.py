import requests
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Updater)

import config

TELEGRAM_TOKEN = config.token
secret = config.secret

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Moscow'))


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Привет! Я бот, который проверяет работоспособность API\n\nДля проверки напиши /check\nДля запуска '
        'автоматической проверки напиши /start_check\nДля остановки автоматической проверки напиши /stop')


def fetch(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def schedule_check(context: CallbackContext, update: Update) -> None:
    url = f"https://schedule.mirea.ninja/api/schedule/teacher/Карпов"
    teacher_schedule = fetch(url)
    if teacher_schedule is None:
        check(update, context)
        refresh_schedule(context, update)


def refresh_schedule(context: CallbackContext, update: Update) -> None:
    url = f"https://schedule.mirea.ninja/api/refresh?secret_key={secret}"
    headers = {"accept": "application/json"}
    data = {}
    response = requests.post(url, headers=headers, data=data)
    context.bot.send_message(chat_id=update.message.chat_id, text="Расписание обновлено")
    check(update, context)
    return response.json()


def check(update: Update, context: CallbackContext) -> None:
    url = f"https://schedule.mirea.ninja/api/schedule/teacher/Карпов"
    teacher_schedule = fetch(url)
    if teacher_schedule is None:
        context.bot.send_message(chat_id=update.message.chat_id, text="Api ❌")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Api ✅")


def start_check(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.message.chat_id, text="Запущена проверка")
    check(update, context)

    scheduler.add_job(schedule_check, 'interval', [context, update], seconds=30, id=str(update.message.chat_id))
    scheduler.start()


def stop_check(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.message.chat_id, text="Проверка остановлена")
    check(update, context)
    scheduler.remove_job(str(update.message.chat_id))


def main():
    start_handler = CommandHandler('start', start, run_async=True)
    start_check_handler = CommandHandler('start_check', start_check, run_async=True)
    stop_check_handler = CommandHandler('stop', stop_check, run_async=True)
    check_handler = CommandHandler('check', check, run_async=True)

    dispatcher.add_handler(check_handler)
    dispatcher.add_handler(stop_check_handler)
    dispatcher.add_handler(start_check_handler)
    dispatcher.add_handler(start_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
