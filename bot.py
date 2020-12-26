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

def select(table, values, conditions):
    connect_db()
    global cursor
    if len(values) == 0:
        values = ("*",)
    sql = "SELECT "+values[0]
    for i in range(1,len(values)):
        sql = sql + ", " + values[i]
    sql = sql + " FROM " + table
    if len(conditions) > 0:
        sql = sql + " WHERE "+conditions
    cursor.execute(sql)
    return cursor.fetchall()
    
def select_one(table, values, conditions):
    connect_db()
    global cursor
    if len(values) == 0:
        values = ("*",)
    sql = "SELECT "+values[0]
    for i in range(1,len(values)):
        sql = sql + ", " + values[i]
    sql = sql + " FROM " + table
    if len(conditions) > 0:
        sql = sql + " WHERE "+conditions
    cursor.execute(sql)
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

def update(table, fields, values, conditions):
    connect_db()
    global cursor, DB
    if len(fields) == 0:
        return False
    if len(fields) != len(values):
        return False
    sql = "UPDATE "+table+" SET "+fields[0]+" = \""+values[0]+"\""
    for i in range(1, len(values)):
        sql = sql + ", "+fields[i]+" = \""+values[i]+"\""
    if len(conditions) > 0:
        sql = sql + " WHERE "+conditions
    cursor.execute(sql)
    DB.commit()
    return True

def get_pattern(message):
    temp = message.split(" ", 1)
    mes = temp[1]
    arr = mes.split(" # ", 1)
    if len(arr) == 2:
        return arr
    else:
        return False

def check_if_mod(member, guild):
    guild_id = str(guild.id)
    mods = select("moderators", ("moderator", "is_user", "is_role"), "server = \""+guild_id+"\"")
    for mod in mods:
        if mod[1] and str(member.id) == mod[0]:
            return True
        if mod[2]:
            for role in member.roles:
                if str(role.id) == mod[0]:
                    return True
    return False

def mention_to_id(string):
    ln = len(string)
    return string[1:(ln-1)]

