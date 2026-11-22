"""Launch: python -m mafia_bot (with PYTHONPATH=src)."""
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from .storage import Store
from .scoring import calculate

router = Router()
store = None
admins = set()

class Input(StatesGroup):
    choose_actor = State()
    choose_targets = State()
    confirm = State()

def authorized(user_id):
    return user_id in admins

def keyboard(items, prefix):
    rows = []
    for i in range(0,len(items),5):
        rows.append([InlineKeyboardButton(text=str(v),callback_data=f"{prefix}:{v}") for v in items[i:i+5]])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.message(Command("start","help"))
async def help_cmd(message: Message):
    await message.answer("Микроскоринг мафии. Команды: /newgame, /games, /use GAME_ID, /role SEAT ROLE, /event, /score, /undo. Только администраторы.")

@router.message(Command("newgame"))
async def newgame(message: Message):
    if not authorized(message.from_user.id): return
    game_id = store.create_game()
    await message.answer(f"Создана партия {game_id}. Выбери: /use {game_id}")

@router.message(Command("games"))
async def games(message: Message):
    if not authorized(message.from_user.id): return
    games = store.games()
    await message.answer("\n".join(f"{g[0]} (день {g[1]})" for g in games) or "Нет партий")

@router.message(Command("use"))
async def use(message: Message, state: FSMContext):
    if not authorized(message.from_user.id): return
    args = (message.text or "").split()
    if len(args) != 2 or not store.exists(args[1]):
        await message.answer("Используй /use GAME_ID из /games"); return
    await state.clear()
    await state.update_data(game_id=args[1])
    await message.answer(f"Активная партия: {args[1]}")

@router.message(Command("role"))
async def role(message: Message, state: FSMContext):
    if not authorized(message.from_user.id): return
    args = (message.text or "").split()
    game_id = (await state.get_data()).get("game_id")
    if not game_id or len(args) != 3:
        await message.answer("Сначала /use GAME_ID, затем /role 1 red|sheriff|mafia|don|unknown"); return
    try:
        store.set_role(game_id,int(args[1]),args[2])
        await message.answer("Роль записана.")
    except ValueError as exc:
        await message.answer(str(exc))

@router.message(Command("event"))
async def event(message: Message, state: FSMContext):
    if not authorized(message.from_user.id): return
    game_id = (await state.get_data()).get("game_id")
    if not game_id:
        await message.answer("Сначала /use GAME_ID"); return
    await message.answer("Тип события",reply_markup=keyboard(["nomination","vote","will"],"kind"))

@router.callback_query(F.data.startswith("kind:"))
async def choose_kind(query: CallbackQuery, state: FSMContext):
    if not authorized(query.from_user.id): await query.answer("Нет доступа"); return
    kind = query.data.split(":",1)[1]
    data = await state.get_data()
    if not data.get("game_id"): await query.answer("Выбери игру"); return
    await state.update_data(kind=kind,targets=[])
    await state.set_state(Input.choose_actor)
    await query.message.answer("Кто совершил действие?",reply_markup=keyboard(list(range(1,11)),"actor"))
    await query.answer()

@router.callback_query(Input.choose_actor,F.data.startswith("actor:"))
async def choose_actor(query: CallbackQuery,state: FSMContext):
    if not authorized(query.from_user.id): await query.answer("Нет доступа"); return
    actor = int(query.data.split(":")[1])
    await state.update_data(actor=actor)
    await state.set_state(Input.choose_targets)
    await query.message.answer("Выбери цель (для завещания — три разные цели)",reply_markup=keyboard(list(range(1,11)),"target"))
    await query.answer()

@router.callback_query(Input.choose_targets,F.data.startswith("target:"))
async def choose_target(query: CallbackQuery,state: FSMContext):
    if not authorized(query.from_user.id): await query.answer("Нет доступа"); return
    target = int(query.data.split(":")[1])
    data = await state.get_data()
    targets = data.get("targets",[])
    if target in targets or (data["kind"] == "will" and target == data["actor"]):
        await query.answer("Недопустимая или повторная цель"); return
    targets.append(target)
    await state.update_data(targets=targets)
    count = 3 if data["kind"] == "will" else 1
    if len(targets) < count:
        await query.message.answer(f"Выбрано {len(targets)}/{count}. Выбери следующую цель.")
    else:
        await state.set_state(Input.confirm)
        await query.message.answer(f"Подтвердить: {data['kind']}, игрок {data['actor']} → {targets}?",reply_markup=keyboard(["yes","no"],"confirm"))
    await query.answer()

@router.callback_query(Input.confirm,F.data.startswith("confirm:"))
async def confirm(query: CallbackQuery,state: FSMContext):
    if not authorized(query.from_user.id): await query.answer("Нет доступа"); return
    decision = query.data.split(":")[1]
    data = await state.get_data()
    if decision == "yes":
        try:
            event_id = store.add(data["game_id"],data["kind"],data["actor"],data["targets"],1,query.from_user.id,f"callback:{query.id}")
            await query.message.answer(f"Событие записано: {event_id}")
        except ValueError as exc:
            await query.message.answer(f"Ошибка: {exc}")
    else:
        await query.message.answer("Отменено.")
    await state.set_state(None)
    await state.update_data(kind=None,actor=None,targets=[])
    await query.answer()

@router.message(Command("score"))
async def score(message: Message,state: FSMContext):
    if not authorized(message.from_user.id): return
    game_id = (await state.get_data()).get("game_id")
    if not game_id: await message.answer("Сначала /use GAME_ID"); return
    scores,entries,pending = calculate(store.roles(game_id),store.events(game_id))
    lines = [f"Игрок {n}: {v:+g}" for n,v in sorted(scores.items(),key=lambda x:(-x[1],x[0]))]
    await message.answer("Предварительный рейтинг (только выставления, голоса красных и завещания):\n"+"\n".join(lines)+f"\nОжидают определения ролей/правил: {len(pending)}")

@router.message(Command("undo"))
async def undo(message: Message,state: FSMContext):
    if not authorized(message.from_user.id): return
    game_id = (await state.get_data()).get("game_id")
    if not game_id: await message.answer("Сначала /use GAME_ID"); return
    event_id = store.undo_last(game_id,message.from_user.id)
    await message.answer(f"Отозвано: {event_id}" if event_id else "Нет событий для отмены.")

async def main():
    global store,admins
    token = os.environ.get("TELEGRAM_BOT_TOKEN","")
    admins = {int(x) for x in os.environ.get("TELEGRAM_ADMIN_IDS","").split(",") if x.strip().isdigit()}
    if not token or token == "replace-with-token" or not admins:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_IDS")
    store = Store(os.environ.get("MAFIA_DB_PATH","./runtime/mafia.sqlite3"))
    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
