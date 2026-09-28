import asyncio
import os
from quart import Quart, render_template, request, jsonify, session
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsKicked
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
API_ID = int(os.environ.get('API_ID', '33325009'))
API_HASH = os.environ.get('API_HASH', '3ef83055e590c94d0c4572dc094771f4')
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

app = Quart(__name__)
app.secret_key = SECRET_KEY

# Global client instance
client = None
unban_progress = {
    'status': 'idle',
    'total': 0,
    'unbanned': 0,
    'failed': 0,
    'current_user': '',
    'logs': []
}


def add_log(message):
    """Add log message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    unban_progress['logs'].append(log_entry)
    logger.info(message)
    # Keep only last 100 logs
    if len(unban_progress['logs']) > 100:
        unban_progress['logs'].pop(0)


async def get_client():
    """Get or create Telegram client"""
    global client
    if client is None:
        client = TelegramClient('session_' + SECRET_KEY[:10], API_ID, API_HASH)
    return client


@app.route('/')
async def index():
    """Main page"""
    return await render_template('index.html')


@app.route('/api/send_code', methods=['POST'])
async def send_code():
    """Send verification code to phone"""
    try:
        data = await request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required'})
        
        client = await get_client()
        await client.connect()
        
        result = await client.send_code_request(phone)
        session['phone'] = phone
        session['phone_code_hash'] = result.phone_code_hash
        
        add_log(f"Verification code sent to {phone}")
        
        return jsonify({'success': True, 'message': 'Code sent! Check your Telegram.'})
        
    except Exception as e:
        add_log(f"Error sending code: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/verify_code', methods=['POST'])
async def verify_code():
    """Verify the code and login"""
    try:
        data = await request.get_json()
        code = data.get('code')
        password = data.get('password', '')
        
        if not code:
            return jsonify({'success': False, 'error': 'Code required'})
        
        phone = session.get('phone')
        phone_code_hash = session.get('phone_code_hash')
        
        if not phone or not phone_code_hash:
            return jsonify({'success': False, 'error': 'Session expired. Please send code again.'})
        
        client = await get_client()
        
        try:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            session['logged_in'] = True
            add_log("Successfully logged in!")
            return jsonify({'success': True, 'message': 'Logged in successfully!'})
            
        except SessionPasswordNeededError:
            if password:
                await client.sign_in(password=password)
                session['logged_in'] = True
                add_log("Successfully logged in with 2FA!")
                return jsonify({'success': True, 'message': 'Logged in successfully!'})
            else:
                return jsonify({'success': False, 'error': '2FA enabled. Please provide password.', 'need_password': True})
                
        except PhoneCodeInvalidError:
            return jsonify({'success': False, 'error': 'Invalid code. Try again.'})
            
    except Exception as e:
        add_log(f"Error verifying code: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/check_login', methods=['GET'])
async def check_login():
    """Check if user is logged in"""
    try:
        client = await get_client()
        if await client.is_user_authorized():
            return jsonify({'logged_in': True})
        return jsonify({'logged_in': False})
    except:
        return jsonify({'logged_in': False})


@app.route('/api/unban', methods=['POST'])
async def start_unban():
    """Start unbanning process"""
    global unban_progress
    
    try:
        data = await request.get_json()
        channel_input = data.get('channel')
        
        if not channel_input:
            return jsonify({'success': False, 'error': 'Channel required'})
        
        client = await get_client()
        
        if not await client.is_user_authorized():
            return jsonify({'success': False, 'error': 'Not logged in'})
        
        # Reset progress
        unban_progress = {
            'status': 'running',
            'total': 0,
            'unbanned': 0,
            'failed': 0,
            'current_user': '',
            'logs': unban_progress['logs']
        }
        
        add_log(f"Starting unban process for: {channel_input}")
        
        # Start unbanning in background
        asyncio.create_task(unban_process(channel_input))
        
        return jsonify({'success': True, 'message': 'Unban process started!'})
        
    except Exception as e:
        add_log(f"Error starting unban: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


async def unban_process(channel_input):
    """Background task to unban users"""
    global unban_progress
    
    try:
        client = await get_client()
        
        # Get channel
        add_log(f"Fetching channel: {channel_input}")
        channel = await client.get_entity(channel_input)
        add_log(f"Found channel: {channel.title}")
        
        # Get banned users
        add_log("Fetching banned users...")
        banned_users = []
        offset = 0
        limit = 200
        
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
                add_log(f"Fetched {len(banned_users)} banned users so far...")
                
                if len(participants.users) < limit:
                    break
                    
            except Exception as e:
                add_log(f"Error fetching banned users: {e}")
                break
        
        unban_progress['total'] = len(banned_users)
        
        if not banned_users:
            add_log("No banned users found!")
            unban_progress['status'] = 'completed'
            return
        
        add_log(f"Found {len(banned_users)} banned users. Starting unban...")
        
        # Unban each user
        for user in banned_users:
            try:
                unban_progress['current_user'] = f"{user.first_name or 'User'} (ID: {user.id})"
                
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
                    send_polls=True
                )
                
                unban_progress['unbanned'] += 1
                add_log(f"✅ Unbanned: {unban_progress['current_user']} ({unban_progress['unbanned']}/{unban_progress['total']})")
                
                await asyncio.sleep(0.5)
                
            except FloodWaitError as e:
                add_log(f"⏳ Flood wait: {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                
            except Exception as e:
                unban_progress['failed'] += 1
                add_log(f"❌ Failed: {unban_progress['current_user']} - {str(e)}")
        
        unban_progress['status'] = 'completed'
        add_log(f"✅ COMPLETED! Unbanned: {unban_progress['unbanned']}, Failed: {unban_progress['failed']}")
        
    except Exception as e:
        unban_progress['status'] = 'error'
        add_log(f"❌ Error: {str(e)}")


@app.route('/api/progress', methods=['GET'])
async def get_progress():
    """Get current progress"""
    return jsonify(unban_progress)


@app.route('/api/logout', methods=['POST'])
async def logout():
    """Logout"""
    try:
        global client
        if client:
            await client.log_out()
            client = None
        session.clear()
        add_log("Logged out successfully")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
