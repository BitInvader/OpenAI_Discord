import os
import json
import openai
import discord
import requests
from discord import Intents
from discord.ext import commands

# Load API keys from config.json file
with open("config.json") as f:
    config = json.load(f)

openai_api_key = config["OPENAI_API_KEY"]
discord_bot_token = config["DISCORD_BOT_TOKEN"]
giphy_api_key = config["GIPHY_API_KEY"]

# Initialize OpenAI API client
openai.api_key = openai_api_key

# Create a Discord bot instance with the default intents and message content intent
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the bot is mentioned in the message
    if bot.user in message.mentions:
        # Remove the bot mention and strip extra whitespaces
        question = message.content.replace(f'<@!{bot.user.id}>', '').strip()

        # Call OpenAI API to get an answer for the question
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"{question}\n\nAnswer:",
            temperature=0.5,
            max_tokens=50,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        answer = response.choices[0].text.strip()

        # Send the answer to the Discord chat
        await message.channel.send(answer)

    # Allow commands processing
    await bot.process_commands(message)

@bot.command()
async def gif(ctx, *, search_query):
    url = f"http://api.giphy.com/v1/gifs/search?api_key={giphy_api_key}&q={search_query}&limit=1"
    response = requests.get(url)
    data = response.json()

    if data["data"]:
        gif_url = data["data"][0]["images"]["original"]["url"]
        await ctx.send(gif_url)
    else:
        await ctx.send("No GIFs found.")

# Run the bot
bot.run(discord_bot_token)
