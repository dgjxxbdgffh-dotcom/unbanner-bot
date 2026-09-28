import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsKicked, ChatBannedRights
from telethon.errors import FloodWaitError
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your API credentials from https://my.telegram.org
API_ID = 33325009
API_HASH = '3ef83055e590c94d0c4572dc094771f4'

# Your phone number (with country code, e.g., +1234567890)
PHONE_NUMBER = 'YOUR_PHONE_NUMBER_HERE'

# Initialize the client
client = TelegramClient('unban_session', API_ID, API_HASH)


async def get_all_banned_users(channel):
    """Get all banned users from a channel"""
    banned_users = []
    offset = 0
    limit = 200
    
    logger.info(f"Fetching banned users from {channel.title}...")
    
    while True:
        try:
            participants = await client(GetParticipantsRequest(
                channel,
                ChannelParticipantsKicked(''),
                offset,
                limit,
                hash=0
            ))
            
            if not participants.users:
                break
            
            banned_users.extend(participants.users)
            offset += len(participants.users)
            
            logger.info(f"Fetched {len(banned_users)} banned users so far...")
            
            if len(participants.users) < limit:
                break
                
        except Exception as e:
            logger.error(f"Error fetching banned users: {e}")
            break
    
    return banned_users


async def unban_all_users(channel):
    """Unban all users in a channel"""
    try:
        # Get all banned users
        banned_users = await get_all_banned_users(channel)
        
        if not banned_users:
            logger.info("No banned users found!")
            return 0
        
        logger.info(f"Found {len(banned_users)} banned users. Starting to unban...")
        
        unbanned_count = 0
        failed_count = 0
        
        # Unban each user
        for user in banned_users:
            try:
                # Unban by setting no restrictions
                await client.edit_permissions(
                    channel,
                    user,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True,
                    send_polls=True,
                    change_info=False,
                    invite_users=False,
                    pin_messages=False
                )
                
                unbanned_count += 1
                logger.info(f"✅ Unbanned: {user.first_name} (ID: {user.id}) - Total: {unbanned_count}/{len(banned_users)}")
                
                # Small delay to avoid flood limits
                await asyncio.sleep(0.5)
                
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood wait! Sleeping for {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
                # Retry this user
                try:
                    await client.edit_permissions(channel, user)
                    unbanned_count += 1
                except Exception as retry_error:
                    logger.error(f"❌ Failed to unban {user.first_name} even after retry: {retry_error}")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to unban {user.first_name} (ID: {user.id}): {e}")
                failed_count += 1
        
        logger.info(f"\n{'='*50}")
        logger.info(f"✅ UNBANNING COMPLETE!")
        logger.info(f"Total Unbanned: {unbanned_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"{'='*50}\n")
        
        return unbanned_count
        
    except Exception as e:
        logger.error(f"Error in unban process: {e}")
        return 0


async def main():
    """Main function"""
    
    # Check if phone number is set
    if PHONE_NUMBER == 'YOUR_PHONE_NUMBER_HERE':
        print("❌ ERROR: Please set your phone number in the PHONE_NUMBER variable!")
        print("Example: PHONE_NUMBER = '+1234567890'")
        return
    
    # Start the client
    await client.start(phone=PHONE_NUMBER)
    
    print("\n" + "="*60)
    print("🤖 TELEGRAM MASS UNBAN TOOL")
    print("="*60 + "\n")
    
    # Get user input
    print("Please enter the channel/group information:")
    print("You can use:")
    print("  - Channel username (e.g., @mychannel)")
    print("  - Channel invite link (e.g., https://t.me/mychannel)")
    print("  - Channel ID (e.g., -1001234567890)")
    
    channel_input = input("\nEnter channel: ").strip()
    
    if not channel_input:
        print("❌ No channel provided!")
        return
    
    try:
        # Get the channel entity
        channel = await client.get_entity(channel_input)
        
        print(f"\n✅ Found channel: {channel.title}")
        print(f"Channel ID: {channel.id}")
        
        # Confirm before proceeding
        confirm = input("\n⚠️  Do you want to unban ALL users in this channel? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled!")
            return
        
        # Start unbanning
        print("\n🔓 Starting mass unban process...\n")
        await unban_all_users(channel)
        
    except ValueError:
        print(f"❌ Could not find channel: {channel_input}")
        print("Make sure you have access to this channel and you're an admin!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("\n✅ Done! You can close this program now.")


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
