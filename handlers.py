import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

# NOTE: These channel IDs are now expected to be STRINGS (usernames or links)
from config import (
    MAIN_CHANNEL,
    BACKUP_CHANNEL,
    PRIVATE_CHANNEL,
    MOBILE_API,
    GST_API,
    IFSC_API,
    PINCODE_API,
    RC_API, 
    IMEI_API 
)

from keyboards import (
    join_channels_kb,
    main_menu_kb,
    lookup_options_kb,
    ask_input_kb,
    quick_back_kb
)

from database import (
    create_user,
    get_user_credits,
    decrease_credit,
    add_referral
)

from utils import validate_input, clean_json # Import both utility functions

logger = logging.getLogger(__name__)

# -------------------------------------------------
# CHECK USER JOINED 3 CHANNELS (Uses String Usernames/Links)
# -------------------------------------------------
async def is_joined_all(bot, user_id):
    """Checks if a user has joined required channels (MAIN + BACKUP only)."""
    try:
        status_ok = ("member", "administrator", "creator")
        
        m1 = await bot.get_chat_member(MAIN_CHANNEL, user_id)
        m2 = await bot.get_chat_member(BACKUP_CHANNEL, user_id)
        
        return (
            m1.status in status_ok and
            m2.status in status_ok
        )
        
    except Exception as e:
        logger.error(f"Channel check failed for user {user_id}: {e}")
        return False
# -------------------------------------------------
# /start COMMAND
# -------------------------------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = ctx.args

    # -------------- REFERRAL ----------------  
    ref = None  
    if args and args[0].isdigit():  
        ref = int(args[0])  

    # Create user and check if they are new
    created = create_user(user.id, user.username, user.first_name)  

    if created and ref and ref != user.id:  
        add_referral(ref, user.id)  
        try:  
            # Notify referrer of new referral and credit
            await ctx.bot.send_message(  
                chat_id=ref,  
                text="🎉 *New Referral!* Someone installed using your link.\nYou received +1 Credit 💳*",  
                parse_mode="Markdown"  
            )  
        except:  
            pass  

    # -------------- CHANNEL CHECK ----------------  
    if not await is_joined_all(ctx.bot, user.id):  
        await update.message.reply_text(  
            "🔐 *Please join all required channels to unlock the bot:*",  
            reply_markup=join_channels_kb(),  
            parse_mode="Markdown"  
        )  
        return  

    # -------------- WELCOME ----------------  
    await update.message.reply_text(  
        f"👋 Welcome to **Nagi OSINT PRO**\nSelect any tool below ⬇️",  
        reply_markup=main_menu_kb(),  
        parse_mode="Markdown"  
    )

# -------------------------------------------------
# VERIFY JOIN BUTTON
# -------------------------------------------------
async def verify_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if await is_joined_all(ctx.bot, q.from_user.id):  
        try:
            # Try to delete the original message for a cleaner chat
            await q.message.delete()
        except:
            pass
            
        await ctx.bot.send_message( 
            chat_id=q.from_user.id,
            text="✅ Verified! Access Unlocked.",  
            reply_markup=main_menu_kb(),  
            parse_mode="Markdown"  
        )  
    else:  
        await q.message.reply_text(  
            "❌ Please join all channels first.",  
            reply_markup=join_channels_kb()  
        )

