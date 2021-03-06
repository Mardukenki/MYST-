# Original source for the deepfrying code (used under the following license): https://github.com/Ovyerus/deeppyer

# MIT License
#
# Copyright (c) 2017 Ovyerus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
from random import randint, uniform

from PIL import Image, ImageEnhance

from ubot import ldr


@ldr.add("deepfry", pattern_extra="(f|)", userlocking=True, help="Deepfries images, takes a number of passes as an argument.")
async def deepfryer(event):
    as_file = bool(event.other_args[0])

    try:
        frycount = int(event.args)
        if frycount < 1:
            frycount = 1
        elif frycount > 10:
            frycount = 10
    except ValueError:
        frycount = 1

    data = await event.get_image()

    if not data:
        await event.reply("Reply to an image or sticker or caption an image to deep fry it!")
        return

    # Download photo (highres) as byte array
    image = io.BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    for _ in range(frycount):
        image = await ldr.run_async(deepfrysync, image)

    fried_io = io.BytesIO()
    fried_io.name = "image.png"
    image.save(fried_io, "PNG")
    fried_io.seek(0)

    await event.respond(file=fried_io, force_document=as_file, reply_to=event.reply_to_msg_id or event.id)


def deepfrysync(img):
    # Generate color overlay
    overlay = img.copy()
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(0.7, 1.8))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(0.8, 1.3))
    overlay = ImageEnhance.Color(overlay).enhance(uniform(0.7, 1.4))

    # Blend random colors onto and sharpen the image
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 200))

    return img
