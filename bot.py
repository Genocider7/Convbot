import discord, mysql.connector, sys
from datetime import datetime
TOKEN=""
DB=None
cursor=None
sys.stdout=open("convbot.log","a")
sys.stderr=open("convbot.error.log","a")
client=discord.Client()

def has_role(user, role):
    for user_role in user.roles:
        if role.id == user_role.id:
            return True
    return False

def connect_db():
    global DB, cursor
    DB = mysql.connector.connect(
    host = 'localhost',
    user = 'convbot',
    password = '&G"Pt_l1+wvbbPBS',
    database = 'conversation_botDB'
    )
    cursor = DB.cursor()

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
    sql = "INSERT INTO "+table+" ("+fields[0]
    for i in range(len(fields)-1):
        sql = sql+", "+fields[i+1]
    sql = sql + ") VALUES (\""+values[0]+"\""
    for i in range(len(fields)-1):
        sql = sql+", \""+values[i+1]+"\""
    sql = sql + ")"
    cursor.execute(sql)
    DB.commit()
    return True

@client.event
async def on_message(message):
    global cursor
    connect_db()
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
async def on_guild_join(guild):
    global cursor
    connect_db()
    for member in guild.members:
        if member.guild_permissions.administrator:
            mod_id = str(member.id)
            check = select("SELECT id FROM moderators WHERE moderator = \""+mod_id+"\" AND is_user = 1")
            if not check:
                server = str(guild.id)
                insert("moderators", ("moderator", "is_user", "server"), (mod_id, "1", server))
    connect_db()
    owner_id = str(guild.owner.id)
    check = select("SELECT id FROM moderators WHERE moderator = \""+owner_id+"\" AND is_user = 1")
    if not check:
        server = str(guild.id)
        insert("moderators", ("moderator", "is_user", "server"), (owner_id, "1", server))

@client.event
async def on_ready():
    now=datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S"), " - Logged in as ", client.user.name, " - ", client.user.id)
    await client.change_presence(status=discord.Status.online, activity=discord.Game("c!help"))

secretfile = open("TOKEN","r")
TOKEN = secretfile.read()
secretfile.close()
connect_db()
insert("moderators",("moderator", "server"),("test", "test"))
client.run(TOKEN)