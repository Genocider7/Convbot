import discord, mysql.connector, sys

TOKEN=""
DB=None
cursor=None
sys.stdout=open("convbot.log","a")
sys.stderr=open("convbot.error.log","a")
client=discord.Client()

@client.event
async def on_message(message):
    global cursor
    if message.author==client.user:
        return
    await message.channel.send("I'm here")
    print(message.channel.guild)
    print(2/0)

@client.event
async def on_ready():
    print("Logged in as "+str(client.user.name))
    print(client.user.id)

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