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

def changequotes(word):
    result = ""
    for letter in word:
        if letter=="\"":
            result = result + "\\"
        result = result + letter    
    return result

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
    connect_db()
    global cursor
    cursor.execute(query)
    return cursor.fetchall()
    
def select_one(query):
    connect_db()
    global cursor
    cursor.execute(query)
    return cursor.fetchone()

def insert(table, fields, values):
    connect_db()
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

def delete(table, conditions):
    connect_db()
    global cursor, DB
    cmd = "DELETE FROM "+table
    if len(conditions) != 0:
        cmd = cmd + " WHERE " + conditions
    cursor.execute(cmd)
    DB.commit()

def get_pattern(message):
    mes=message[6:]
    arr = mes.split(" # ",1)
    if len(arr) == 2:
        return arr
    else:
        return False

def check_if_mod(member, guild):
    guild_id = str(guild.id)
    mods = select("SELECT moderator, is_user, is_role FROM moderators WHERE server = \""+guild_id+"\"")
    for mod in mods:
        if mod[1] and str(member.id) == mod[0]:
            return True
        if mod[2]:
            for role in member.roles:
                if str(role.id) == mod[0]:
                    return True
    return False

@client.event
async def on_message(message):
    global cursor, forbidden

    try:
        array = [3]
        print(array[7])
        if message.author==client.user:
            return
        
        #Super important feature. Bot doesn't work without it
        if message.mention_everyone:
            rage = ":AngryPing:791612271293759508"
            await message.add_reaction(rage)

        mes = message.content.lower()
        query_mes = changequotes(mes)
        response = None
        try:
            response = select_one("SELECT response FROM conversations WHERE LOWER(message) = \""+query_mes+"\" AND server = \"ALL\"")
        except mysql.connector.errors.DatabaseError:
            return
        if not response:
            if str(message.channel.type) == "private":
                await message.channel.send("Ten bot działa tylko na serwerach, nie DMach")
                return
        else:
            await message.channel.send(response[0])
            return

        if mes.startswith("c!set "):
            permission = check_if_mod(message.author, message.channel.guild)
            if not permission:
                await message.channel.send("Nie masz odpowiednich uprawnień")
                return
            lis = get_pattern(changequotes(message.content))
            if not lis:
                await message.channel.send("Nieprawidłowa forma komendy c!set. (c!set [wiadomość] # [odpowiedź]")
                return
            check = select("SELECT id FROM conversations WHERE LOWER(message) = \""+lis[0].lower()+"\"")
            if check:
                await message.channel.send("Odpowiedź do takiej wiadomości już istnieje. Użyj funkcji c!edit aby ją zmienić")
                return
            for each in forbidden:
                if lis[0].lower() == each:
                    await message.channel.send("Nie można ustawić wiadomości o takiej treści")
                    return
            insert("conversations", ("message", "response", "server"), (lis[0], lis[1], str(message.channel.guild.id)))
            await message.channel.send("Gotowe!")
            return

        if mes.startswith("c!list"):
            words = message.content.split(" ")
            to_server = False
            try:
                option = words[1].lower()
            except IndexError:
                option = "Null"
            if option == "-s":
                to_server = True
                permission = check_if_mod(message.author, message.channel.guild)
                if not permission:
                    msg = "Wiadomości prosto na serwer mogą wypisywać tylko moderatorzy. Uruchom komendę bez flagi \"-u\" aby dostać listę na DM"
                    await message.channel.send(msg)
                    return
            guild_id = str(message.channel.guild.id)
            messages = select("SELECT message FROM conversations WHERE server = \""+guild_id+"\"")
            msg = None
            if len(messages) == 0:
                msg = "Ten serwer nie posiada żadnych wiadomości na które mam reagować"
            else:
                msg = "Oto lista wiadomości dla tego serwera:"
            if to_server:
                await message.channel.send(msg)
                for each in messages:
                    await message.channel.send("- "+each[0])
            else:
                await message.author.send(msg)
                for each in messages:
                    await message.author.send("- "+each[0])
            return

        if mes.startswith("c!delete"):
            words = changequotes(mes).split(" ", 1)
            if len(words) != 2:
                await message.channel.send("Błędne użycie komendy. Prawidłowe użycie: c!delete [wiadomość]")
                return
            permission = check_if_mod(message.author, message.channel.guild)
            if not permission:
                await message.channel.send("Nie masz odpowiednich uprawnień")
                return
            conditions = "LOWER(message) = \""+words[1].lower()+"\" AND server = \""+str(message.channel.guild.id)+"\""
            check = select_one("SELECT id FROM conversations WHERE "+conditions)
            if not check:
                await message.channel.send("Nie znaleziono podanej wiadomości w bazie danych")
                return
            delete("conversations", conditions)
            await message.channel.send("Gotowe!")
            return        

        response = select_one("SELECT response FROM conversations WHERE LOWER(message) = \""+query_mes+"\" AND server = \""+str(message.channel.guild.id)+"\"")
        if response:
            await message.channel.send(response[0])
            return
    except Exception as e:
        now=datetime.now()
        sys.stderr.write(str(now.strftime("%d/%m/%Y %H:%M:%S"))+": "+e)

@client.event
async def on_guild_join(guild):
    global cursor
    for member in guild.members:
        if member.guild_permissions.administrator:
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