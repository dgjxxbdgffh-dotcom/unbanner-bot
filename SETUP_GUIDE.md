# 🚀 Complete Setup Guide - Telegram Mass Unban Tool

## ✅ What This Tool Does

This tool will **automatically unban ALL banned users** from your Telegram channel or group. No manual work needed!

---

## 📋 Step-by-Step Setup

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. Install it (make sure to check "Add Python to PATH" during installation)
3. Open Command Prompt or PowerShell and verify:
   ```bash
   python --version
   ```

### Step 2: Install Telethon Library

Open your terminal/command prompt and run:

```bash
pip install -r requirements.txt
```

Or directly:

```bash
pip install telethon
```

### Step 3: Configure Your API Credentials

1. Open `unban_bot.py` in any text editor
2. Find these lines near the top:

```python
API_ID = 33325009
API_HASH = '3ef83055e590c94d0c4572dc094771f4'
```

**✅ These are already filled in with your credentials!**

3. Now find this line:

```python
PHONE_NUMBER = 'YOUR_PHONE_NUMBER_HERE'
```

4. Replace it with your phone number (include country code):

```python
PHONE_NUMBER = '+1234567890'  # Example: +1 for USA, +44 for UK, etc.
```

### Step 4: Run the Tool

1. Open terminal/command prompt in the project folder
2. Run:

```bash
python unban_bot.py
```

3. **First time only**: Telegram will send you a verification code
   - Enter the code when prompted
   - If you have 2FA enabled, enter your password too

4. Enter your channel information:
   - Channel username (e.g., `@mychannel`)
   - Channel invite link (e.g., `https://t.me/mychannel`)
   - Or channel ID (e.g., `-1001234567890`)

5. Confirm when asked

6. **Sit back and watch!** The tool will:
   - Fetch all banned users
   - Unban them one by one
   - Show progress in real-time

---

## 🎯 Example Usage

```
🤖 TELEGRAM MASS UNBAN TOOL
============================================================

Please enter the channel/group information:
You can use:
  - Channel username (e.g., @mychannel)
  - Channel invite link (e.g., https://t.me/mychannel)
  - Channel ID (e.g., -1001234567890)

Enter channel: @mychannel

✅ Found channel: My Awesome Channel
Channel ID: -1001234567890

⚠️  Do you want to unban ALL users in this channel? (yes/no): yes

🔓 Starting mass unban process...

Fetching banned users from My Awesome Channel...
Fetched 150 banned users so far...
Found 150 banned users. Starting to unban...
✅ Unbanned: John Doe (ID: 123456789) - Total: 1/150
✅ Unbanned: Jane Smith (ID: 987654321) - Total: 2/150
...
```

---

## 📝 Important Notes

### ✅ Advantages Over Bot API:
- **Automatically retrieves ALL banned users** (Bot API can't do this!)
- No need to manually provide user IDs
- Full control over your channel
- Works with any channel you're admin in

### ⚠️ Requirements:
- You must be an **admin** in the channel
- You must have **ban/unban permissions** in the channel
- Your account must be logged in (verification code on first run)

### 🔐 Security:
- Your API credentials are stored only on YOUR computer
- The session file (`unban_session.session`) stores your login
- Never share your API_HASH or session file with anyone!

---

## 🛠️ Troubleshooting

**Problem: "Could not find channel"**
- Make sure you're an admin in the channel
- Try using the channel ID instead of username
- Check that the channel exists and is accessible

**Problem: "FloodWaitError"**
- Telegram is rate-limiting you
- The tool will automatically wait and retry
- This is normal for large channels

**Problem: "Phone number required"**
- You forgot to set your phone number in the code
- Open `unban_bot.py` and set `PHONE_NUMBER`

**Problem: "Permission denied"**
- Make sure you have ban/unban permissions in the channel
- Check that you're an admin, not just a member

---

## 📞 Need Help?

If something doesn't work:
1. Check the error message in the console
2. Make sure all steps above are completed
3. Verify your admin permissions in the channel

---

## 🎉 That's It!

Your credentials are already configured:
- ✅ API_ID: 33325009
- ✅ API_HASH: 3ef83055e590c94d0c4572dc094771f4
- ⏳ Just add your phone number and run!

**Happy unbanning! 🔓**
