#!optimize
import asyncio
import time
import sys
import os
import httpx
import discord
import aiohttp
from discord import commands



# * YOU ARE ALLOWED TO MODIFY THIS SCRIPT AS YOU LIKE
# * TARGET COPIER SCRIPT
# * TO GET SELF BOT IMPORT DO 'pip uninstall discord' AND INSTALL 'pip install git+https://github.com/dolfies/discord.py-self.git'

__config__ = {
    "account_token": os.getenv("DISCORD_TOKEN"),
    "prefix": "$",
    "webhook": os.getenv("DISCORD_WEBHOOK"),
    "tracker_guild": 1429695694901346394 or "https://discord.gg/nrrBBBr3UJ",
    "tracker_channel": 1429882647856939091,
    "preset_target": {
        "activate_preset_instead": True,
        "userid": 891507123324846081, # 891507123324846081
        "channelid": 1429878948904566814, # 1429878948904566814
        "shared_guildids": {}
    },
}

monitering = None
server_monitering = None
output = __config__["webhook"]
prefix = __config__["prefix"]
commands = {
    "status": lambda client, message: message.channel.send(f"Active | Leached on to {monitering}"),
}

preset = __config__["preset_target"]
activator = preset["activate_preset_instead"]
presetid = preset["userid"]

if activator == True:
    monitering = presetid

public_guilds = { # * Guilds to check if there in one of them | Logic is missing and this will require a captcha bypasser for discord. or a api of some sort
    "https://discord.gg/marvelrivals",
    "https://discord.gg/midjourney",
    "https://discord.gg/genshinimpact",
    "https://discord.gg/roblox",
    "https://discord.gg/rodevs",
    "https://discord.gg/minecraft",
    "https://discord.gg/fortnite",
    "https://discord.gg/tkfortnite",
    "https://discord.gg/ecafe",
    "https://discord.gg/yumm",
    "https://discord.gg/socialz",
    "https://discord.gg/maba",
    "https://discord.com/32TwwtZFjW",
    "https://discord.com/ntts",
    "https://discord.com/finalstand"
}

