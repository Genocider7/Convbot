import discord, mysql.connector, logging

TOKEN=""
DB=None
cursor=None

logging.basicConfig(filename='convbot.debug.log',level=logging.DEBUG)
logging.basicConfig(filename='convbot.log',level=logging.INFO)
logging.basicConfig(filename='convbot.error.log',level=logging.ERROR)
client=discord.Client()

@client.event
async def on_message(message):
    global cursor
    if message.author==client.user:
        return
    await message.channel.send("I'm here")
    logging.info(message.channel.guild)

@client.event
async def on_ready():
    logging.info("Logged in as "+str(client.user.name))
    logging.info(client.user.id)

secretfile = open("TOKEN","r")
TOKEN = secretfile.read()
secretfile.close()
DB = mysql.connector.connect(
    host = 'localhost',
    user = 'convbot',
    password = '&G"Pt_l1+wvbbPBS',
    database = 'conversation_botDB'
)

cursor = DB.cursor()

client.run(TOKEN)