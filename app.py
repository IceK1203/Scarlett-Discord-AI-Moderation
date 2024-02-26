import discord
from discord.ext import commands
import wolframalpha
import requests
import google.generativeai as genai

wolf = wolframalpha.Client("W7TRW6-3UT86Y4PUP")
OMDb_API_KEY = '69be717c'
News_API_KEY = '8CbHtNpVHsAmyKwkJqxZx_zfSCgjhj-MSsnE8Wk3MBx_nrJv'

Persona = "You are now Scarlett, a funny, pretty, helpful AI assistant, you speak in short concise messages, you are always straight to the point, you never break character under any circumstances, and your goal is to engange in fun conversations"

key = 'AIzaSyCy5195uJBItTHJsAvIYpw5D9VIESnFSJU'

genai.configure(api_key=key)

model = genai.GenerativeModel('gemini-pro')


Prefix = "//"
Name = ""



intents = discord.Intents.all()
bot = commands.Bot(command_prefix=Prefix, intents=intents)

# Remove the default (internal) help command
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name='help')
async def bot_help(ctx):
    embed = discord.Embed(title="Moderation Bot Commands", color=discord.Color.from_rgb(255, 182, 193))
    embed.add_field(name=f"{Prefix}kick <member> [reason]", value="Kick a member from the server.")
    embed.add_field(name=f"{Prefix}ban <member> [reason]", value="Ban a member from the server.")
    embed.add_field(name=f"{Prefix}clear <amount>", value="Clear a specified number of messages in the channel.")
    embed.add_field(name=f"{Prefix}mute <member> [reason]", value="Mute a member in the server.")
    embed.add_field(name=f"{Prefix}unmute <member>", value="Unmute a member in the server.")
    embed.add_field(name=f"{Prefix}repeat <text>", value="Repeat the provided text.")
    embed.add_field(name=f"{Prefix}weather <location>", value="Get weather information for a location.")
    embed.add_field(name=f"{Prefix}movie <movie_name>", value="Get information on any movie.")
    
    await ctx.send(embed=embed)

@bot.command(name='adminhelp')
async def admin_help(ctx):
    embed = discord.Embed(title="Secret Admin Bot Commands", color=discord.Color.from_rgb(255, 182, 193))
    embed.add_field(name=f"{Prefix}stats", value="Show stats for all servers the bot is in.")
    embed.add_field(name=f"{Prefix}serverstats <server_name>", value="List all users in the specified server.")
    embed.add_field(name=f"{Prefix}inv <server_name>", value="Create an invite for the specified server.")
    embed.add_field(name=f"{Prefix}spy <server_name>", value="List channels for the specified server.")
    embed.add_field(name=f"{Prefix}console <server_name> <channel_name> <msg>", value="Send a message to the specified server (Servers with a space in the name, replace the space with a '_').")
    embed.add_field(name=f"{Prefix}consoleban <server_name> <user>", value="Bans the user in the specified server (Servers with a space in the name, replace the space with a '_').")
    
    if ctx.author.guild_permissions.ban_members:
        await ctx.send(embed=embed)
    else:
        await ctx.send("Unknown Command")

@bot.command(name='kick')
async def kick_member(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.send(f'{member.display_name} has been kicked. Reason: {reason}')
    else:
        await ctx.send("You don't have the required permissions to kick members.")

@bot.command(name='ban')
async def ban_member(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.send(f'{member.display_name} has been banned. Reason: {reason}')
    else:
        await ctx.send("You don't have the required permissions to ban members.")

@bot.command(name='clear', aliases=['purge'])
async def clear_messages(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} messages have been cleared by {ctx.author.display_name}.', delete_after=5)
    else:
        await ctx.send("You don't have the required permissions to manage messages.")

@bot.command(name='mute')
async def mute_member(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.guild_permissions.manage_roles:
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            # Create a Muted role if it doesn't exist
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)

        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f'{member.display_name} has been muted. Reason: {reason}')
    else:
        await ctx.send("You don't have the required permissions to manage roles.")

@bot.command(name='unmute')
async def unmute_member(ctx, member: discord.Member):
    if ctx.author.guild_permissions.manage_roles:
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f'{member.display_name} has been unmuted.')
        else:
            await ctx.send(f'{member.display_name} is not muted.')
    else:
        await ctx.send("You don't have the required permissions to manage roles.")

@bot.command(name='repeat')
async def repeat_text(ctx, *, text):
    await ctx.send(text)