class Client(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.http_client = httpx.AsyncClient()
    
    async def on_ready(self): 
        print(f"Logged on as {self.user}")
        shared_guilds = []
        for guild in self.guilds:
            try:
                await guild.fetch_member(presetid)
                shared_guilds.append(guild)
            except discord.NotFound:
                pass
            except Exception as e:
                print(f"Error checking guild {guild.id}: {e}")
        if shared_guilds:
            __config__["preset_target"]["shared_guildids"] = {g.id for g in shared_guilds}
            print(f"Found shared guilds: {', '.join(str(g.id) for g in shared_guilds)}")
        else:
            print("No shared guilds found with the target user")
        if activator == True:
            await self.start_preset_mimic()
    
    async def join_guild(self):
        session = httpx.Client()

        for invite in public_guilds:
            import json

            get = session.get(f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true")
            if get.status_code == 200:
                try:
                    data = get.json()
                    guild = data["guild"]["id"]
                    channel = data["channel"]["id"]
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")

    async def find_user_guild(self, userid: int, search_term: str, message):
        results = []

        await self.join_guild()
        for guild in self.guilds:
            for member in guild.members:
                if (
                    search_term.lower() in member.name.lower()
                    or search_term.lower() in member.display_name.lower()
                    or search_term == str(member.id)
                    or userid == str(member.id)
                ):
                    results.append(f"{member} | ID: {member.id}")
            if results:
                print(f"\n".join(results[:10]))
                return results
            else:
                print("not found")

    async def start_preset_mimic(self):
        print(f"Started the mimic")

        target_user_id = __config__["preset_target"]["userid"]
        channel_id = __config__["preset_target"]["channelid"]

        target_member = None
        for guild_id in __config__["preset_target"]["shared_guildids"]:
            guild = self.get_guild(guild_id)
            if guild:
                try:
                    member = await guild.fetch_member(target_user_id)
                    if member:
                        target_member = member
                        break
                except discord.NotFound:
                    pass
                except Exception as e:
                    print(f"Error fetching member in guild {guild_id}: {e}")

        channel = self.get_channel(channel_id)

        if target_member and channel:
            print(f"Started copying {target_member}'s status and state")
            await self.mimic_user_status(target_member)
        
    async def mimic_user_status(self, target_member):
        print(f"Trying to mimic...")
        
        try:
            target_status = target_member.status
            target_activity = target_member.activity

            await self.change_presence(status=target_status, activity=target_activity)
            print(f"Mimicked status: {target_status} | Activity: {target_activity}")
        except Exception as e:
            print(f"Error: {e}")

    async def on_presence_update(self, before, after):
        if __config__["preset_target"]["activate_preset_instead"] and after.id == __config__["preset_target"]["userid"]:
            await self.mimic_user_status(after)
    
    async def send_webhook(self, data):
        try:
            response = await self.http_client.post(output,json=data, timeout=3.0)
            if response.status_code == 204:
                pass
            else:
                print(f"failed ({response.status_code}): {response.text}")
        except httpx.RequestError as e:
            print(f"Webhook send failed: {e}")
    
    async def close(self):
        await self.http_client.aclose()
        await super().close()

    async def on_message(self, message):
        if message.content.startswith(prefix):
            await self.handle_command(message)
        if monitering and str(message.author.id) == str(monitering):
            guild = message.guild
            guildid = guild.id if guild else "DM"
            guild_name = guild.name if guild else "DM"
            print(f"Monitoring: {message.author} said: '{message.content}' | in: {guild_name} {guildid}")
            await self.send_webhook(
                data={
                    "content": message.content,
                    "username": str(message.author),
                    "avatar_url": message.author.display_avatar.url,
                }
            )
        #if str(message.author.id) == str(presetid):
        #    guild = message.guild
        #    guildid = guild.id if guild else "DM"
        #    guild_name = guild.name if guild else "DM"
        #    print(f"**PRESET** Monitoring: {message.author} said: '{message.content}' | in: {guild_name} {guildid}")
        #    await self.send_webhook(
        #        data={
        #            "content": message.content,
        #            "username": str(message.author),
        #            "avatar_url": message.author.display_avatar.url,
        #        }
        #    )
    
    async def handle_command(self, message):
        content = message.content[len(prefix):].strip()
        cmd = content.split()[0] if content else ""
        
        if cmd in commands:
            await commands[cmd](self, message)
            print(f"Executed command: {cmd} ")
        else:
            await message.channel.send(f"Unkown command: {cmd} ")        

def addCMD(name, callback):
    commands[name] = callback
    print(f"command injected: {name} ")

# we could also put a attach server command here but that would require a bot
# it would be a lot of work ngl, so i didn't put it here

async def attach_user(client, message):
    global monitering
    args = message.content.split()[1:]
    if args and activator == False:
        target = args[0]
        if target.startswith('<@') and target.endswith('>'):
            target = target[2:-1]
            if target.startswith('!'):
                target = target[1:]
        monitering = target
        target_id = int(monitering)
        shared_guilds = []
        for guild in client.guilds:
            try:
                await guild.fetch_member(target_id)
                shared_guilds.append(guild)
            except discord.NotFound:
                pass
            except Exception as e:
                print(f"Error checking guild {guild.id} for monitor: {e}")
        if shared_guilds:
            await message.channel.send(f"Leached on to: {monitering}\nFound shared guilds: {', '.join(g.name for g in shared_guilds)}")
        else:
            await message.channel.send(f"Leached on to: {monitering}\nNo shared guilds found with the target user")

async def unattach_user(client, message):
    global monitering
    monitering = None
    await message.channel.send("Stopped leach")

async def delete_all_messages(client, message):
    args = message.content.split()[1:]
    if not args:
        await message.channel.send("that's not how you use the args -_-")
        return
    
    channel_id = args[0]
    try:
        channel = client.get_channel(int(channel_id))
        if not channel:
            await message.channel.send("channel not found!")
            return
        
        count = 0
        async for msg in channel.history(limit=None):
            if msg.author == client.user:
                await msg.delete()
                count += 1
                await asyncio.sleep(0)
        await message.channel.send(f"Deleted {count}")
    except Exception as e:
        await message.channel.send(f"Error: {str(e)}")

async def save_chat(client, message):
    current_channel = message.channel
    file_name = f"chat_{current_channel.id}_history.txt"

    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            async for msg in current_channel.history(limit=None):
                f.write(f"{msg.created_at} | {msg.author}: {msg.content}\n\n")
        await message.channel.send(file=discord.File(file_name))
        os.remove(file_name)
    except Exception as e:
        await message.channel.send(f"Error: {str(e)}")
            
async def main():
    while True:
        main_Client = Client()
        addCMD("savechat", save_chat)
        addCMD("purge", delete_all_messages)
        addCMD("monitor", attach_user)
        addCMD("unmonitor", unattach_user)

        try:
            print("Bot starting...")
            await main_Client.start(__config__["account_token"]) # or main_Client.run
        except Exception as e:
            print(f"Disconnected: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)
        finally:
            try:
                await main_Client.close()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
