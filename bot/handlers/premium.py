# file: bot/handlers/premium.py
"""Premium subscription handler"""

import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.db import is_premium, get_active_subscription
from bot.services.premium_service import activate_premium, get_premium_benefits
from bot.keyboards.premium import get_premium_tiers_keyboard
from bot.loader import bot
from config import config

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text == "👑 Premium")
async def show_premium_menu(message: types.Message) -> None:
    """Show premium subscription options"""
    user_id = message.from_user.id
    
    if await is_premium(user_id):
        benefits = await get_premium_benefits(user_id)
        await message.answer(benefits)
        return
    
    menu = """
👑 PREMIUM MEMBERSHIP 👑

⚡ SUPERPOWER YOUR DATING:
✅ 20 swipes/day (2.5x more!)
✅ See who liked you
✅ Unlimited super-likes
✅ Profile boost
✅ Priority in search

💎 CHOOSE YOUR PLAN:
"""
    await message.answer(menu, reply_markup=get_premium_tiers_keyboard())


@router.callback_query(lambda c: c.data.startswith("premium:buy:"))
async def buy_premium(query: types.CallbackQuery) -> None:
    """Handle premium purchase with Telegram Stars"""
    tier = query.data.split(":")[2]
    user_id = query.from_user.id
    
    if tier not in config.PREMIUM_TIERS:
        await query.answer("❌ Invalid tier")
        return
    
    tier_data = config.PREMIUM_TIERS[tier]
    
    # Send invoice using Telegram Stars
    try:
        await query.bot.send_invoice(
            user_id,
            title=tier_data['name'],
            description="Premium Dating App Membership",
            payload=f"premium_{tier}_{user_id}",
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",  # XTR = Telegram Stars
            prices=[types.LabeledPrice(label=tier_data['name'], amount=tier_data['price_stars'])]
        )
        await query.answer("💳 Invoice sent!")
        logger.info(f"Premium invoice sent: {user_id} - {tier}")
    except Exception as e:
        logger.error(f"Invoice error: {e}")
        await query.answer("❌ Error processing payment")


@router.pre_checkout_query()
async def process_pre_checkout(query: types.PreCheckoutQuery) -> None:
    """Handle pre-checkout validation"""
    await query.answer(ok=True)


@router.message(lambda m: m.successful_payment)
async def process_successful_payment(message: types.Message) -> None:
    """Handle successful payment"""
    user_id = message.from_user.id
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    try:
        # Extract tier from payload (format: "premium_TIER_USERID")
        tier = payload.split("_")[1]
        
        if tier in config.PREMIUM_TIERS:
            tier_data = config.PREMIUM_TIERS[tier]
            
            # Activate premium
            success = await activate_premium(
                user_id=user_id,
                tier=tier,
                amount_usd=tier_data['price_usd'],
                amount_stars=tier_data['price_stars'],
                payment_id=payment.telegram_payment_charge_id
            )
            
            if success:
                benefits_msg = await get_premium_benefits(user_id)
                await message.answer(f"✅ PREMIUM ACTIVATED! 🎉\n\n{benefits_msg}")
                logger.info(f"Premium activated: {user_id} - {tier}")
            else:
                await message.answer("❌ Error activating premium")
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        await message.answer("❌ Error with your payment")
