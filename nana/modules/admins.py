import asyncio
import time
from emoji import get_emoji_regexp

from pyrogram import ChatPermissions, Filters
from pyrogram.errors import (
    UsernameInvalid,
    ChatAdminRequired,
    PeerIdInvalid,
    UserIdInvalid,
    UserAdminInvalid,
    FloodWait,
)

from nana import app, Command, AdminSettings
from nana.helpers.admincheck import admin_check, is_sudoadmin
from nana.helpers.PyroHelpers import msg


__MODULE__ = "Admin"
__HELP__ = """
Module for Group Admins

──「 **Locks / Unlocks** 」──
-> `lock` or `unlock`
locks and unlocks permission in the group
__Supported Locks / Unlocks__:
 `messages` `media` `stickers`
 `polls` `info` `invite`
 `animations` `games`
 `inlinebots` `webprev`
 `pin` `all`

-> `vlock`
view group permissions

──「 **Promote / Demote** 」──
-> `promote`
Reply to a user to promote

-> `demote`
Reply to a user to demote

──「 **Ban / Unban** 」──
-> `ban` or `unban`
Reply to a user to perform ban or unban

──「 **Kick User** 」──
-> `kick`
Reply to a user to kick from chat

──「 **Mute / Unmute** 」──
-> `mute` or `mute 24` or `unmute`
Reply to a user to mute or unmute

──「 **Invite Link** 」──
-> `invite`
Generate Invite link

──「 **Message Pin** 」──
-> `pin`
Reply a message to pin in the Group
__Supported pin types__: `alert`, `notify`, `loud`

──「 **Deleted Account** 」──
-> `delacc` or `delacc clean`
Checks Group for deleted accounts & clean them
"""

# Mute permissions
mute_permission = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_stickers=False,
    can_send_animations=False,
    can_send_games=False,
    can_use_inline_bots=False,
    can_add_web_page_previews=False,
    can_send_polls=False,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)

# Unmute permissions
unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_stickers=True,
    can_send_animations=True,
    can_send_games=True,
    can_use_inline_bots=True,
    can_add_web_page_previews=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)


@app.on_message(Filters.user(AdminSettings) & Filters.command("invite", Command))
async def invite_link(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        chat_name = message.chat.title
        can_invite = await admin_check(message)
        if can_invite:
            try:
                link = await client.export_chat_invite_link(chat_id)
                await msg(message, text=f"**Generated Invite link for {chat_name}:**\n - **Join Link:** {link}")
            except Exception as e:
                print(e)
                await msg(message, text="`permission denied`")
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("pin", Command))
async def pin_message(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_pin = await admin_check(message)
        if can_pin:
            try:
                if message.reply_to_message:
                    disable_notification = True
                    if len(message.command) >= 2 and message.command[1] in [
                        "alert",
                        "notify",
                        "loud",
                    ]:
                        disable_notification = False
                    await client.pin_chat_message(
                        message.chat.id,
                        message.reply_to_message.message_id,
                        disable_notification=disable_notification,
                    )
                    text = f"**Message Pinned**\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)
                else:
                    await msg(message, text="`Reply to a message to pin`")
                    await asyncio.sleep(5)
                    await message.delete()
            except Exception as e:
                await msg(message, text="`Error!`\n" f"**Log:** `{e}`")
                return
        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("mute", Command))
async def mute_hammer(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_mute = await admin_check(message)
        if can_mute:
            if message.reply_to_message:
                try:
                    get_mem = await client.get_chat_member(
                        chat_id, message.reply_to_message.from_user.id
                    )
                    if (
                        len(message.text.split()) == 2
                        and message.text.split()[1] == "24"
                    ):
                        await client.restrict_chat_member(
                            chat_id=message.chat.id,
                            user_id=message.reply_to_message.from_user.id,
                            permissions=mute_permission,
                            until_date=int(time.time() + 86400),
                        )
                        text = f"**Muted for 24 hours**\n"
                    else:
                        await client.restrict_chat_member(
                            chat_id=message.chat.id,
                            user_id=message.reply_to_message.from_user.id,
                            permissions=mute_permission,
                        )
                        text = f"**Muted Indefinitely**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)
                except Exception as e:
                    await msg(message, text="`Error!`\n" f"**Log:** `{e}`")
                    return
            else:
                await msg(message, text="`Reply to a user to mute them`")
                await asyncio.sleep(5)
                await message.delete()
        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("unmute", Command))
