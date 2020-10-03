# SPDX-License-Identifier: GPL-2.0-or-later

from asyncbooru import Gelbooru
from telethon import Button
from ubot import ldr

gelbooru_api = Gelbooru(ldr.aioclient)
gel_button_dict = {}
help_string = "Fetches images from Gelbooru, takes tags as arguments."


@ldr.add_list(["gel", "gelx", "gelq"], pattern_extra="(f|)", nsfw=True, userlocking=True, help=help_string)
@ldr.add("gels", pattern_extra="(f|)", userlocking=True, help=help_string)
async def gelbooru(event):
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
    posts = await gelbooru_api.get_random_posts(event.args, 3, safety_arg)

    if not posts:
        await event.reply(f"No results for query: {event.args}")
        return

    images = [[post.file_url, post.sauce] for post in posts if post.file_url]

    if not images:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    for image in images:
        try:
            await event.reply(f"[sauce]({image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("gel(s|x|q|)", default="gel")
async def gelbooru_inline(event):
    posts = await gelbooru_api.get_random_posts(event.args, 3, event.other_args[0])
    return [[post.file_url, f"[sauce]({post.sauce})"] for post in posts if post.file_url] if posts else None


@ldr.add("gelb", nsfw=True, userlocking=True)
async def gelbooru_buttons(event):
    posts = await gelbooru_api.get_random_posts(event.args, 30)

    if not posts:
        await event.reply(f"No results for query: {event.args}")
        return

    images = [[post.file_url, post.sauce] for post in posts if post.file_url]

    if not images:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    gel_button_dict[f"{event.chat.id}_{event.id}"] = [0, images]

    await event.reply(
        f"[sauce]({images[0][1]})",
        file=images[0][0],
        buttons=[Button.inline('➡️', f'gel*{event.chat.id}_{event.id}*r')]
    )


@ldr.add_callback_query("gel")
async def gelbooru_buttons_callback(event):
    args_split = event.args.split("*")

    dict_id = args_split[0]
    direction = args_split[1]

    if dict_id in gel_button_dict:
        this_dict = gel_button_dict[dict_id]
    else:
        return

    if direction == "r":
        this_dict[0] += 1

        if this_dict[0] + 1 > len(this_dict[1]):
            this_dict[0] = len(this_dict[1]) - 1

        this_image = this_dict[1][this_dict[0]]
    elif direction == "l":
        this_dict[0] -= 1

        if this_dict[0] < 0:
            this_dict[0] = 0

        this_image = this_dict[1][this_dict[0]]

    buttons = []

    if this_dict[0] > 0:
        buttons += [Button.inline('⬅️', f'gel*{dict_id}*l')]

    if len(this_dict[1]) - 1 > this_dict[0]:
        buttons += [Button.inline('➡️', f'gel*{dict_id}*r')]

    try:
        await event.edit(
            f"[sauce]({this_image[1]})",
            file=this_image[0],
            buttons=buttons
        )
    except:
        pass
