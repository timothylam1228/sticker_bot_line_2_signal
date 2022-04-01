import os
import glob

from signalstickers_client import StickersClient
from signalstickers_client.models import LocalStickerPack, Sticker


def add_sticker(pack, path, emoji):
    stick = Sticker()
    stick.id = pack.nb_stickers
    stick.emoji = emoji
    for filename in glob.glob(path+"/*.png"):
        with open(filename, "rb") as f_in:
            stick.image_data = f_in.read()

    pack._addsticker(stick)


async def createPackage(title, author, file_path):
    pack = LocalStickerPack()

    # Set here the pack title and author
    pack.title = title
    pack.author = author

    # Add the stickers here, with their emoji
    # Accepted format:
    # - Non-animated webp
    # - PNG
    # - GIF <100kb for animated stickers
    all_sticker = glob.glob(file_path+"/*.png")
    for filename in all_sticker:  # assuming gif
        add_sticker(pack, filename, "😃")

    # Specifying a cover is optionnal
    # By default, the first sticker is the cover
    cover = Sticker()
    cover.id = pack.nb_stickers
    # Set the cover file here
    with open(all_sticker[0], "rb") as f_in:
        cover.image_data = f_in.read()
    pack.cover = cover

    # Instanciate the client with your Signal crendentials
    async with StickersClient(os.environ['SIGNAL_USERNAME'], os.environ['SIGNAL_PASSWORD']) as client:
        # Upload the pack
        pack_id, pack_key = await client.upload_pack(pack)

    print("Pack uploaded!\n\nhttps://signal.art/addstickers/#pack_id={}&pack_key={}".format(pack_id, pack_key))
