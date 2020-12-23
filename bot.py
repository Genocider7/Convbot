import discord, mysql.connector

TOKEN=""
MYSQLPASSWD=""
DB=None

client=discord.Client()

@client.event
async def on_message(message):
    global cursor
    if message.author==client.user:
        return
    await message.channel.send("I'm here")
    print(message.channel.guild)

@client.event
async def on_ready():
    print("Logged in as ",client.user.name)
    print(client.user.id)

secretfile = open("TOKEN","r")
TOKEN = secretfile.read()
secretfile.close()
secretfile = open("MYSQLPASSWD","r")
MYSQLPASSWD = secretfile.read()
secretfile.close()
DB = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = MYSQLPASSWD,
)

cursor = DB.cursor()

client.run(TOKEN)