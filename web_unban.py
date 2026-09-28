import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsKicked
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError
import logging
from datetime import datetime
from typing import Dict

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

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Global client instance and session storage
client = None
sessions: Dict[str, dict] = {}
unban_progress = {
    'status': 'idle',
    'total': 0,
    'unbanned': 0,
    'failed': 0,
    'current_user': '',
    'logs': []
}


def add_log(message: str):
    """Add log message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    unban_progress['logs'].append(log_entry)
    logger.info(message)
    if len(unban_progress['logs']) > 100:
        unban_progress['logs'].pop(0)


async def get_client():
    """Get or create Telegram client"""
    global client
    if client is None:
        client = TelegramClient('session_' + SECRET_KEY[:10], API_ID, API_HASH)
    return client


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/send_code")
async def send_code(request: Request):
    """Send verification code to phone"""
    try:
        data = await request.json()
        phone = data.get('phone')
        
        if not phone:
            return JSONResponse({'success': False, 'error': 'Phone number required'})
        
        client = await get_client()
        await client.connect()
        
        result = await client.send_code_request(phone)
        
        # Store in memory (in production, use Redis or similar)
        sessions['current'] = {
            'phone': phone,
            'phone_code_hash': result.phone_code_hash
        }
        
        add_log(f"Verification code sent to {phone}")
        
        return JSONResponse({'success': True, 'message': 'Code sent! Check your Telegram.'})
        
    except Exception as e:
        add_log(f"Error sending code: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)})


@app.post("/api/verify_code")
async def verify_code(request: Request):
    """Verify the code and login"""
    try:
        data = await request.json()
        code = data.get('code')
        password = data.get('password', '')
        
        if not code:
            return JSONResponse({'success': False, 'error': 'Code required'})
        
        session = sessions.get('current', {})
        phone = session.get('phone')
        phone_code_hash = session.get('phone_code_hash')
        
        if not phone or not phone_code_hash:
            return JSONResponse({'success': False, 'error': 'Session expired. Please send code again.'})
        
        client = await get_client()
        
        try:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            sessions['current']['logged_in'] = True
            add_log("Successfully logged in!")
            return JSONResponse({'success': True, 'message': 'Logged in successfully!'})
            
        except SessionPasswordNeededError:
            if password:
                await client.sign_in(password=password)
                sessions['current']['logged_in'] = True
                add_log("Successfully logged in with 2FA!")
                return JSONResponse({'success': True, 'message': 'Logged in successfully!'})
            else:
                return JSONResponse({'success': False, 'error': '2FA enabled. Please provide password.', 'need_password': True})
                
        except PhoneCodeInvalidError:
            return JSONResponse({'success': False, 'error': 'Invalid code. Try again.'})
            
    except Exception as e:
        add_log(f"Error verifying code: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)})


@app.get("/api/check_login")
async def check_login():
    """Check if user is logged in"""
    try:
        client = await get_client()
        if await client.is_user_authorized():
            return JSONResponse({'logged_in': True})
        return JSONResponse({'logged_in': False})
    except:
        return JSONResponse({'logged_in': False})


@app.post("/api/unban")
async def start_unban(request: Request):
    """Start unbanning process"""
    global unban_progress
    
    try:
        data = await request.json()
        channel_input = data.get('channel')
        
        if not channel_input:
            return JSONResponse({'success': False, 'error': 'Channel required'})
        
        client = await get_client()
        
        if not await client.is_user_authorized():
            return JSONResponse({'success': False, 'error': 'Not logged in'})
        
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
        
        return JSONResponse({'success': True, 'message': 'Unban process started!'})
        
    except Exception as e:
        add_log(f"Error starting unban: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)})


async def unban_process(channel_input: str):
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
                
                # Simply unban by removing all restrictions
                await client.edit_permissions(
                    channel,
                    user
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


@app.get("/api/progress")
async def get_progress():
    """Get current progress"""
    return JSONResponse(unban_progress)


@app.post("/api/logout")
async def logout():
    """Logout"""
    try:
        global client
        if client:
            await client.log_out()
            client = None
        sessions.clear()
        add_log("Logged out successfully")
        return JSONResponse({'success': True})
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)})


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run(app, host='0.0.0.0', port=port)
