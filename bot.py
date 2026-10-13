
import os
import asyncio
import discord
from google import genai
from google.genai import types

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
ai = genai.Client(api_key=GEMINI_API_KEY)


def analisar_imagem(image_url):
    import urllib.request

    with urllib.request.urlopen(image_url, timeout=30) as resposta:
        imagem_bytes = resposta.read()

    response = ai.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=imagem_bytes,
                mime_type="image/jpeg",
            ),
            (
                "Descreva em português o que aparece nesta imagem "
                "de jogo. Identifique objetos, itens e textos legíveis. "
                "Não invente informações; se não tiver certeza, diga isso."
            ),
        ],
    )
    return response.text or "Não consegui identificar a imagem."


@bot.event
async def on_ready():
    print(f"Bot conectado: {bot.user}")


@bot.event
async def on_message(message):
    if bot.user and message.author.id == bot.user.id:
        return

    if message.channel.id != CHANNEL_ID:
        return

    imagens = [
        anexo for anexo in message.attachments
        if anexo.content_type
        and anexo.content_type.startswith("image/")
    ]

    for imagem in imagens[:3]:
        try:
            async with message.channel.typing():
                descricao = await asyncio.to_thread(
                    analisar_imagem, imagem.url
                )

            await message.reply(
                f"**Análise da imagem**\n{descricao}",
                mention_author=False,
            )
        except Exception as erro:
            print(f"Erro ao analisar imagem: {erro}")


bot.run(DISCORD_TOKEN)