async def unmute(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_unmute = await admin_check(message)
        if can_unmute:
            try:
                if message.reply_to_message:
                    get_mem = await client.get_chat_member(
                        chat_id, message.reply_to_message.from_user.id
                    )
                    await client.restrict_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.reply_to_message.from_user.id,
                        permissions=unmute_permissions,
                    )
                    text = f"**Unmuted**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)

                else:
                    await msg(message, text="`Reply to a user to mute them`")
                    await asyncio.sleep(5)
                    await message.delete()
            except Exception as e:
                await msg(message, text="`Error!`\n" f"**Log:** `{e}`")
                return
        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("kick", Command))
async def kick_user(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_kick = await admin_check(message)
        if can_kick:
            if message.reply_to_message:

                try:
                    get_mem = await client.get_chat_member(
                        chat_id, message.reply_to_message.from_user.id
                    )
                    await client.kick_chat_member(
                        chat_id, get_mem.user.id, int(time.time() + 45)
                    )
                    text = f"**Kicked**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)

                except ChatAdminRequired:
                    await msg(message, text="`permission denied`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except Exception as e:
                    await msg(message, text="`Error!`\n" f"**Log:** `{e}`")
                    return

            else:
                await msg(message, text="`Reply to a user to kick`")
                await asyncio.sleep(5)
                await message.delete()
                return

        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("ban", Command))
async def ban_usr(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_ban = await admin_check(message)

        if can_ban:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
            else:
                await msg(message, text="`reply to a user to ban.`")
                await asyncio.sleep(5)
                await message.delete()

            if user_id:
                try:
                    get_mem = await client.get_chat_member(chat_id, user_id)
                    await client.kick_chat_member(chat_id, user_id)
                    text = f"**Banned**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)

                except UsernameInvalid:
                    await msg(message, text="`invalid username`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except PeerIdInvalid:
                    await msg(message, text="`invalid username or userid`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except UserIdInvalid:
                    await msg(message, text="`invalid userid`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except ChatAdminRequired:
                    await msg(message, text="`permission denied`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except Exception as e:
                    await msg(message, text=f"**Log:** `{e}`")
                    return

        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
            return
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("unban", Command))
async def unban_usr(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_unban = await admin_check(message)
        if can_unban:
            if message.reply_to_message:
                try:
                    get_mem = await client.get_chat_member(
                        chat_id, message.reply_to_message.from_user.id
                    )
                    await client.unban_chat_member(chat_id, get_mem.user.id)
                    text = f"**Unbanned**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)

                except Exception as e:
                    await msg(message, text=f"**Log:** `{e}`")
                    return

            else:
                await msg(message, text="`Reply to a user to unban`")
                await asyncio.sleep(5)
                await message.delete()
                return
        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("promote", Command))
async def promote_usr(client, message):
    if message.chat.type in ["group", "supergroup"]:
        cmd = message.command
        custom_rank = ""
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_promo = await is_sudoadmin(message)

        if can_promo:
            if message.reply_to_message:
                get_mem = await client.get_chat_member(
                    chat_id, message.reply_to_message.from_user.id
                )
                user_id = message.reply_to_message.from_user.id
                custom_rank = get_emoji_regexp().sub("", " ".join(cmd[1:]))

                if len(custom_rank) > 15:
                    custom_rank = custom_rank[:15]
            else:
                await msg(message, text="`reply to a user to promote`")
                await asyncio.sleep(5)
                await message.delete()
                return

            if user_id:
                try:
                    await client.promote_chat_member(
                        chat_id,
                        user_id,
                        can_change_info=True,
                        can_delete_messages=True,
                        can_restrict_members=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                    )

                    await asyncio.sleep(2)
                    await client.set_administrator_title(chat_id, user_id, custom_rank)
                    text = f"**Promoted**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)
                except UsernameInvalid:
                    await msg(message, text="`invalid username`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return
                except PeerIdInvalid:
                    await msg(message, text="`invalid username or userid`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return
                except UserIdInvalid:
                    await msg(message, text="`invalid userid`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except ChatAdminRequired:
                    await msg(message, text="`permission denied`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except Exception as e:
                    await msg(message, text=f"**Log:** `{e}`")
                    return

        else:
            await msg(message, text="`permission denied`")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("demote", Command))
async def demote_usr(client, message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        get_group = await client.get_chat(chat_id)
        can_demote = await is_sudoadmin(message)

        if can_demote:
            if message.reply_to_message:
                try:
                    get_mem = await client.get_chat_member(
                        chat_id, message.reply_to_message.from_user.id
                    )
                    await client.promote_chat_member(
                        chat_id,
                        get_mem.user.id,
                        can_change_info=False,
                        can_delete_messages=False,
                        can_restrict_members=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                    )


                    text = f"**Demoted**\n"
                    text += f"User: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    text += f"(`{get_mem.user.id}`)\n"
                    text += f"Chat: `{get_group.title}` (`{chat_id}`)"
                    await msg(message, text=text)
                except ChatAdminRequired:
                    await msg(message, text="`permission denied`")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except Exception as e:
                    await msg(message, text=f"**Log:** `{e}`")
                    return

            if not message.reply_to_message:
                await msg(message, text="`reply to a user to demote.`")
                return
        else:
            await msg(message, text="``permission denied`")
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("lock", Command))
async def lock_permission(client, message):
    """module that locks group permissions"""
    if message.chat.type in ["group", "supergroup"]:
        cmd = message.command
        is_admin = await admin_check(message)
        if not is_admin:
            await message.delete()
            return
        messages = ""
        media = ""
        stickers = ""
        animations = ""
        games = ""
        inlinebots = ""
        webprev = ""
        polls = ""
        info = ""
        invite = ""
        pin = ""
        perm = ""
        lock_type = " ".join(cmd[1:])
        chat_id = message.chat.id
        if not lock_type:
            await msg(message, text="`Cant lock the void")
            await asyncio.sleep(3)
            await message.delete()
            return

        get_perm = await client.get_chat(chat_id)

        messages = get_perm.permissions.can_send_messages
        media = get_perm.permissions.can_send_media_messages
        stickers = get_perm.permissions.can_send_stickers
        animations = get_perm.permissions.can_send_animations
        games = get_perm.permissions.can_send_games
        inlinebots = get_perm.permissions.can_use_inline_bots
        webprev = get_perm.permissions.can_add_web_page_previews
        polls = get_perm.permissions.can_send_polls
        info = get_perm.permissions.can_change_info
        invite = get_perm.permissions.can_invite_users
        pin = get_perm.permissions.can_pin_messages

        if lock_type == "all":
            try:
                await client.set_chat_permissions(chat_id, ChatPermissions())
                await msg(message, text="`Locked all permission from this Chat!`")
                await asyncio.sleep(5)
                await message.delete()

            except Exception as e:
                await msg(message, text="`permission denied`\n" f"**Log:** `{e}`")
            return

        if lock_type == "messages":
            messages = False
            perm = "messages"

        elif lock_type == "media":
            media = False
            perm = "audios, documents, photos, videos, video notes, voice notes"

        elif lock_type == "stickers":
            stickers = False
            perm = "stickers"

        elif lock_type == "animations":
            animations = False
            perm = "animations"

        elif lock_type == "games":
            games = False
            perm = "games"

        elif lock_type == "inlinebots":
            inlinebots = False
            perm = "inline bots"

        elif lock_type == "webprev":
            webprev = False
            perm = "web page previews"

        elif lock_type == "polls":
            polls = False
            perm = "polls"

        elif lock_type == "info":
            info = False
            perm = "info"

        elif lock_type == "invite":
            invite = False
            perm = "invite"

        elif lock_type == "pin":
            pin = False
            perm = "pin"

        else:
            print(e)
            await msg(message, text="Something Happened Please Check logs.")
            return

        try:
            await client.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=msg,
                    can_send_media_messages=media,
                    can_send_stickers=stickers,
                    can_send_animations=animations,
                    can_send_games=games,
                    can_use_inline_bots=inlinebots,
                    can_add_web_page_previews=webprev,
                    can_send_polls=polls,
                    can_change_info=info,
                    can_invite_users=invite,
                    can_pin_messages=pin,
                ),
            )

            await msg(message, text=f"`Locked {perm} for this chat!`")
            await asyncio.sleep(5)
            await message.delete()

        except Exception as e:
            print(e)
            await msg(message, text="Something Happened Please Check logs.")
            return
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("unlock", Command))
async def unlock_permission(client, message):
    """this module unlocks group permission for admins"""
    if message.chat.type in ["group", "supergroup"]:
        cmd = message.command
        is_admin = await admin_check(message)
        if not is_admin:
            await message.delete()
            return

        umsg = ""
        umedia = ""
        ustickers = ""
        uanimations = ""
        ugames = ""
        uinlinebots = ""
        uwebprev = ""
        upolls = ""
        uinfo = ""
        uinvite = ""
        upin = ""
        uperm = ""  # pylint:disable=E0602

        unlock_type = " ".join(cmd[1:])
        chat_id = message.chat.id

        if not unlock_type:
            await msg(message, text="`can't unlock the void`")
            await asyncio.sleep(5)
            await message.delete()
            return

        get_uperm = await client.get_chat(chat_id)

        umsg = get_uperm.permissions.can_send_messages
        umedia = get_uperm.permissions.can_send_media_messages
        ustickers = get_uperm.permissions.can_send_stickers
        uanimations = get_uperm.permissions.can_send_animations
        ugames = get_uperm.permissions.can_send_games
        uinlinebots = get_uperm.permissions.can_use_inline_bots
        uwebprev = get_uperm.permissions.can_add_web_page_previews
        upolls = get_uperm.permissions.can_send_polls
        uinfo = get_uperm.permissions.can_change_info
        uinvite = get_uperm.permissions.can_invite_users
        upin = get_uperm.permissions.can_pin_messages

        if unlock_type == "all":
            try:
                await client.set_chat_permissions(
                    chat_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_stickers=True,
                        can_send_animations=True,
                        can_send_games=True,
                        can_use_inline_bots=True,
                        can_send_polls=True,
                        can_change_info=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                        can_add_web_page_previews=True,
                    ),
                )
                await msg(message, text="`Unlocked all permission from this Chat!`")
                await asyncio.sleep(5)
                await message.delete()

            except Exception as e:
                await msg(message, text="`permission denied`\n" f"**Log:** `{e}`")
            return

        if unlock_type == "msg":
            umsg = True
            uperm = "messages"

        elif unlock_type == "media":
            umedia = True
            uperm = "audios, documents, photos, videos, video notes, voice notes"

        elif unlock_type == "stickers":
            ustickers = True
            uperm = "stickers"

        elif unlock_type == "animations":
            uanimations = True
            uperm = "animations"

        elif unlock_type == "games":
            ugames = True
            uperm = "games"

        elif unlock_type == "inlinebots":
            uinlinebots = True
            uperm = "inline bots"

        elif unlock_type == "webprev":
            uwebprev = True
            uperm = "web page previews"

        elif unlock_type == "polls":
            upolls = True
            uperm = "polls"

        elif unlock_type == "info":
            uinfo = True
            uperm = "info"

        elif unlock_type == "invite":
            uinvite = True
            uperm = "invite"

        elif unlock_type == "pin":
            upin = True
            uperm = "pin"

        else:
            await msg(message, text="`Invalid Unlock Type!`")
            await asyncio.sleep(5)
            await message.delete()
            return

        try:
            await client.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=umsg,
                    can_send_media_messages=umedia,
                    can_send_stickers=ustickers,
                    can_send_animations=uanimations,
                    can_send_games=ugames,
                    can_use_inline_bots=uinlinebots,
                    can_add_web_page_previews=uwebprev,
                    can_send_polls=upolls,
                    can_change_info=uinfo,
                    can_invite_users=uinvite,
                    can_pin_messages=upin,
                ),
            )
            await msg(message, text=f"`Unlocked {uperm} for this chat!`")
            await asyncio.sleep(5)
            await message.delete()

        except Exception as e:
            await msg(message, text="`Error!`\n" f"**Log:** `{e}`")
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("vlock", Command))
async def view_perm(client, message):
    """view group permission."""
    if message.chat.type in ["group", "supergroup"]:
        v_perm = ""
        vmsg = ""
        vmedia = ""
        vstickers = ""
        vanimations = ""
        vgames = ""
        vinlinebots = ""
        vwebprev = ""
        vpolls = ""
        vinfo = ""
        vinvite = ""
        vpin = ""

        v_perm = await client.get_chat(message.chat.id)

        def convert_to_emoji(val: bool):
            if val:
                return "<code>True</code>"
            return "<code>False</code>"

        vmsg = convert_to_emoji(v_perm.permissions.can_send_messages)
        vmedia = convert_to_emoji(v_perm.permissions.can_send_media_messages)
        vstickers = convert_to_emoji(v_perm.permissions.can_send_stickers)
        vanimations = convert_to_emoji(v_perm.permissions.can_send_animations)
        vgames = convert_to_emoji(v_perm.permissions.can_send_games)
        vinlinebots = convert_to_emoji(v_perm.permissions.can_use_inline_bots)
        vwebprev = convert_to_emoji(v_perm.permissions.can_add_web_page_previews)
        vpolls = convert_to_emoji(v_perm.permissions.can_send_polls)
        vinfo = convert_to_emoji(v_perm.permissions.can_change_info)
        vinvite = convert_to_emoji(v_perm.permissions.can_invite_users)
        vpin = convert_to_emoji(v_perm.permissions.can_pin_messages)

        if v_perm is not None:
            try:
                permission_view_str = ""

                permission_view_str += "<b>Chat permissions:</b>\n"
                permission_view_str += f"<b>Send Messages:</b> {vmsg}\n"
                permission_view_str += f"<b>Send Media:</b> {vmedia}\n"
                permission_view_str += f"<b>Send Stickers:</b> {vstickers}\n"
                permission_view_str += f"<b>Send Animations:</b> {vanimations}\n"
                permission_view_str += f"<b>Can Play Games:</b> {vgames}\n"
                permission_view_str += f"<b>Can Use Inline Bots:</b> {vinlinebots}\n"
                permission_view_str += f"<b>Webpage Preview:</b> {vwebprev}\n"
                permission_view_str += f"<b>Send Polls:</b> {vpolls}\n"
                permission_view_str += f"<b>Change Info:</b> {vinfo}\n"
                permission_view_str += f"<b>Invite Users:</b> {vinvite}\n"
                permission_view_str += f"<b>Pin Messages:</b> {vpin}\n"
                await msg(message, text=permission_view_str)

            except Exception as e:
                await msg(message, text="`Error!`\n" f"**Log:** `{e}`")
    else:
        await message.delete()


@app.on_message(Filters.user(AdminSettings) & Filters.command("delacc", Command))
async def deleted_clean(client, message):
    cmd = message.command
    chat_id = message.chat.id
    get_group = await client.get_chat(chat_id)

    clean_tag = " ".join(cmd[1:])
    rm_delaccs = "clean" in clean_tag
    can_clean = await admin_check(message)

    del_stats = "`no deleted accounts found in this chat`"

    del_users = 0
    if rm_delaccs:

        if can_clean:
            await msg(message, text="`cleaning deleted accounts from this chat..`")
            del_admins = 0
            del_total = 0
            async for member in client.iter_chat_members(chat_id):

                if member.user.is_deleted:

                    try:
                        await client.kick_chat_member(
                            chat_id, member.user.id, int(time.time() + 45)
                        )

                    except UserAdminInvalid:
                        del_users -= 1
                        del_admins += 1

                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                    del_users += 1
                    del_total += 1

            del_stats = f"`Found` **{del_total}** `total accounts..`"
            await msg(message, text=del_stats)
            await message.edit(
                f"**Cleaned Deleted accounts**:\n"
                f"Total Deleted Accounts: `{del_total}`\n"
                f"Cleaned Deleted Accounts: `{del_users}`\n"
                f"Chat: `{get_group.title}` (`{chat_id}`)"
            )

        else:
            await msg(message, text="`permission denied`")

    else:

        async for member in client.iter_chat_members(chat_id):
            if member.user.is_deleted:
                del_users += 1
        if del_users > 0:
            del_stats = f"`Found` **{del_users}** `deleted accounts in this chat.`"
        await msg(message, text=del_stats)