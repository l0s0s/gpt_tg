import praw
from telegram.ext import ApplicationBuilder
import asyncio
from os import environ
from openai import OpenAI
import time

telegram_channel_id = environ.get('TELEGRAM_CHANNEL_ID')

reddit = praw.Reddit(
    client_id=environ.get('REDDIT_CLIENT_ID'),
    client_secret=environ.get('REDDIT_CLIENT_SECRET'),
    user_agent='python:reddit-bot:v1.0',
)

client = OpenAI(
    api_key=environ.get("OPENAI_API_KEY"),
)

app = ApplicationBuilder().token(environ.get('TELEGRAM_BOT_TOKEN')).build()

def is_image(url):
    return url.endswith(('.jpg', '.jpeg', '.png', '.gif'))

async def fetch_and_send_posts():
    subreddit = reddit.subreddit(environ.get('SUBREDDIT'))
    for submission in subreddit.top(limit=5, time_filter="hour"):
        if submission.over_18 and not is_image(submission.url):
            continue
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": '''
                            Translate the following text from English to Russian.
                            Expand the text, adding more detail and context to make it more informative and engaging.
                            Optimize the message for Telegram by keeping key information concise but appealing.
                            Add relevant emojis to make the message more lively and interesting.
                            Keep the message short and concise (no longer than 600 characters).
                            Always include a bold headline using single asterisks (*) for the title.
                            Use only single asterisks (*) for bold text (no other markdown formatting).
                             '''},
                            {"type": "text", "text": submission.title},
                        ],
                    }
                ],
            )
        
            await app.bot.send_photo(chat_id=telegram_channel_id, photo=submission.url, caption=response.choices[0].message.content, parse_mode='Markdown')
        except Exception as e:
            print(e)
            continue
        
            
        
if __name__ == "__main__":
    time.sleep(300)
    asyncio.run(fetch_and_send_posts())
