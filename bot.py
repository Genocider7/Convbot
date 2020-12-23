import discord, mysql.connector, sys
from datetime import datetime
TOKEN=""
DB=None
cursor=None
sys.stdout=open("convbot.log","a")
sys.stderr=open("convbot.error.log","a")
client=discord.Client()

def select(query):
    global cursor
    cursor.execute(query)
    return cursor.fetchall()
    
def select_one(query):
    global cursor
    cursor.execute(query)
    return cursor.fetchone()

def insert(table, fields, values):
    global cursor, DB
    if len(fields)==0:
        return False
    if len(fields)!=len(values):
        return False
    sql = "INSER INTO %s (%s"
    for i in range(len(fields)-1):
        sql = sql+", %s"
    sql = sql + ") VALUES (\"%s\""
    for i in range(len(fields)-1):
        sql = sql+", \"%s\""
    sql = sql + ")"
    cursor.execute(sql, table, fields, values)
    DB.commit()
    return True

@client.event
async def on_message(message):
    global cursor
    cursor = DB.cursor()
    if message.author==client.user:
        return
    mes = message.content.lower()
    
    response = select_one("SELECT response FROM conversations WHERE LOWER(message) = \""+mes+"\" AND server = \"ALL\"")
    if not response:
        if str(message.channel.type) == "private":
            await message.channel.send("Ten bot działa tylko na serwerach, nie DMach")
            return
    else:
        await message.channel.send(response[0])
        return

    response = select_one("SELECT response FROM conversations WHERE LOWER(message) = \""+mes+"\" AND server = \""+str(message.channel.guild.id)+"\"")
    if response:
        await message.channel.send(response[0])
        return

@client.event
async def on_ready():
    now=datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S"), " - Logged in as ", client.user.name, " - ", client.user.id)
    await client.change_presence(status=discord.Status.online, activity=discord.Game("c!help"))

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