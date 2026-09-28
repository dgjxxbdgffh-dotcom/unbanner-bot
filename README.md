# 🔓 Telegram Mass Unban Tool

Automatically unban **ALL** banned users from your Telegram channel or group with a single command!

## ✨ Features

- ✅ **Automatically fetches ALL banned users** (no manual list needed!)
- ✅ **Mass unban** with one command
- ✅ **Real-time progress** tracking
- ✅ **Flood protection** with automatic retry
- ✅ Works with any channel you're admin in
- ✅ Uses official Telegram User API (Telethon)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Phone Number

Open `unban_bot.py` and set your phone number:

```python
PHONE_NUMBER = '+1234567890'  # Replace with your number
```

**Note:** Your API credentials are already configured!
- API_ID: `33325009`
- API_HASH: `3ef83055e590c94d0c4572dc094771f4`

### 3. Run the Tool

```bash
python unban_bot.py
```

### 4. First Time Only

- Enter the verification code Telegram sends you
- If you have 2FA, enter your password

### 5. Unban Users

- Enter your channel username (e.g., `@mychannel`)
- Or channel link (e.g., `https://t.me/mychannel`)
- Confirm when prompted
- **Done!** The tool unbans everyone automatically

## 📖 Detailed Setup Guide

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete step-by-step instructions.

## 🎯 How It Works

1. **Connects** to Telegram using your account (via API)
2. **Fetches** all banned users from the channel
3. **Unbans** them one by one with progress tracking
4. **Handles** rate limits automatically

## ✅ Advantages Over Bot API

Traditional Telegram bots **cannot** retrieve the list of banned users. This tool uses the **User API** which gives full access:

| Feature | Bot API ❌ | User API ✅ |
|---------|-----------|------------|
| Get banned users list | ❌ No | ✅ Yes |
| Requires user IDs | ❌ Yes | ✅ No |
| Automatic mass unban | ❌ No | ✅ Yes |
| Real channel control | ❌ Limited | ✅ Full |

## 🔐 Security

- Your credentials stay on **YOUR computer only**
- Session file stores your login securely
- Never share your `API_HASH` or `.session` file!

## 📋 Requirements

- Python 3.7 or higher
- You must be an **admin** in the channel
- You must have **ban/unban permissions**

## 🛠️ Troubleshooting

**"Could not find channel"**
- Make sure you're an admin with proper permissions
- Try using the channel ID instead

**"FloodWaitError"**
- Telegram is rate-limiting (normal for large channels)
- The tool automatically waits and continues

**"Phone number required"**
- Set your `PHONE_NUMBER` in `unban_bot.py`

## 📁 Project Files

- `unban_bot.py` - Main program
- `requirements.txt` - Python dependencies
- `SETUP_GUIDE.md` - Detailed setup instructions
- `README.md` - This file

## 💡 Tips

- Run this during off-peak hours for large channels
- The tool shows real-time progress
- You can close and restart anytime (session is saved)
- Works for both channels and supergroups

## 🎉 Ready to Use!

Your API credentials are already configured. Just add your phone number and run:

```bash
python unban_bot.py
```

**Happy unbanning! 🚀**
