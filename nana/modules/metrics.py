# Thanks to @Athfan for a Base Plugin.
# Go and Do a star on his repo: https://github.com/athphane/userbot
import time
import timeago

from pyrogram import Filters
from pyrogram.client.ext.utils import get_channel_id

from nana import Command, app, AdminSettings
from nana.helpers.PyroHelpers import msg

__MODULE__ = "Metrics"
__HELP__ = """
This module can help you do the wordcount in the last 1000 messages in a groupchat or private chat.

──「 **Word Count** 」──
-> `wordcount` or `wc`
Finds the 25 most used words in the last 1000 messages in a chat.

──「 **Inactive message count** 」──
-> `msg` or `msg <integer>`
Finds the inactive users with last message in a chat.

"""


class Custom(dict):
    def __missing__(self, key):
        """define missing value"""
        return 0


async def get_inactive(client, message):
    cmd = message.command
    start = time.time()
    limit = int(" ".join(cmd[1:])) if len(cmd) > 1 else 0
    messages = [
        m
        async for member in client.iter_chat_members(
            message.chat.id, limit=limit, filter="recent"
        )
        if not member.user.is_deleted
        async for m in client.search_messages(
            message.chat.id, limit=1, from_user=member.user.id
        )
    ]

    delta = time.time() - start
    messages.sort(key=lambda k: k["date"])

    return "\n".join(
        [
            "[{}](tg://user?id={}) last [message](https://t.me/c/{}/{}) was {}".format(
                m.from_user.first_name,
                m.from_user.id,
                get_channel_id(m.chat.id),
                m.message_id,
                timeago.format(m.date),
            )
            for m in messages
        ]
        + [f"`{int(delta * 1000)}ms`"]
    )


@app.on_message(Filters.user(AdminSettings) & Filters.command(["wordcount", "wc"], Command))
async def word_count(client, message):
    await message.delete()
    words = Custom()
    progress = await client.send_message(message.chat.id, "`Processing 1000 messages...`")
    async for msg in client.iter_history(message.chat.id, 1000):
        if msg.text:
            for word in msg.text.split():
                words[word.lower()] += 1
        if msg.caption:
            for word in msg.caption.split():
                words[word.lower()] += 1
    freq = sorted(words, key=words.get, reverse=True)
    out = "Word Counter\n"
    for i in range(25):
        out += f"{i + 1}. **{words[freq[i]]}**: {freq[i]}\n"

    await progress.edit_text(out)


@app.on_message(Filters.me & Filters.command("msg", Command))
async def inactive_msg(client, message):
    text = await get_inactive(client, message)
    await msg(message, text=text)
