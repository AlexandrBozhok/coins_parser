import asyncio
import datetime
import time

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.exceptions import BotBlocked, RetryAfter
from bson import ObjectId

from src.config.settings import settings, logger
from src.crud.client import ClientCRUD
from src.crud.invite import InviteCRUD
from src.crud.payment import PaymentCRUD
from src.crud.product import ProductCRUD
from src.schemas.mongo_collections import ClientIn, PaymentIn, Product, Invite
from src.services.payment_controller import PaymentControllerV2
from src.utils.bot_helpers import get_start_message, get_payment_message, success_payment_and_invite_messages, \
    kick_user_from_channel_msg, find_product_message, get_join_command_message, get_info_command_message, \
    get_unknown_command_message, get_support_command_message, get_about_command_message, get_chat_join_request_message, \
    report_notification_message
from src.utils.helpers import client_has_active_sub
from src.utils.utils import generate_fondy_payment_params

bot = Bot(settings.bot_api_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['about'])
async def about_command(message: Message):
    message_models = get_about_command_message()
    for model in message_models:
        try:
            await message.answer(model.text, reply_markup=model.keyboard)
            await asyncio.sleep(8)
        except BotBlocked:
            break


@dp.message_handler(commands=['start'])
async def start(message: Message):
    is_exists = await ClientCRUD.exists_by_chat_id(message.from_user.id)
    if not is_exists:
        new_client = ClientIn(
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            chat_id=message.from_user.id
        )
        client = await ClientCRUD.insert_one(new_client)
        logger.info(f'Add new client: {client}')
    message_models = get_start_message(message)
    for model in message_models:
        try:
            await message.answer(
                text=model.text,
                reply_markup=model.keyboard,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
        except BotBlocked:
            break
        await asyncio.sleep(8)


@dp.message_handler(commands=['payment'])
async def create_payment(message: Message):
    client = await ClientCRUD.get_one(chat_id=message.from_user.id)
    order_id = str(ObjectId())
    payment_params = generate_fondy_payment_params(order_id)
    payment_url = PaymentControllerV2.create_invoice_url(payment_params)
    if payment_url:
        logger.info(f'Create New payment. User: {message.from_user}')
        message_model = get_payment_message(payment_url)
        try:
            await message.answer(text=message_model.text, reply_markup=message_model.keyboard)
        except BotBlocked:
            pass
        new_payment = PaymentIn(
            id=order_id,
            client_id=str(client.id),
            amount=payment_params.amount,
            invoice_url=payment_url
        )
        result = await PaymentCRUD.insert_one(new_payment)
        logger.info(f'Inserted new payment {result}')


@dp.message_handler(commands=['join'])
async def join_command(message: Message):
    client = await ClientCRUD.get_one(chat_id=message.from_user.id)
    has_subscribe = client_has_active_sub(client)
    if has_subscribe:
        invite_link = await get_or_create_invite_link()
        message_model = get_join_command_message(has_subscribe, invite_link)
    else:
        message_model = get_join_command_message(has_subscribe)

    try:
        await message.answer(text=message_model.text, reply_markup=message_model.keyboard)
    except BotBlocked:
        pass


@dp.message_handler(commands=['info'])
async def info_command(message: Message):
    client = await ClientCRUD.get_one(chat_id=message.from_user.id)
    has_subscribe = client_has_active_sub(client)
    message_model = get_info_command_message(has_subscribe, client.expired_at)

    try:
        await message.answer(text=message_model.text, reply_markup=message_model.keyboard)
    except BotBlocked:
        pass


@dp.message_handler(commands=['support'])
async def support_command(message: Message):
    message_model = get_support_command_message()
    try:
        await message.answer(text=message_model.text, reply_markup=message_model.keyboard)
    except BotBlocked:
        pass


@dp.chat_join_request_handler()
async def chat_join_approve_or_decline(update: types.ChatJoinRequest):
    """ Відслідковує запити на приєднання до каналу, якщо юзер сплатив підписку - підтверджує інвайт """
    logger.info(f'New chat join request: {update}')
    user_id = update['from']['id']
    client = await ClientCRUD.get_one(chat_id=user_id)
    has_subscribe = client_has_active_sub(client)
    try:
        if has_subscribe:
            await update.approve()
        else:
            await update.decline()

        message_model = get_chat_join_request_message(is_approved=has_subscribe)
        await bot.send_message(chat_id=user_id, text=message_model.text)
    except Exception as e:
        logger.error(f'Error with approve or decline invite. Traceback: {e}')


@dp.message_handler()
async def echo_message(message: Message):
    message_model = get_unknown_command_message()
    try:
        await message.answer(text=message_model.text)
    except BotBlocked:
        pass


async def send_approve_payment_msg(client_id: str, order_reference: str):
    client = await ClientCRUD.get_one(id=client_id)
    if client:
        invite_link = await get_or_create_invite_link()
        message_models = success_payment_and_invite_messages(
            order_reference,
            client.expired_at,
            invite_link
        )
        for model in message_models:
            try:
                await bot.send_message(
                    chat_id=client.chat_id,
                    text=model.text,
                    reply_markup=model.keyboard
                )
            except BotBlocked:
                break
            await asyncio.sleep(3)


async def get_or_create_invite_link():
    link_from_db = await InviteCRUD.get()
    if link_from_db:
        is_expired = link_from_db['expired_at'].timestamp() < datetime.datetime.now(tz=settings.default_tz).timestamp()
        if not is_expired:
            return link_from_db['link']

    link_obj = await bot.create_chat_invite_link(
        chat_id=settings.channel_id,
        expire_date=datetime.datetime.now(tz=settings.default_tz) + datetime.timedelta(days=3),
        creates_join_request=True
    )

    await InviteCRUD.update_or_create(Invite(
        link=link_obj.invite_link,
        expired_at=link_obj.expire_date
    ))
    return link_obj.invite_link


async def send_find_product_message(chat_id: str, product: Product, is_new: bool = True):
    message_model = find_product_message(product, is_new)

    try:
        await bot.send_photo(
            photo=product.image_url,
            chat_id=chat_id,
            caption=message_model.text,
            reply_markup=message_model.keyboard,
            parse_mode='HTML'
        )
    except RetryAfter as e:
        logger.error(f'Retry after error. Timeout: {e.timeout}')
        await asyncio.sleep(e.timeout)


async def remove_user_from_channel(chat_id: str, user_id: int):
    await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    # Коли бот банить юзера, він потрапляє в чорний список. Щоб в подальшому юзер міг
    # приєднатись за посиланням, треба видалити його з цього списку методом unban_chat_member
    await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)

    message_model = kick_user_from_channel_msg()
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message_model.text,
            reply_markup=message_model.keyboard
        )
    except BotBlocked:
        pass


async def send_report():
    start_time = time.time()
    today = datetime.date.today()
    start_dt = datetime.datetime.combine(today, datetime.time.min)
    end_dt = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time.min)
    new_products = await ProductCRUD.get_many(filter={
        'available_from': {'$gte': start_dt, '$lt': end_dt}
    })
    cursor = await ClientCRUD.get_many(
        filter={'expired_at': {'$gte': datetime.datetime.now(tz=settings.default_tz)}},
        cursor_mode=True
    )
    message_model = report_notification_message(new_products=new_products)
    async for client in cursor:
        try:
            await bot.send_message(chat_id=client['chat_id'], text=message_model.text)
        except BotBlocked:
            pass

    logger.info(f'Task send report notifications completed work at '
                f'{round(time.time() - start_time, 2)} sec.')
