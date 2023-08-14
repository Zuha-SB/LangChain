import os
from dotenv import load_dotenv
import openai
import discord

# Add variables
load_dotenv()

# Add intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

# Get token and key
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

# Send prompt to openai and get response
def get_response(msg):
    response = openai.Completion.create(
        api_key = OPENAI_KEY,
        model = "text-davinci-003",
        prompt = msg,
        temperature = 0.9, # higher temp = more creative AI
        max_tokens = 100,
    )
    return response

# When ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# When a message is sent
@client.event
async def on_message(message):

    # If the message was by the bot, do nothing
    if message.author == client.user:
        return 

    # Otherwise, get and send response   
    response = get_response(message.content)
    await message.channel.send(response["choices"][0]["text"])

    return

# Start
client.run(BOT_TOKEN)
