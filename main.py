import discord
from discord.ext import commands
import sqlite3

# -----------------------------
# CONFIGURACIÓN DEL BOT
# -----------------------------

TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# BASE DE DATOS
# -----------------------------

conn = sqlite3.connect("leafy.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    achievements TEXT DEFAULT ''
)
""")

conn.commit()

# -----------------------------
# FUNCIONES
# -----------------------------

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute("""
        INSERT INTO users (user_id, xp, level, achievements)
        VALUES (?, 0, 1, '')
        """, (user_id,))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

    return user


def add_xp(user_id, amount):
    user = get_user(user_id)

    xp = user[1] + amount
    level = user[2]

    next_level_xp = level * 100

    if xp >= next_level_xp:
        level += 1

    cursor.execute("""
    UPDATE users
    SET xp = ?, level = ?
    WHERE user_id = ?
    """, (xp, level, user_id))

    conn.commit()


def add_achievement(user_id, achievement):
    user = get_user(user_id)

    achievements = user[3]

    if achievement not in achievements:
        achievements += f"{achievement},"

        cursor.execute("""
        UPDATE users
        SET achievements = ?
        WHERE user_id = ?
        """, (achievements, user_id))

        conn.commit()

        return True

    return False


# -----------------------------
# EVENTOS
# -----------------------------

@bot.event
async def on_ready():
    print(f"🍃 Leafy conectado como {bot.user}")


# -----------------------------
# COMANDOS
# -----------------------------

@bot.command()
async def hola(ctx):
    await ctx.send("🌿 Hola, soy Leafy")


@bot.command()
async def reto(ctx):
    retos = [
        "♻️ Recicla algo hoy",
        "💧 Ahorra agua durante el día",
        "🚶 Camina en vez de usar carro",
        "🌱 Planta algo pequeño",
        "🛍️ Evita plástico de un solo uso"
    ]

    import random

    reto_random = random.choice(retos)

    add_xp(ctx.author.id, 20)

    logro = add_achievement(ctx.author.id, "🌱 Primer Reto")

    mensaje = f"{ctx.author.mention}\nTu reto de hoy:\n\n{reto_random}\n\n+20 XP"

    if logro:
        mensaje += "\n🏆 Logro desbloqueado: 🌱 Primer Reto"

    await ctx.send(mensaje)


@bot.command()
async def perfil(ctx):
    user = get_user(ctx.author.id)

    xp = user[1]
    level = user[2]
    achievements = user[3]

    if achievements == "":
        achievements = "Ninguno"

    embed = discord.Embed(
        title="🍃 Perfil Leafy",
        color=discord.Color.green()
    )

    embed.add_field(name="Usuario", value=ctx.author.name, inline=False)
    embed.add_field(name="Nivel", value=level, inline=True)
    embed.add_field(name="XP", value=xp, inline=True)
    embed.add_field(name="Logros", value=achievements, inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def ayudar(ctx):
    embed = discord.Embed(
        title="🌎 Comandos Leafy",
        color=discord.Color.green()
    )

    embed.add_field(name="!hola", value="Saluda al bot", inline=False)
    embed.add_field(name="!reto", value="Obtén un reto ecológico", inline=False)
    embed.add_field(name="!perfil", value="Muestra tu perfil", inline=False)

    await ctx.send(embed=embed)


# -----------------------------
# INICIAR BOT
# -----------------------------

bot.run(TOKEN)
