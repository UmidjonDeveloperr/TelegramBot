import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import ADMIN_ID
from db_checks import add_test, delete_test, get_test, get_all_tests
import logging

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int):
    return user_id == ADMIN_ID

class TestStates(StatesGroup):
    waiting_for_test_data = State()
    waiting_for_test_id = State()

# ADMIN uchun keyboard
def get_admin_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ Test qo'shish")
    builder.button(text="🗑 Test o'chirish")
    builder.button(text="📜 Barcha testlar")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# USER uchun keyboard
def get_user_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Test ishlash")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("start"))
async def start_command(message: types.Message):
    """Start komandasi: foydalanuvchi yoki admin ekanini aniqlaydi"""
    try:
        photo_path = "https://github.com/UmidjonDeveloperr/TelegramBot/blob/5b982cdba2b6dcf6ec1cb9d7cdffc44b1fed54b1/images/welcometc.PNG"
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Rasm topilmadi: {photo_path}")

        photo = FSInputFile(photo_path)
        if is_admin(message.from_user.id):
            caption = "Assalomu alaykum, Admin!\n\nQuyidagi tugmalardan foydalaning:"
            reply_markup = get_admin_keyboard()
        else:
            caption = "Assalomu alaykum!\n\nTest ishlash uchun quyidagi tugmani bosing:"
            reply_markup = get_user_keyboard()

        await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)

    except FileNotFoundError as e:
        logger.warning(str(e))
        await message.answer(
            "Xush kelibsiz!\n\nQuyidagi tugmalardan foydalaning:",
            reply_markup=get_admin_keyboard() if is_admin(message.from_user.id) else get_user_keyboard()
        )
    except Exception as e:
        logger.error(f"Start commandda xato: {e}", exc_info=True)
        await message.answer(
            "Xush kelibsiz! Botda xatolik yuz berdi.",
            reply_markup=get_admin_keyboard() if is_admin(message.from_user.id) else get_user_keyboard()
        )

