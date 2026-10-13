
import os
import asyncio
import discord
from openai import OpenAI

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
ai = OpenAI(api_key=OPENAI_API_KEY)


def analisar_imagem(image_url):
    response = ai.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Descreva em português o que aparece "
                            "nesta imagem. Identifique objetos, "
                            "itens do jogo e textos legíveis. "
                            "Não invente informações; se não "
                            "tiver certeza, diga isso."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url,
                        "detail": "high",
                    },
                ],
            }
        ],
    )
    return response.output_text.strip()


@bot.event
async def on_ready():
    print(f"Bot conectado: {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
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
