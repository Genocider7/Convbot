import discord, mysql.connector, logging

TOKEN=""
DB=None
cursor=None

client=discord.Client()

def err(message):
    logging.basicConfig(filename='convbot.error.log',level=logging.ERROR)
    logging.error(message)

def debug(message):
    logging.basicConfig(filename='convbot.debug.log',level=logging.DEBUG)
    logging.debug(message)

def log(message):
    logging.basicConfig(filename='convbot.log',level=logging.INFO)
    logging.info(message)


@client.event
async def on_message(message):
    global cursor
    if message.author==client.user:
        return
    await message.channel.send("I'm here")
    log(message.channel.guild)

@client.event
async def on_ready():
    log("Logged in as "+str(client.user.name))
    log(client.user.id)

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