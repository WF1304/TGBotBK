from aiogram.dispatcher import Dispatcher
from aiogram import types, Bot
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import *

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


class FSM(StatesGroup):

    balance = State()
    k1 = State()
    k2 = State()

@dp.message_handler(commands=['help'])
async def Help(message: types.Message):
    await bot.send_message(message.from_user.id, 'FAQ => https://t.me/foxes1231')

@dp.message_handler(commands=['start'], state=None)
async def FSM_Start(message: types.Message):
    await FSM.balance.set()
    await message.answer('Укажите свой бюджет.')


@dp.message_handler(state=FSM.balance)
async def Balance(message: types.Message, state: FSMContext):
    async with state.proxy() as date:
        date['balance'] = float(message.text)
        await FSM.next()
        await message.answer('Введите коэффициент на 1-ю команду.')


@dp.message_handler(state=FSM.k1)
async def koef1(message: types.Message, state: FSMContext):
    async with state.proxy() as date:
        date['k1'] = float(message.text)
        await FSM.next()
        await message.answer('Введите коэффицинет на 2-ю команду.')


@dp.message_handler(state=FSM.k2)
async def koef2(message: types.Message, state: FSMContext):
    async with state.proxy() as date:
        date['k2'] = float(message.text)

    p = 1/2

    precent_1 = (p * (date['k1'] + 1) - 1) / date['k1']
    precent_2 = (p * (date['k2'] + 1) - 1) / date['k2']

    bet1 = round(date['balance'] * (precent_1 * 100) / 100, 0)
    bet2 = round(date['balance'] * (precent_2 * 100) / 100, 0)
    Bet = round(bet1 + bet2, 0)

    Wresult = bet1 * date['k1']
    Lresult = bet2 * date['k2']

    NewWBalance = (date['balance'] - Bet) + Wresult
    NewLBalance = (date['balance'] - Bet) + Lresult

    Wout = NewWBalance - (NewWBalance * 13 / 100)
    Lout = NewLBalance - (NewLBalance * 13 / 100)

    ostW = Wout - date['balance']
    ostL = Lout - date['balance']

    await bot.send_message(message.from_user.id,
                           "Сумма ставки на первую команду: " + str(bet1) + "₽ => Коэф: " + str(
                               date['k1']) + "\nСумма ставки на вторую команду: " + str(bet2) + "₽ => Коэф: "
                           + str(date['k2']) + "\n\nОбщая сумма ставки: " + str(Bet) +
                           "₽\n\nДоход от 1й команды: " +
                           str(round(Wresult, 2))
                           + f"₽ | Баланс => {round(NewWBalance, 2)}\nДоход от 2й команды: " +
                           str(round(Lresult, 2))
                           + f"₽ | Баланс => {round(NewLBalance, 2)}\n\nДоход с вывода баланса 1й команды => {round(Wout, 2)}₽ // Результат {round(ostW, 2)}₽\nДоход с вывода баланса 2й команды => {round(Lout,2)}₽ // Результат {round(ostL, 2)}₽")

    await state.finish()


@dp.message_handler(content_types='text')
async def TextUser(message: types.Message):
    await message.answer('Необходимо снова прописать /start для изменения значений.')




executor.start_polling(dp, skip_updates=True)