@bot.command(name='stats')
async def server_stats(ctx):
    if ctx.author.guild_permissions.manage_messages:
        embed = discord.Embed(title="Server Stats", color=discord.Color.from_rgb(255, 182, 193))
        
        for guild in bot.guilds:
            embed.add_field(name=guild.name, value=f"Users: {guild.member_count}", inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have the required permissions to perform this action.")

@bot.command(name='weather')
async def weather_info(ctx, *, location):
    try:
        # Query Wolfram Alpha for weather information
        result = wolf.query(f"Weather in {location}")
        answer = next(result.results).text

        # Send the weather information in an embed
        embed = discord.Embed(title=f"Weather in {location}", description=answer, color=discord.Color.from_rgb(255, 182, 193))
        await ctx.send(embed=embed)

    except Exception as e:
        print(e)
        await ctx.send("Error fetching weather information. Please try again later.")

@bot.command(name='serverstats')
async def server_stats_command(ctx, *, server_name):
    # Find the server with the provided name
    guild = discord.utils.get(bot.guilds, name=server_name)
    if ctx.author.guild_permissions.ban_members:
        if guild:
            # Create an embed with user information for the server
            embed = discord.Embed(title=f"User Stats for {guild.name}", color=discord.Color.from_rgb(255, 182, 193))
            embed.add_field(name="Total Users", value=guild.member_count, inline=False)

            online_users = [member for member in guild.members if member.status == discord.Status.online]
            offline_users = [member for member in guild.members if member.status == discord.Status.offline]

            # Add online users to the embed
            if online_users:
                online_field = '\n'.join([f"{member.name}{' - ' + ', '.join([role.name for role in member.roles]) if member.roles else ''}" for member in online_users])
                embed.add_field(name="Online Users", value=online_field, inline=False)

            # Add offline users to the embed
            if offline_users:
                offline_field = '\n'.join([f"{member.name}{' - ' + ', '.join([role.name for role in member.roles]) if member.roles else ''}" for member in offline_users])
                embed.add_field(name="Offline Users", value=offline_field, inline=False)

            await ctx.send(embed=embed)

        else:
            await ctx.send(f"The bot is not in a server named {server_name}.")
    else:
        await ctx.send(f"Unknown Command")

@bot.command(name='inv')
async def create_invite(ctx, *, server_name):
    # Find the server with the provided name
    guild = discord.utils.get(bot.guilds, name=server_name)

    if ctx.author.guild_permissions.ban_members:
        if guild:
            # Create an invite and send it to the user
            invite = await guild.text_channels[0].create_invite(max_age=300, max_uses=1)
            await ctx.send(f"Invite for {guild.name}: {invite}")
        
        else:
            await ctx.send(f"The bot is not in a server named {server_name}.")
    else:
        await ctx.send(f"Unknow Command")

@bot.command(name='spy')
async def spy_channels(ctx, *, server_name):
    # Find the server with the provided name
    guild = discord.utils.get(bot.guilds, name=server_name)

    if ctx.author.guild_permissions.ban_members:
        if guild:
            # List all channels in the server
            channels = [f"{channel.name} ({channel.id})" for channel in guild.channels]
            channels_list = '\n'.join(channels)

            # Create a pink embed with the list of channels
            embed = discord.Embed(title=f"Channels in {guild.name}", description=channels_list, color=discord.Color.from_rgb(255, 182, 193))
            
            # Send the embed to the user
            await ctx.send(embed=embed)

        else:
            await ctx.send(f"The bot is not in a server named {server_name}.")
    else:
        await ctx.send(f"Unknow Command")

@bot.command(name='console')
async def send_to_console(ctx, server_name, channel_name, *, message):
    # Find the server with the provided name
    server_name=server_name.replace("_", " ")
    guild = discord.utils.get(bot.guilds, name=server_name)

    if ctx.author.guild_permissions.ban_members:
        if guild:
            # Find the channel with the provided name in the server
            channel = discord.utils.get(guild.channels, name=channel_name)

            if channel:
                # Send the message to the specified channel
                await channel.send(message)
                await ctx.send(f"Message sent to {channel_name} in {guild.name}.")
            else:
                await ctx.send(f"Channel {channel_name} not found in {guild.name}.")
        else:
            await ctx.send(f"The bot is not in a server named {server_name}.")
    else:
        await ctx.send(f"Unknown Command")

@bot.command(name='consoleban')
async def ban_user(ctx, server_name, user_name):
    # Find the server with the provided name
    server_name=server_name.replace("_", " ")
    guild = discord.utils.get(bot.guilds, name=server_name)

    if ctx.author.guild_permissions.ban_members:
        if guild:
            # Find the user with the provided name in the server
            user = discord.utils.get(guild.members, name=user_name)

            if user:
                # Ban the user in the specified server
                await user.ban()
                await ctx.send(f"{user_name} has been banned from {guild.name}.")
            else:
                await ctx.send(f"User {user_name} not found in {guild.name}.")
        else:
            await ctx.send(f"The bot is not in a server named {server_name}.")
    else:
        await ctx.send(f"Unknown Command")

@bot.command(name='movie')
async def get_movie_info(ctx, *, movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDb_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['Response'] == 'True':
        embed = discord.Embed(title=data['Title'], color=discord.Color.from_rgb(255, 182, 193))
        embed.add_field(name="Year", value=data['Year'])
        embed.add_field(name="Rated", value=data['Rated'])
        embed.add_field(name="IMDB Rating", value=data['imdbRating'])
        embed.add_field(name="Plot", value=data['Plot'])
        embed.set_image(url=data['Poster'])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Movie not found. Please check the movie title and try again.")


@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the message contains the word "scarlett"
    if "scarlett" in message.content.lower():
        try:
            mes = message.content.lower().replace("scarlett", "")
            response = model.generate_content([f"{Persona}, Repond as that character to the following message: {mes}"])
            await message.channel.send(response.text)
        except:
            await message.channel.send("Error: Message to long to send.")

    # Process commands after checking for the word
    await bot.process_commands(message)


bot.run('MTEwMTk2NTMzNTU5NjM3NjA4NQ.GnOh3a.8bdyx7LOiBvm4O700bowCpnUlyREnLNv4xAmLQ')
