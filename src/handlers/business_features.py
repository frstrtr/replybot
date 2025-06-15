"""Business-related features for the bot, including contact and business hours"""

from aiogram import Dispatcher, F
from aiogram.types import Message  # , CallbackQuery
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BUSINESS_CONTACT_EMAIL, BUSINESS_HOURS
from keyboards.reply_keyboards import get_business_menu_keyboard

router = Router()  # Keep this router local to these features


class BusinessDialog(StatesGroup):
    """States for business dialog flow"""

    waiting_for_message = State()
    waiting_for_contact = State()


async def cmd_business_start(message: Message):
    """Handler for /business command"""
    await message.answer(
        "Welcome to our business bot! How can I help you today?",
        reply_markup=get_business_menu_keyboard(),
    )


async def business_hours(message: Message):
    """Handler for business hours button"""
    await message.answer(f"Our business hours are: {BUSINESS_HOURS}")


async def business_contact(message: Message, state: FSMContext):
    """Handler for contact button"""
    await message.answer(
        f"You can reach us at: {BUSINESS_CONTACT_EMAIL}\n"
        f"Or leave your contact info and we'll get back to you.",
    )
    await message.answer("Please enter your contact information:")
    await state.set_state(BusinessDialog.waiting_for_contact)  # Use state.set_state


async def process_contact_info(message: Message, state: FSMContext):
    """Process contact information from user"""
    await state.update_data(contact_info=message.text)
    await message.answer(
        "Thank you for providing your contact information. "
        "Our team will get back to you as soon as possible."
    )
    await state.clear()

    # Here you would typically save this information to a database
    # and notify business representatives


async def business_message_command_handler(
    message: Message, state: FSMContext
):  # Renamed to avoid conflict
    """Handler for starting a business message via command/button"""
    await message.answer("Please enter your message to our business:")
    await state.set_state(BusinessDialog.waiting_for_message)  # Use state.set_state


async def process_business_message(message: Message, state: FSMContext):
    """Process business message from user (from FSM)"""
    await state.update_data(user_message=message.text)
    await message.answer(
        "Thank you for your message. Our team will process it and respond shortly."
    )
    await state.clear()

    # Here you would typically save this message to a database
    # and notify business representatives


def register_business_command_handlers(dp: Dispatcher):  # Renamed registration function
    """Register all business feature command handlers"""
    dp.include_router(router)

    # Register handlers
    router.message.register(cmd_business_start, Command("business"))
    router.message.register(business_hours, F.text == "Business Hours")
    router.message.register(business_contact, F.text == "Contact Us")
    router.message.register(
        business_message_command_handler, F.text == "Send Business Message"
    )  # Ensure this matches keyboard

    # State handlers
    router.message.register(process_contact_info, BusinessDialog.waiting_for_contact)
    router.message.register(
        process_business_message, BusinessDialog.waiting_for_message
    )