# -------------------------------------------------
# BUTTON HANDLER
# -------------------------------------------------
async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    if data == "lookup_options":  
        await q.message.edit_text("🔍 Select Lookup Type:", reply_markup=lookup_options_kb(), parse_mode="Markdown")  

    elif data == "help_guide":  
        await q.message.edit_text(  
            "📘 *HELP GUIDE*\n\nThis bot supports auto-detection of:\n\n"
            "• 10-digit mobile number\n"
            "• 15-digit GST number\n"
            "• 11-char IFSC Code\n"
            "• 6-digit Pincode\n"
            "• Vehicle Number\n"
            "• 15-digit IMEI Number\n\n"
            "Just click any tool or simply send your query! Bot auto fetches LIVE data.",  
            reply_markup=quick_back_kb(),  
            parse_mode="Markdown"  
        )  

    elif data == "support":  
        await q.message.edit_text(  
            "🛠 Support: @AbdulBotz",  
            reply_markup=quick_back_kb(),  
            parse_mode="Markdown"  
        )  

    elif data == "quick_search":  
        await q.message.edit_text(  
            "⚡ *QUICK SEARCH*\n\nSIMPLY SEND ANY OF THESE:\n\n"
            "`9876543210` - MOBILE\n"
            "`09AAYFK4129N1ZF` - GST\n"
            "`ICIC0001206` - IFSC\n"
            "`110001` - PINCODE\n"
            "`MH12DE1433` - VEHICLE\n"
            "`123456789012345` - IMEI",
            reply_markup=quick_back_kb(),  
            parse_mode="Markdown"  
        )  

    # -------- SELECT LOOKUP TYPE ----------  
    lookup_modes = {  
        "mobile_lookup": "📱 Send Mobile Number (10 digits):",  
        "gst_lookup": "🏢 Send GST Number (15 digits):",  
        "ifsc_lookup": "🏦 Send IFSC Code (11 characters):",  
        "pincode_lookup": "📮 Send Pincode (6 digits):",  
        "vehicle_lookup": "🚗 Send RC Number (e.g., MH12DE1433):",  
        "imei_lookup": "🧾 Send IMEI Number (15 digits):" 
    }  

    if data in lookup_modes:  
        ctx.user_data["mode"] = data  
        await q.message.edit_text(  
            lookup_modes[data],  
            reply_markup=ask_input_kb(),  
            parse_mode="Markdown"  
        )  
        return  

    if data == "back_home":  
        await q.message.edit_text("🏠 Main Menu:", reply_markup=main_menu_kb(), parse_mode="Markdown")

# -------------------------------------------------
# PROCESS USER MESSAGE
# -------------------------------------------------
async def process_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message.text.strip()

    # JOIN CHECK  
    if not await is_joined_all(ctx.bot, user.id):  
        await update.message.reply_text(  
            "🔐 Join all channels first.",  
            reply_markup=join_channels_kb()  
        )  
        return  

    # Check if a lookup mode has been selected (e.g., by clicking a button)
    if "mode" not in ctx.user_data:  
        await update.message.reply_text(
            "Please select a lookup option first from the Main Menu.",
            reply_markup=main_menu_kb()
        )
        return
            
    mode = ctx.user_data["mode"]
    
    # --- Input Validation (CRITICAL FIX) ---
    lookup_type = mode.replace("_lookup", "")
    if not validate_input(lookup_type, msg):
        await update.message.reply_text(
            f"❌ Invalid format for {lookup_type.upper()}! Please send a valid input.",
            reply_markup=ask_input_kb()
        )
        return

    # --------- CREDIT CHECK ----------  
    credits = get_user_credits(user.id)  
    if credits <= 0:  
        await update.message.reply_text(  
            "❌ *No credits left!*\nUse /start → Refer & Earn",  
            parse_mode="Markdown"  
        )  
        return  

    decrease_credit(user.id)  

    status_message = await update.message.reply_text("⏳ Fetching data…")  

    # --------- API MAPPING ----------  
    api_map = {  
        "mobile_lookup": MOBILE_API + msg,  
        "gst_lookup": GST_API + msg,  
        "ifsc_lookup": IFSC_API + msg,  
        "pincode_lookup": PINCODE_API + msg,  
        "vehicle_lookup": RC_API + msg, 
        "imei_lookup": IMEI_API + msg  
    }  

    url = api_map.get(mode)  

    # --------- CALL API ----------  
    data = None
    try:  
        async with aiohttp.ClientSession() as session:  
            async with session.get(url, timeout=15) as r: 
                if r.status == 200:
                    data = await r.json()  
                else:
                    await status_message.edit_text(f"⚠️ API returned status code {r.status}. Check API URL or input.", parse_mode="Markdown")
                    return
    except Exception as e:
        await status_message.edit_text("⚠️ API Error or Timeout. Try again.", parse_mode="Markdown")  
        logger.error(f"API call failed for {mode}: {e}")
        return  

    # ---------- CLEAN OUTPUT ----------  
    formatted_data = clean_json(data)
    
    formatted = f"📄 *OSINT Result*\n\n```json\n{formatted_data}\n```\n\n" \
                f"💳 Credits remaining: *{get_user_credits(user.id)}*"

    await status_message.edit_text( 
        formatted,  
        parse_mode="Markdown"
    )
    
    # Clear the mode context after successful use
    del ctx.user_data["mode"]
    
