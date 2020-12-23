import discord, mysql.connector, logging

TOKEN=""
DB=None
cursor=None

logging.basicConfig(filename='convbot.log',
filemode='a',
format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
datefmt='%H:%M:%S',
level=logging.CRITICAL)
client=discord.Client()

@client.event
async def on_message(message):
    global cursor
    if message.author==client.user:
        return
    await message.channel.send("I'm here")
    logging.info(str(message.channel.guild))
    print(2/0)

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