# --------------- ADMIN FUNKSIYALARI ---------------
@router.message(lambda message: message.text == "➕ Test qo'shish")
async def add_test_command(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Siz admin emassiz!")
    await state.set_state(TestStates.waiting_for_test_data)
    await message.answer("Test ID va javoblarini kiriting:\n`test_id:javoblar`")

@router.message(lambda message: message.text == "🗑 Test o'chirish")
async def remove_test_command(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Siz admin emassiz!")
    await state.set_state(TestStates.waiting_for_test_id)
    await message.answer("O'chiriladigan test ID sini kiriting:")

@router.message(TestStates.waiting_for_test_data)
async def save_test(message: types.Message, state: FSMContext):
    """Test qo'shish"""
    try:
        test_id, answers = message.text.split(":")
        if get_test(test_id):
            return await message.answer(f"Bunday nomli ID databaseda bor Iltimos boshqa ID kiriting!")
        add_test(test_id.strip(), answers.strip())
        await message.answer(f"✅ Test `{test_id}` saqlandi!", reply_markup=get_admin_keyboard())
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    finally:
        await state.clear()

@router.message(lambda message: message.text == "📜 Barcha testlar")
async def list_all_tests(message: types.Message):
    """Barcha testlarni ID va javoblari bilan chiqarish"""
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Siz admin emassiz!")

    tests = get_all_tests()  # Barcha testlarni olish
    if not tests:
        return await message.answer("📭 Hozircha hech qanday test yo'q.")

    result_message = "📜 **Barcha testlar:**\n\n"
    for test in tests:
        result_message += f"🆔 {test['test_id']}: {test['answers']} ({test['created_at']})\n"

    await message.answer(result_message)


@router.message(TestStates.waiting_for_test_id)
async def delete_test_handler(message: types.Message, state: FSMContext):
    """Testni o‘chirish"""
    test_id = message.text.strip()
    if not get_test(test_id):
        return await message.answer(f"4️⃣0️⃣4️⃣ Bunday ID databaseda yo'q!🤔")
    delete_test(test_id)
    await message.answer(f"🗑 Test `{test_id}` o'chirildi!", reply_markup=get_admin_keyboard())
    await state.clear()

# ❗️ Invalid buyruqlarni tekshirish
@router.message(lambda message: is_admin(message.from_user.id) and message.text not in ["➕ Test qo'shish", "🗑 Test o'chirish", "/start"])
async def invalid_command(message: types.Message):
    """Noto‘g‘ri buyruqlar uchun xabar chiqarish"""
    await message.answer("❌ Invalid Command! Iltimos quyidagilardan birini kiriting:\n\n"
                         "➕ Test qo'shish\n"
                         "🗑 Test o'chirish", reply_markup=get_admin_keyboard())

# --------------- USER FUNKSIYALARI ---------------
@router.message(lambda message: message.text == "📝 Test ishlash")
async def solve_test_button(message: types.Message):
    """Foydalanuvchi testni boshlaydi"""
    await message.answer(
        "Test ID va javoblaringizni quyidagi formatda yuboring:\n"
        "`test_id:javoblar`\n\n"
        "Misol: `test1:ABCD`",
        reply_markup=get_user_keyboard()
    )

@router.message(lambda message: ":" in message.text and not is_admin(message.from_user.id))
async def check_answers(message: types.Message):
    """Test natijalarini tekshirish"""
    try:
        test_id, user_answers = message.text.split(":", 1)
        test_id = test_id.strip()
        user_answers = user_answers.strip().upper()

        correct_answers = get_test(test_id)
        if not correct_answers:
            return await message.answer("❌ Bunday test topilmadi!", reply_markup=get_user_keyboard())

        if isinstance(correct_answers, (list, tuple)):
            correct_answers = correct_answers[0] if correct_answers else ""

        correct_answers = str(correct_answers).upper()

        if len(user_answers) != len(correct_answers):
            return await message.answer(f"❌ Javoblar soni noto'g'ri! Kutilgan: {len(correct_answers)}", reply_markup=get_user_keyboard())

        correct_count = 0
        feedback = []
        for i, (u, c) in enumerate(zip(user_answers, correct_answers), start=1):
            if u == c:
                feedback.append(f"{i}) {u} ✅")
                correct_count += 1
            else:
                feedback.append(f"{i}) {u} ❌ (To‘g‘ri: {c})")

        score = (correct_count / len(correct_answers)) * 100

        result_message = (
            f"📊 Test: {test_id}\n"
            f"✅ To'g'ri: {correct_count}/{len(correct_answers)}\n"
            f"📈 Foiz: {score:.1f}%\n\n"
            f"📋 Natijalar:\n" + "\n".join(feedback)
        )
        await message.answer(result_message, reply_markup=get_user_keyboard())

    except Exception as e:
        logger.error(f"Xato: {e}", exc_info=True)
        await message.answer("❌ Xatolik yuz berdi. Format: `test_id:javoblar`", reply_markup=get_user_keyboard())

# ❗️ Invalid buyruqlarni tekshirish
@router.message(lambda message: not is_admin(message.from_user.id) and message.text not in ["📝 Test ishlash", "/start"])
async def invalid_command(message: types.Message):
    """Noto‘g‘ri buyruqlar uchun xabar chiqarish"""
    await message.answer("❌ Invalid Command! Iltimos quyidagi buyruqni kiriting:\n\n"
                         "📝 Test ishlash", reply_markup=get_user_keyboard())

# --------------- DEFAULT HANDLER ---------------
@router.message()
async def default_handler(message: types.Message):
    """Noto‘g‘ri xabarlar uchun umumiy javob"""
    if is_admin(message.from_user.id):
        await message.answer("Admin buyruqlari: \n➕ Test qo'shish, 🗑 Test o'chirish", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Test ishlash uchun pastdagi tugmadan foydalaning:", reply_markup=get_user_keyboard())
