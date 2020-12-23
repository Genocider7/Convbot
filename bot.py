import discord, mysql.connector, sys
from datetime import datetime
TOKEN=""
DB=None
cursor=None

forbidden = ["c!set", "c!addmoderator", "c!removemoderator", "c!edit", "c!delete",  "c!list", "c!mods"]
sys.stdout=open("convbot.log","a")
sys.stderr=open("convbot.error.log","a")
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

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
    database = 'convbotDB'
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

def get_pattern(message):
    mes=message[6:]
    arr = mes.split(" # ",2)
    if len(arr) == 2:
        return arr
    else:
        return False

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

    if mes.startswith("c!set "):
        permission = False
        guild_id = str(message.channel.guild.id)
        mods = select("SELECT moderator, is_user, is_role FROM moderators WHERE server = \""+guild_id+"\"")
        for mod in mods:
            if mod[1] and str(message.author.id) == mod[0]:
                permission = True
                break
            if mod[2]:
                for role in message.author.roles:
                    if str(role.id) == mod[0]:
                        permission = True
                        break
                if permission:
                    break
        if not permission:
            await message.channel.send("Nie masz odpowiednich uprawnień")
            return
        lis = get_pattern(message.content)
        if not lis:
            await message.channel.send("Nieprawidłowa forma komendy c!set. (c!set [wiadomość] # [odpowiedź]")
            return
        check = select("SELECT id FROM conversations WHERE LOWER(message) = \""+lower(lis[0])+"\"")
        if check:
            await message.channel.send("Odpowiedź do takiej wiadomości już istnieje. Użyj funkcji c!edit aby ją zmienić")
            return
        insert("conversations", ("message", "response", "server"), (lis[0], lis[1], guild_id))
        await message.channel.send("Gotowe!")
        return

    response = select_one("SELECT response FROM conversations WHERE LOWER(message) = \""+mes+"\" AND server = \""+str(message.channel.guild.id)+"\"")
    if response:
        await message.channel.send(response[0])
        return

@client.event
async def on_guild_join(guild):
    global cursor
    for member in guild.members:
        if member.guild_permissions.administrator:
            connect_db()
            mod_id = str(member.id)
            check = select("SELECT id FROM moderators WHERE moderator = \""+mod_id+"\" AND is_user = 1")
            if len(check) == 0:
                server = str(guild.id)
                insert("moderators", ("moderator", "is_user", "server"), (mod_id, "1", server))

@client.event
async def on_ready():
    now=datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S"), " - Logged in as ", client.user.name, " - ", client.user.id)
    await client.change_presence(status=discord.Status.online, activity=discord.Game("c!help"))

secretfile = open("TOKEN","r")
TOKEN = secretfile.read()
secretfile.close()
connect_db()
client.run(TOKEN)