import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, BotCommand

from src.config.settings import settings
from src.schemas.mongo_collections import Product
from src.schemas.bot import MessageModel


def get_bot_commands():
    bot_commands = [
        BotCommand(command="/about", description="Як це працює?"),
        BotCommand(command="/join", description="Приєднатись до каналу"),
        BotCommand(command="/info", description="Інформація про Вашу підписку"),
        BotCommand(command="/payment", description="Сплатити підписку на сервіс"),
        BotCommand(command="/support", description="Надіслати питання або пропозицію")
    ]
    return bot_commands


def get_cmd_list_message() -> MessageModel:
    bot_commands = get_bot_commands()
    text = f'Ось основні команди бота:\n\n'
    for command in bot_commands:
        text += f'{command.command} - {command.description}\n'

    return MessageModel(text=text)


def get_start_message(message: Message) -> list[MessageModel]:
    text = f'Вітаю, {message.from_user.full_name}!\n\n' \
           f'НБУ запустив нумізматичний інтернет магазин https://coins.bank.gov.ua, ' \
           f'але товари на ньому з\'являються в різний час, в обмеженій кількості та ' \
           f'швидко продаються. Цей бот бере на себе моніторинг каталогу монет, ' \
           f'і одразу сповіщає Вас при надходженні нової позиції, щоб Ви встигли зробити замовлення ' \
           f'витрачаючи мінімум зусиль.\n\n' \
           f'Наразі магазин НБУ працює в тестовому режимі, тому вони можуть робити зміни, які впливають ' \
           f'на роботу бота. Такі "вдосконалення" будуть впроваджуватись максимально швидко.\n\n' \
           f'<b>Щомісячна вартість підписки становить {settings.service_price} грн.</b>\n\n'

    cmd_list_message_model = get_cmd_list_message()

    return [MessageModel(text=text), cmd_list_message_model]


def get_payment_message(payment_url: str) -> MessageModel:

    text = f'Для оплати натисніть кнопку "Оплатити", після чого Вас направить на платіжну сторінку. ' \
           f'Після успішного платежу Вам надійде посилання на канал, в якому бот публікує сповіщення про ' \
           f'надходження нового товару на сайт.'

    kb_markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text='Оплатити',
        url=payment_url
    )
    kb_markup.add(button)

    return MessageModel(text=text, keyboard=kb_markup)


def success_payment_and_invite_messages(order_reference: str,
                                        subscribe_expired_at: datetime.datetime,
                                        invite_link: str
                                        ) -> list[MessageModel]:

    _invite_button_text = 'Приєднатись'
    expired_at = subscribe_expired_at.strftime('%d.%m.%Y')

    first_message = f'Дякуємо за оплату! Номер вашого замовлення - {order_reference}\n' \
                    f'Підписка дійсна до: {expired_at}'

    second_message = f'Для Вас сформоване запрошення, натисніть кнопку "{_invite_button_text}". ' \
                     f'Бот автоматично підтвердить Ваш запит у випадку активної підписки.'

    kb_markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text=_invite_button_text,
        url=invite_link
    )
    kb_markup.add(button)

    return [
        MessageModel(text=first_message),
        MessageModel(text=second_message, keyboard=kb_markup)
    ]


def kick_user_from_channel_msg() -> MessageModel:
    text = 'Термін дії Вашої підписки закінчився, тому бот обмежив доступ до каналу.\n' \
           'Сплатіть, будь ласка, підписку на сервіс, щоб відновити доступ'

    return MessageModel(text=text)


def find_product_message(product: Product, is_new: bool = True) -> MessageModel:
    if is_new:
        title = 'З\'явився новий товар на сайті!'
    else:
        title = 'Товар знову у продажі!'

    text = f'<b>{title}</b>\n\n' \
           f'<b>Назва:</b> {product.name}\n' \
           f'<b>Ціна:</b> {product.price} грн.' \

    kb_markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        text='Переглянути',
        url=product.url
    )
    kb_markup.add(button)

    return MessageModel(text=text, keyboard=kb_markup)


def get_join_command_message(has_subscribe: bool, invite_link: str | None = None) -> MessageModel:
    if has_subscribe:
        _invite_button_text = 'Приєднатись'
        text = f'Для Вас сформоване запрошення, натисніть кнопку "{_invite_button_text}". ' \
               f'Бот автоматично підтвердить Ваш запит у випадку активної підписки.'

        kb_markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(
            text=_invite_button_text,
            url=invite_link
        )
        kb_markup.add(button)

        return MessageModel(text=text, keyboard=kb_markup)

    text = f'Нажаль, у Вас немає активної підписки.' \
           f'Скористайтесь командою \n/payment для оплати, щоб отримати посилання-запрошення ' \
           f'на канал.'

    return MessageModel(text=text)


def get_about_command_message() -> list[MessageModel]:
    text = f'Отже, як це все працює?\n' \
           f'Бот в реальному часі постійно слідкує за оновленнями на сайті інтернет магазину НБУ. ' \
           f'Як тільки з\'являється новий товар - в закритий канал відправляється сповіщення з інформацією ' \
           f'про нього, а саме: фото, назва, ціна і посилання на сторінку товару.'

    text2 = f'Щоб потрапити в канал, потрібно сплатити підписку, після чого бот відправить вам ' \
            f'посилання-запрошення на канал. Вам потрібно буде відправити запит на приєднання, а система ' \
            f'автоматично додасть вас в спільноту у випадку активної підписки.'

    text3 = f'Підписка діє 1 (один) календарний місяць. Ближче до наступної оплати, Вам буде відправлено ' \
            f'сповіщення про необхідність продовження підписки. У випадку, коли підписка не подовжилась - ' \
            f'телеграм бот закриє доступ до каналу. Але ви зможете знову приєднатись після наступної оплати.'

    return [MessageModel(text=text), MessageModel(text=text2), MessageModel(text=text3)]


def get_info_command_message(has_subscribe: bool, subscribe_expired_at: datetime.datetime):
    if has_subscribe:
        dt_format = subscribe_expired_at.strftime('%d.%m.%Y')
        text = f'У Вас є активна підписка, термін якої спливає {dt_format}'
        return MessageModel(text=text)

    text = f'Нажаль, у Вас немає активної підписки.' \
           f'Щоб оформити підписку, скористайтесь командою:\n' \
           f'/payment'

    return MessageModel(text=text)


def get_unknown_command_message() -> MessageModel:
    text = f'Невідома команда!\n'
    cmd_list_message_model = get_cmd_list_message()
    text += cmd_list_message_model.text
    return MessageModel(text=text)


def get_support_command_message() -> MessageModel:
    text = f'Ваші питання та пропозиції пишіть в особисті повідомлення адміну:\n' \
           f'@alex_support_man'
    return MessageModel(text=text)


def get_chat_join_request_message(is_approved: bool) -> MessageModel:
    if is_approved:
        text = f'Запит на приєднання до каналу схвалено. Вдалих покупок в інтернет магазині!'
    else:
        text = f'Нажаль, запит на приєднання до каналу відхилено - у Вас немає активної підписки.'

    return MessageModel(text=text)


def report_notification_message(new_products: list[Product]) -> MessageModel:
    text = f'Надсилаю Вам щоденний звіт по оновленням інтернет магазину.\n'
    if not new_products:
        text += f'Сьогодні нових товарів в інтернет магазині не надходило.'
    else:
        text += f'Сьогодні було додано нових товарів {len(new_products)} шт.'

    return MessageModel(text=text)