@client.event
async def on_message(message):
    global cursor, forbidden

    try:
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
            response = select_one("conversations", ("response",), "LOWER(message) = \""+query_mes+"\" AND server = \"ALL\"")
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
            check = select("conversations", ("id",) ,"LOWER(message) = \""+lis[0].lower()+"\"")
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
            messages = select("conversations", ("message",), "server = \""+guild_id+"\"")
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
            permission = check_if_mod(message.author, message.channel.guild)
            if not permission:
                await message.channel.send("Nie masz odpowiednich uprawnień")
                return
            words = changequotes(mes).split(" ", 1)
            if len(words) != 2:
                await message.channel.send("Błędne użycie komendy. Prawidłowe użycie: c!delete [wiadomość]")
                return
            conditions = "LOWER(message) = \""+words[1].lower()+"\" AND server = \""+str(message.channel.guild.id)+"\""
            check = select_one("conversations", ("id",), conditions)
            if not check:
                await message.channel.send("Nie znaleziono podanej wiadomości w bazie danych")
                return
            delete("conversations", conditions)
            await message.channel.send("Gotowe!")
            return        

        if mes.startswith("c!edit"):
            permission = check_if_mod(message.author, message.channel.guild)
            if not permission:
                await message.channel.send("Nie masz odpowiednich uprawnień")
                return
            pattern = get_pattern(message.content)
            if not pattern:
                await message.channel.send("Błędne użycie komendy. Prawidłowe użycie: c!edit [wiadomość] # [odpowiedź]")
                return
            sql_mes = changequotes(pattern[0]).lower()
            sql_res = changequotes(pattern[1])
            check = select("conversations", ("id",), "LOWER(message) = \""+sql_mes+"\" AND server = \""+str(message.channel.guild.id)+"\"")
            if not check:
                await message.channel.send("Nie znaleziono podanej wiadomości w bazie danych")
                return
            if update("conversations", ("response",), (sql_res,), "LOWER(message) = \""+sql_mes+"\" AND server = \""+str(message.channel.guild.id)+"\""):
                await message.channel.send("Gotowe!")
            else:
                await message.channel.send("Coś poszło nie tak")
            return

        if mes.startswith("c!mods"):
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
                    msg = "Listę moderatorów prosto na serwer mogą wypisywać tylko moderatorzy. Uruchom komendę bez flagi \"-u\" aby dostać listę na DM"
                    await message.channel.send(msg)
                    return
            guild_id = str(message.channel.guild.id)
            mods_users = select("moderators", ("moderator",), "is_user = 1 AND server = \""+guild_id+"\"")
            mods_roles = select("moderators", ("moderator",), "is_role = 1 AND server = \""+guild_id+"\"")
            msg = None
            if len(mods_users)+len(mods_roles) == 0:
                msg = "Wygląda na to, że ten serwer nie ma żadnych moderatorów. Nie będzie można na tym serwerze używać bota.\nProszę skontaktować się z moim twórcą: Genocider#0794"
            else:
                msg = "Oto lista moderatorów dla tego serwera:"
            if to_server:
                await message.channel.send(msg)
                if len(mods_users) > 0:
                    await message.channel.send("Indywidualni użytkownicy:")
                for each in mods_users:
                    member = await message.channel.guild.fetch_member(int(each[0]))
                    await message.channel.send("**"+member.display_name+"** (id: "+each[0]+")")
                if len(mods_roles) > 0:
                    await message.channel.send("Role moderatorskie:")
                for each in mods_roles:
                    role = message.channel.guild.get_role(int(each[0]))
                    await message.channel.send("**"+role.name+"** (id: "+each[0]+")")
            else:
                await message.author.send(msg)
                if len(mods_users) > 0:
                    await message.author.send("Indywidualni użytkownicy:")
                for each in mods_users:
                    member = await message.channel.guild.fetch_member(int(each[0]))
                    await message.author.send("**"+member.display_name+"** (id: "+each[0]+")")
                if len(mods_roles) > 0:
                    await message.author.send("Role moderatorskie:")
                for each in mods_roles:
                    role = message.channel.guild.get_role(int(each[0]))
                    await message.channel.send("**"+role.name+"** (id: "+each[0]+")")
            return

        if mes.startswith("c!addmoderator"):
            permission = check_if_mod(message.author, message.channel.guild)
            if not permission:
                await message.channel.send("Nie masz odpowiednich uprawnień")
                return
            words = mes.split(" ")
            for word in words:
                print(word)
            if len(words) < 2:
                await message.channel.send("Błędne użycie komendy. Prawidłowe użycie: c!addModerator [rola/użytkownik] <\"-u\" jeżeli użytkownik>")
                return
            is_user = False
            try:
                option = words[2]
            except IndexError:
                option = "Null"
            if option == "-u":
                is_user = True
                user = None
                members = message.channel.guild.members
                for member in members:
                    if str(member.id) == words[1] or member.display_name.lower() == words[1]:
                        user = member
                        break
                    if len(words[1]) > 3:
                        if mention_to_id(words[1]) == str(member.id):
                            user = member
                            break
                if not user:
                    await message.channel.send("Nie znaleziono podanego użytkownika na serwerze")
                    return
                check = select("moderators", ("id",), "moderator = "+str(user.id)+" AND is_user = 1 AND server = "+str(message.channel.guild.id))
                if check:
                    await message.channel.send("Ta osoba jest już moderatorem na tym serwerze")
                    return
            else:
                mod_role = None
                roles = message.channel.guild.roles
                for role in roles:
                    if role.name.lower() == words[1] or str(role.id) == words[1]:
                        mod_role = role
                        break
                if not mod_role:
                    await message.channel.send("Nie znaleziono podanej roli na serwerze")
                    return
                check = select("moderators", ("id",), "moderator = "+str(mod_role.id)+" AND is_role = 1 AND server = "+str(message.channel.guild.id))
                if check:
                    await message.channel.send("Ta rola jest już moderatorska na tym serwerze")
                    return
            if is_user:
                if insert("moderators", ("moderator", "is_user", "server"), (str(user.id), "1", str(message.channel.guild.id))):
                    await message.channel.send("Gotowe!")
                else:
                    await message.channel.send("Coś poszło nie tak")
            else:
                if insert("moderators", ("moderator", "is_role", "server"), (str(role.id), "1", str(message.channel.guild.id))):
                    await message.channel.send("Gotowe!")
                else:
                    await message.channel.send("Coś poszło nie tak")
            return

        response = select_one("conversations", ("response",), "LOWER(message) = \""+query_mes+"\" AND server = \""+str(message.channel.guild.id)+"\"")
        if response:
            await message.channel.send(response[0])
            return

    except Exception as e:
        now=datetime.now()
        error_msg = "\nError occured: \n"
        error_msg = error_msg + "Date: "+str(now.strftime("%d/%m/%Y %H:%M:%S"))+"\n"
        if str(message.channel.type) == "private":
            error_msg = error_msg + "DM with "+message.author.display_name+" id: "+str(message.author.id)+"\n"
        else:
            error_msg = error_msg + "On server "+message.channel.guild.name+" id: "+str(message.channel.guild.id)+"\n"
        error_msg = error_msg + "Message content: "+message.content+"\n"
        error_msg = error_msg + "Error text: \n" 
        sys.stderr.write(error_msg)
        raise e

@client.event
async def on_guild_join(guild):
    global cursor
    for member in guild.members:
        if member.guild_permissions.administrator:
            mod_id = str(member.id)
            check = select("moderators", ("id",), "moderator = \""+mod_id+"\" AND is_user = 1")
            if not check:
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