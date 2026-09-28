import logging
from telegram import Update, ChatMemberUpdated
from telegram.ext import Application, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"


async def unban_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unban all users when the bot is added to a channel as admin"""
    
    # Get the chat member update
    result = update.my_chat_member
    
    if result is None:
        return
    
    # Check if the bot was just made an admin
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    
    chat = result.chat
    
    # If bot became an admin
    if (old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.MEMBER] and 
        new_status == ChatMemberStatus.ADMINISTRATOR):
        
        logger.info(f"Bot was made admin in chat: {chat.title} (ID: {chat.id})")
        
        try:
            # Get all banned users (this requires the bot to have the necessary permissions)
            banned_count = 0
            
            # Note: Telegram doesn't provide a direct way to list all banned users
            # This is a limitation of the Telegram Bot API
            # The bot will need to store banned user IDs or you'll need to provide them
            
            await context.bot.send_message(
                chat_id=chat.id,
                text="🤖 Bot activated as admin! Ready to unban users.\n\n"
                     "⚠️ Note: Due to Telegram API limitations, I cannot automatically "
                     "retrieve the list of banned users. Please use /unbanall command "
                     "with the list of user IDs, or use the alternative method below."
            )
            
            logger.info(f"Sent welcome message to chat: {chat.id}")
            
        except Exception as e:
            logger.error(f"Error processing chat {chat.id}: {e}")


async def unban_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command to unban all users in the chat"""
    
    if update.effective_chat.type not in ['group', 'supergroup', 'channel']:
        await update.message.reply_text("This command only works in groups or channels!")
        return
    
    # Check if the user is an admin
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await update.message.reply_text("Only admins can use this command!")
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return
    
    await update.message.reply_text(
        "🔓 Starting to unban all users...\n\n"
        "⚠️ Important: Please provide the user IDs to unban, separated by spaces.\n"
        "Example: /unbanall 123456789 987654321\n\n"
        "Or if you have ban logs, I can process them!"
    )
    
    # If user IDs are provided
    if context.args:
        unbanned_count = 0
        failed_count = 0
        
        for user_id_str in context.args:
            try:
                user_id = int(user_id_str)
                await context.bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
                unbanned_count += 1
                logger.info(f"Unbanned user {user_id} from chat {chat_id}")
            except ValueError:
                logger.warning(f"Invalid user ID: {user_id_str}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Failed to unban user {user_id_str}: {e}")
                failed_count += 1
        
        await update.message.reply_text(
            f"✅ Unbanning complete!\n"
            f"Unbanned: {unbanned_count}\n"
            f"Failed: {failed_count}"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors"""
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """Start the bot"""
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set your bot token in the BOT_TOKEN variable!")
        print("Get your token from @BotFather on Telegram")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(ChatMemberHandler(unban_all_users, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started successfully! Add it to your channel as an admin.")
    print("🤖 Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
