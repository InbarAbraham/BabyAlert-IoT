import requests
def send_telegram_alert(message: str):
    bot_token = 'your_bot_token_here'
    chat_id = 'your_chat_id'  
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': message
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"❌ Failed to send Telegram message: {response.text}")
        else:
            print("✅ Telegram alert sent!")
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")

send_telegram_alert("🚨 ALERT: A kid was detected inside the locked car!")