from asyncbooru import Danbooru, Gelbooru, Konachan, Sankaku, Yandere
from telethon import Button
from ubot import ldr

help_str = "Fetches images from Danbooru, Gelbooru, Konachan, Sankaku Complex and Yandere, takes tags as arguments."

dan_api = Danbooru(ldr.aioclient)
gel_api = Gelbooru(ldr.aioclient)
kon_api = Konachan(ldr.aioclient)
san_api = Sankaku(ldr.aioclient)
yan_api = Yandere(ldr.aioclient)

dan_butt = {}
gel_butt = {}
kon_butt = {}
san_butt = {}
yan_butt = {}

normal_commands = {
    "dan": dan_api,
    "gel": gel_api,
    "kon": kon_api,
    "san": san_api,
    "yan": yan_api
}

button_commands = {
    "danb": [dan_api, dan_butt, "dan"],
    "gelb": [gel_api, gel_butt, "gel"],
    "konb": [kon_api, kon_butt, "kon"],
    "sanb": [san_api, san_butt, "san"],
    "yanb": [yan_api, yan_butt, "yan"]
}


@ldr.add_dict(normal_commands, pattern_extra="(s)(f|)", help=help_str, userlocking=True)
@ldr.add_dict(normal_commands, pattern_extra="(x|q|)(f|)", userlocking=True, nsfw=True, nsfw_warning="NSFW commands are disabled in this chat, add 's' to the end of the command for SFW images.", hide_help=True)
async def booru(event):
    posts = await event.extra.get_random_posts(event.args, 3, event.other_args[0])

    if not posts:
        await event.reply(f"No results for query: {event.args}")
        return

    images = [[post.file_url, post.sauce, post.source] for post in posts if post.file_url]

    if not images:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    for image in images:
        try:
            await event.reply(f"[sauce]({image[1]}) [original sauce]({image[2]})" if image[2] else f"[sauce]({image[1]})", file=image[0], force_document=bool(event.other_args[1]))
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("dan(s|x|q|)", default="dan", extra=dan_api)
@ldr.add_inline_photo("gel(s|x|q|)", default="gel", extra=gel_api)
@ldr.add_inline_photo("kon(s|x|q|)", default="kon", extra=kon_api)
@ldr.add_inline_photo("san(s|x|q|)", default="san", extra=san_api)
@ldr.add_inline_photo("yan(s|x|q|)", default="yan", extra=yan_api)
async def booru_inline(event):
    posts = await event.extra.get_random_posts(event.args, 3, event.other_args[0])
    return [[post.file_url, f"[sauce]({post.sauce}) [original sauce]({post.source})" if post.source else f"[sauce]({post.sauce})"] for post in posts if post.file_url] if posts else None


@ldr.add_dict(button_commands, pattern_extra="(s)", help=help_str, userlocking=True)
@ldr.add_dict(button_commands, pattern_extra="(x|q|)", userlocking=True, nsfw=True, nsfw_warning="NSFW commands are disabled in this chat, add 's' to the end of the command for SFW images.", hide_help=True)
async def booru_buttons(event):
    posts = await event.extra[0].get_random_posts(event.args, 30, event.other_args[0])

    if not posts:
        await event.reply(f"No results for query: {event.args}")
        return

    images = [[post.file_url, post.sauce, post.source] for post in posts if post.file_url]

    if not images:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    event.extra[1][f"{event.chat.id}_{event.id}"] = [0, images]

    await event.reply(
        f"[sauce]({images[0][1]}) [original sauce]({images[0][2]})" if images[0][2] else f"[sauce]({images[0][1]})",
        file=images[0][0],
        buttons=[Button.inline('??????', f'{event.extra[2]}*{event.chat.id}_{event.id}*r')]
    )


@ldr.add_callback_query("dan", extra=dan_butt)
@ldr.add_callback_query("gel", extra=gel_butt)
@ldr.add_callback_query("kon", extra=kon_butt)
@ldr.add_callback_query("san", extra=san_butt)
@ldr.add_callback_query("yan", extra=yan_butt)
async def booru_buttons_callback(event):
    args_split = event.args.split("*")

    dict_id = args_split[0]
    direction = args_split[1]

    if dict_id in event.extra:
        this_dict = event.extra[dict_id]
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
        buttons += [Button.inline('??????', f'{event.command}*{dict_id}*l')]

    if len(this_dict[1]) - 1 > this_dict[0]:
        buttons += [Button.inline('??????', f'{event.command}*{dict_id}*r')]

    try:
        await event.edit(
            f"[sauce]({this_image[1]}) [original sauce]({this_image[2]})" if this_image[2] else f"[sauce]({this_image[1]})",
            file=this_image[0],
            buttons=buttons
        )
    except:
        pass
