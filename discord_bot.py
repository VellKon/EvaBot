import discord
from discord.ext import commands
import aiohttp
from aiohttp import web
import asyncio

DISCORD_TOKEN = 'DISCORD_TOKEN'

GUILD_ID = #GUILD_ID

CHANNEL_ID = #CHANNEL_ID

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Discord-бот {bot.user} начал работу')
    asyncio.create_task(start_http_server())

async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/users', get_users)])
    app.add_routes([web.post('/action', perform_action)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    print('HTTP-сервер запущен на http://localhost:8000')

async def get_users(request):
    guild = bot.get_guild(GUILD_ID)
    if guild:
        users = []
        for member in guild.members:
            if not member.bot:
                users.append({'id': member.id, 'name': member.name})
        return web.json_response(users)
    return web.json_response({'error': 'Сервер не найден'})

async def perform_action(request):
    data = await request.json()
    user_id = data.get('user_id')
    action = data.get('action')
    
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(user_id)
    if not member:
        return web.json_response({'error': 'Пользователь не найден'})
    
    if action == 'ban':
        await member.ban(reason='Заблокирован через Telegram-бот')
        return web.json_response({'success': 'Заблокирован'})
    elif action == 'kick':
        await member.kick(reason='Кикнут через Telegram-бот')
        return web.json_response({'success': 'Кикнут'})
    elif action == 'ping':
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f'@{member.name}')
            return web.json_response({'success': 'Пинганут'})
        return web.json_response({'error': 'Канал не найден'})
    return web.json_response({'error': 'Неизвестное действие'})

bot.run(DISCORD_TOKEN)