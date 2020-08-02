
import asyncio
import aiohttp
from html import escape

from pyrogram import Filters

from nana import app, Command, AdminSettings
from nana.helpers.PyroHelpers import msg


__MODULE__ = "Weather"
__HELP__ = """
Get current weather in your location

──「 **Weather** 」──
-> `wttr (location)`
Get current weather in your location.
Powered by `wttr.in`
"""


@app.on_message(Filters.user(AdminSettings) & Filters.command("wttr", Command))
async def weather(_client, message):
    if len(message.command) == 1:
        await msg(message, text="Usage: `wttr Maldives`")
        await asyncio.sleep(3)
        await message.delete()

    if len(message.command) > 1:
        location = message.command[1]
        headers = {'user-agent': 'httpie'}
        url = f"https://wttr.in/{location}?mnTC0&lang=en"
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    data = await resp.text()
        except Exception as e:
            print(e)
            await msg(message, text="Failed to get the weather forecast")

        if 'we processed more than 1M requests today' in data:
            await msg(message, text="`Sorry, we cannot process this request today!`")
        else:
            weather_data = f"<code>{escape(data.replace('report', 'Report'))}</code>"
            await msg(message, text=weather_data, parse_mode='html')
