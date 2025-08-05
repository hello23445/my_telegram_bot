from telegram import Update, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, PreCheckoutQueryHandler

# Токены ботов
MAIN_BOT_TOKEN = '7435075014:AAF3sagbYsDlAfGFi6tO0HavXKNXATatdHk'  # Токен для основного бота
SECOND_BOT_TOKEN = '7633424551:AAHKj7bCuaNCuA2cBPcgRFpQsRFRyE1gliY'  # Токен для второго бота

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    query = context.args
    if query:
        try:
            # Разделяем строку на количество кристаллов и количество звезд
            crystals, stars = map(int, query[0].split('_'))
        except ValueError:
            await update.message.reply_text("Ошибка")
            return

        # Прямое использование количества звезд как стоимости
        prices = [LabeledPrice(f"Кристаллы {crystals:,}".replace(",", " "), stars)]  # Заменяем запятую на пробел

        await update.message.reply_invoice(
            title="Покупка кристаллов",
            description=f"Получите {crystals:,}".replace(",", " ") + " кристаллов",  # Заменяем запятую на пробел
            payload=str(crystals),  # Уникальный идентификатор платежа
            provider_token=None,  # Не требуется для XTR
            currency="XTR",  # Используем XTR как валюту
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
        )
    else:
        await update.message.reply_text("Ошибка")

# Обработчик подтверждения оплаты
async def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload.isdigit():  # Проверяем payload
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Что-то пошло не так. Попробуйте снова.")

# Обработчик успешной оплаты
async def successful_payment(update: Update, context: CallbackContext):
    payment = update.message.successful_payment
    crystals = int(payment.invoice_payload)  # Используем количество кристаллов
    stars = payment.total_amount  # Количество звезд из суммы платежа

    # Получаем chat_id пользователя, который оплатил
    user_chat_id = update.message.chat_id

    # Отправляем сообщение пользователю с подтверждением
    await update.message.reply_text(f"Оплата на {stars:,}".replace(",", " ") + " звезд успешно выполнена! Вы получили " + f"{crystals:,}".replace(",", " ") + " кристаллов.")

    # Отправляем сообщение в другой бот
    second_bot = Application.builder().token(SECOND_BOT_TOKEN).build()

    # Создаём кнопки с ReplyKeyboardMarkup (без форматирования чисел для кнопки)
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(f"Получить {crystals}")]
    ], one_time_keyboard=True, resize_keyboard=True)

    # Отправляем сообщение пользователю с кнопкой
    await second_bot.bot.send_message(
        chat_id=user_chat_id,  # Отправляем сообщение пользователю, который оплатил
        text=f"Вы оплатили {stars:,}".replace(",", " ") + " звезд за " + f"{crystals:,}".replace(",", " ") + " кристаллов.",
        reply_markup=keyboard
    )

# Запуск бота
def main():
    application = Application.builder().token(MAIN_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    application.run_polling()

if __name__ == "__main__":
    main()
