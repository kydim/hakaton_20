from config import BOT_TOKEN
import logging
from telegram.ext import (
    MessageHandler, Filters, Updater, CommandHandler, InlineQueryHandler
)
from telegram import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CallbackQueryHandler
)
from bot import api
from bot.bot_config import GOODS
from random import randint

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)10s- %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

updater = Updater(token=BOT_TOKEN, use_context=True)

TEST_CNT = 0


def _ask(update, context):
    pass


def dummy():
    pass


def start(update, context):
    global TEST_CNT  # tdo delete it

    TEST_CNT = 0
    data = api.get_state(update.effective_chat.id)
    responce = api.update_state(
        chat_id=update.effective_chat.id,
        status=api.Status.init.value,
    )
    logger.info(f'update: {update}')
    logger.info(f'responce: {responce}')

    update.message.reply_text(responce.bot_text)

    # keyboard = [
    #     [InlineKeyboardButton(v, callback_data=k)]
    #     for k, v in GOODS.items()
    # ]
    #
    # reply_markup = InlineKeyboardMarkup(keyboard)
    #
    # update.message.reply_text(responce.bot_text, reply_markup=reply_markup)


def message(update, context):

    chat_id = update.effective_chat.id
    data = api.get_state(chat_id)
    logger.info(f'data: {data}')

    responce = api.update_state(
        chat_id=chat_id,
        status=api.Status.wait_category.value,
        user_query=update.message.text,
    )
    logger.info(f'responce: {responce}')

    # update.message.reply_text(f'responce.status: {responce.status}')

    if responce.status == api.Status.wait_category.value:
        keyboard = [
            [InlineKeyboardButton(v, callback_data=k)]
            for k, v in GOODS.items()
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(responce.bot_text, reply_markup=reply_markup)

    elif responce.status == api.Status.looking.value:
        data = api.get_state(chat_id)
        logger.info(f'data: {data}')
        responce = api.update_state(
            chat_id=chat_id,
            status=api.Status.wait_category.value,
            user_query=update.message.text,
        )

        new_job = context.job_queue.run_repeating(alarm, randint(0, 3), context=update.effective_chat.id)
        context.chat_data['job'] = new_job
        update.message.reply_text(responce.bot_text)


def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


def unset(context):
    # """Remove the job if the user changed their mind."""
    # if 'job' not in context.chat_data:
    #     update.message.reply_text('You have no active timer')
    #     return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']


def alarm(context):
    global TEST_CNT  # delete it

    """Send the alarm message."""
    job = context.job
    if TEST_CNT == 0:
        text = api.get_nearest_station()
    else:
        text = 'Еще немного терпения ...'

    if TEST_CNT > 1:
        job.schedule_removal()
        text = api.get_result()
        api.reset()

    context.bot.send_message(job.context, text=text)
    TEST_CNT += 1


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_repeating(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def button(update, context):
    query = update.callback_query
    good_name = GOODS[query.data]

    chat_id = update.effective_chat.id
    data = api.get_state(chat_id)
    logger.info(f'data: {data}')
    responce = api.update_state(
        chat_id=chat_id,
        status=api.Status.wait_category.value,
        user_query=good_name,
    )
    logger.info(f'responce: {responce}')

    if responce.status == api.Status.looking.value:
        new_job = context.job_queue.run_repeating(alarm, 3, context=update.effective_chat.id)
        context.chat_data['job'] = new_job
        context.bot.send_message(
            chat_id=chat_id,
            text=responce.bot_text,
        )


def main():
    dp = updater.dispatcher
    start_handler = CommandHandler('start', start,
        pass_job_queue=True,
        pass_user_data=True,
        pass_chat_data=True,)
    dp.add_handler(start_handler)
    updater.start_polling()

    message_handler = MessageHandler(
        Filters.text & (~Filters.command),
        message,
        pass_job_queue=True,
        pass_user_data=True,
        pass_chat_data=True,
    )
    dp.add_handler(message_handler)

    dp.add_handler(CallbackQueryHandler(button))

    inline_caps_handler = InlineQueryHandler(inline_caps)
    dp.add_handler(inline_caps_handler)

    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    unknown_handler = MessageHandler(Filters.command, unknown)
    dp.add_handler(unknown_handler)
    updater.idle()


if __name__ == '__main__':
    main()
