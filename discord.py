import discord
import asyncio
import requests
import json
from discord.ext import commands
from datetime import datetime

class GrokAutoReplyBot:
    def __init__(self):
        self.token = None
        self.channel_id = None
        self.delay = None
        self.grok_api_key = None
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self.setup_commands()

    def setup_commands(self):
        @self.bot.command()
        async def setup(ctx, token: str, channel_id: int, delay: int, grok_api_key: str):
            """Set up the auto-reply bot with configuration"""
            self.token = token
            self.channel_id = channel_id
            self.delay = delay
            self.grok_api_key = grok_api_key
            
            await ctx.send(f"""
            Bot configuration set:
            - Channel ID: {self.channel_id}
            - Reply delay: {self.delay} seconds
            - Grok API: {'Connected' if self.test_grok_connection() else 'Connection failed'}
            Auto-reply system activated in {self.bot.get_channel(self.channel_id).mention}
            """)

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user or str(message.channel.id) != str(self.channel_id):
                return

            # Get reply from Grok API
            grok_reply = self.get_grok_reply(message.content)
            
            # Send reply after delay
            await asyncio.sleep(self.delay)
            await message.reply(grok_reply, mention_author=False)

    def test_grok_connection(self):
        """Test if Grok API key is valid"""
        try:
            test_url = "https://api.groq.com/v1/test"
            response = requests.get(test_url, headers={"Authorization": f"Bearer {self.grok_api_key}"})
            return response.status_code == 200
        except:
            return False

    def get_grok_reply(self, message_content):
        """Get reply from Grok API"""
        headers = {
            "Authorization": f"Bearer {self.grok_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "user", "content": message_content},
            ]
        }
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error getting Grok reply: {e}")
            return "I couldn't generate a response at the moment."

    def run(self):
        """Run the bot with the configured token"""
        if self.token:
            self.bot.run(self.token)
        else:
            print("Error: No token provided. Use !setup command first.")

# How to use:
# 1. Create your bot in Discord Developer Portal and get token
# 2. Get your channel ID by enabling developer mode in Discord and right-clicking the channel
# 3. Get your Groq API key from their platform
# 4. Run the bot with !setup <token> <channel_id> <delay_seconds> <grok_api_key>

if __name__ == "__main__":
    bot = GrokAutoReplyBot()
    
    # Interactive setup if run directly
    print("Grok Auto-Reply Discord Bot Setup")
    bot.token = input("Enter Discord bot token: ")
    bot.channel_id = int(input("Enter channel ID to monitor: "))
    bot.delay = int(input("Enter reply delay in seconds: "))
    bot.grok_api_key = input("Enter Groq API key: ")
    
    print("Starting bot...")
    bot.run()
