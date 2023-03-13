import datetime
import time

import uvicorn
from aiogram import types, Dispatcher, Bot
from fastapi import FastAPI, Request

from src.config.settings import settings, logger
from src.bot import bot, dp, send_approve_payment_msg, remove_user_from_channel
from src.crud.payment import PaymentCRUD
from src.crud.client import ClientCRUD
from src.services.payment_controller import PaymentController
from src.services.product_parser import parser_processing
from src.schemas.mongo_collections import PaymentUpdateFields
from src.utils.bot_helpers import get_bot_commands
from src.utils.enums import ExpireDateAction
from src.utils.helpers import update_client_expire_date

app = FastAPI()


@app.get("/", include_in_schema=False)
async def main_page():
    return {
        "status": "Working"
    }


@app.on_event('startup')
async def on_startup():
    bot_commands = get_bot_commands()
    await bot.set_my_commands(bot_commands)
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != settings.bot_webhook():
        await bot.set_webhook(url=settings.bot_webhook())


@app.post(f'/bot/{settings.bot_api_token}')
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.post('/payments/approve')
async def approve_payment(request: Request):
    # {'merchantAccount': 'freelance_user_640614adde9d1', 'orderReference': '64076226c240de74e32b1a3b',
    #  'merchantSignature': '359c05b9a4870947942b2bff139a9e58', 'amount': 1, 'currency': 'UAH', 'authCode': '332226',
    #  'email': 'shurick672@gmail.com', 'phone': '380989866672', 'createdDate': 1678205498, 'processingDate': 1678205507,
    #  'cardPan': '', 'cardType': 'MasterCard', 'issuerBankCountry': 'Ukraine',
    #  'issuerBankName': 'COMMERCIAL BANK PRIVATBANK', 'recToken': '', 'transactionStatus': 'Approved', 'reason': 'Ok',
    #  'reasonCode': 1100, 'fee': 0.02, 'paymentSystem': 'googlePay', 'acquirerBankName': 'WayForPay',
    #  'cardProduct': 'debit', 'clientName': 'forward672',
    #  'products': [{'name': 'Підписка на оновлення інтернет магазину', 'price': 1, 'count': 1}]}
    data = await request.json()
    approve_response = PaymentController.create_approve_response(data)
    payment = await PaymentCRUD.get_one(data['orderReference'])
    logger.info(f'Create new payment: {payment}')
    if payment:
        status = data['transactionStatus']
        result = await PaymentCRUD.update_one(
            payment['_id'],
            PaymentUpdateFields(**{'status': status})
        )
        if result.modified_count > 0:
            if status == 'Approved':
                await send_approve_payment_msg(payment['client_id'], payment['_id'])
                await update_client_expire_date(payment['client_id'], ExpireDateAction.add)
            elif status == 'Refunded':
                await update_client_expire_date(payment['client_id'], ExpireDateAction.subtract)

    return approve_response


@app.post('/payments/fondy/approve')
async def fondy_approve_payment(request: Request):
    data = await request.json()
    payment = await PaymentCRUD.get_one(data['order_id'])
    logger.info(f'Create new payment: {payment}')
    if payment:
        status = data['order_status']
        result = await PaymentCRUD.update_one(
            payment['_id'],
            PaymentUpdateFields(**{'status': status})
        )
        if result.modified_count > 0:
            if status == 'approved':
                await update_client_expire_date(payment['client_id'], ExpireDateAction.add)
                await send_approve_payment_msg(payment['client_id'], payment['_id'])
            elif status == 'reversed':
                await update_client_expire_date(payment['client_id'], ExpireDateAction.subtract)
        else:
            logger.warning(f'Problem in update payment, cant modify. Callback data from fondy:\n{data}')

    return 'OK'


@app.get('/check_subscribe')
async def check_subscribe():
    expired_subscribers = await ClientCRUD.get_many(
        filter={'expired_at': {'$lt': datetime.datetime.now()}}
    )
    logger.info(f'Rxpired subscribers: {expired_subscribers}')
    for sub in expired_subscribers:
        try:
            chat_member = await bot.get_chat_member(chat_id=settings.channel_id, user_id=sub.chat_id)
            if chat_member['status'] == 'member':
                logger.info(f'Remove expired subscriber: first_name: {sub.first_name}, '
                            f'last_name: {sub.last_name}, username: {sub.username}')
                await remove_user_from_channel(chat_id=settings.channel_id, user_id=sub.chat_id)
        except Exception as e:
            logger.error(f'Error in check_subscribe method. Traceback: {e}')


@app.get('/start_parser')
async def start_parser():
    t = time.time()
    await parser_processing()
    logger.info(f'Parse finished at {round((time.time() - t), 2)} seconds.')


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
