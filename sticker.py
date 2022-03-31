'''Line sticker downloader'''
from PIL import Image, ImageSequence,ImageOps
import requests
import sys
import os
from os import listdir
from os.path import isfile, join
import glob
import re
import codecs
import zipfile
from apng import PNG, APNG
import subprocess
from change_size import *
#from scripts.apng_square_and_optimize import *
im2 = APNG()
basewidth = 512


def main():
    pack_ext = ""

    if len(sys.argv) > 1:
        pack_id = int(sys.argv[1])
        if len(sys.argv) > 2:
            pack_ext = sys.argv[2]
    else:
        pack_id = int(input("Enter the sticker pack ID: "))
    pack_meta = get_pack_meta(pack_id).text

    name_string = """"en":"""  # folder name will take pack's English title
    pack_name = get_pack_name(name_string, pack_meta)
    pack_name = decode_escapes(pack_name)
    pack_name = pack_name.strip()  # To remove empty sides spaces # Example Bug:  Sticker ID= 9721  Name= UNIVERSTAR BT21: Cuteness Overloaded! # noqa: E501
    print("\nThis pack contains stickers for", pack_name)

    if pack_ext == "":
        if """"hasAnimation":true""" in pack_meta:
            if sys.version_info[0] < 3:
                # https://stackoverflow.com/questions/31722883/python-nameerror-name-hello-is-not-defined
                # compatibility python v2
                pack_ext = input("\nAnimated stickers available! \n"
                                 "Enter png, apng, or both, anything else to exit: ")  # noqa: E501
            else:
                pack_ext = input("\nAnimated stickers available! \n"
                                 "Enter png, apng, or both, anything else to exit: ")  # noqa: E501

        else:
            if sys.version_info[0] < 3:
                # https://stackoverflow.com/questions/31722883/python-nameerror-name-hello-is-not-defined
                # compatibility python v2
                pack_ext = input("\nOnly static stickers available! \n"
                                 "y to download, anything else to exit: ")
            else:
                pack_ext = input("\nOnly static stickers available! \n"
                                 "y to download, anything else to exit: ")

    id_string = """"id":"""
    list_ids = []

    current_id, start_index = 0, 0  # [4] Why have start_index included

    while start_index != -1:
        start_index, current_id, pack_meta = get_ids(id_string, pack_meta)
        # "Passing by assignment" mutable vs. immutable. Any reassignments done in called function will not reflect on return. But manipulating the parameter will reflect. # noqa: E501
        list_ids.append(current_id)

    list_ids.pop()  # [4] Why pop

    # [3] A less ugly way of checking menu values
    menu = {'apng': (get_gif,),
            'png': (get_png,),
            'y': (get_png,),
            'both': (get_gif, get_png)}  # D'OH! Originally said tuples wouldn't work, which was strange. Thanks to doing MIT problems, I realized I used (var) instead of (var,). Former will not be considered a tuple. # noqa: E501
    if pack_ext in menu:
        for choice in menu[pack_ext]:
            choice(pack_id, list_ids, pack_name)
    else:
        print("Nothing done. Program exiting...")
        sys.exit()

    print("\nDone! Program exiting...")

    sys.exit()


def get_pack_name(name_string, pack_meta):
    start_index = pack_meta.find(name_string)
    end_index = pack_meta.find(',', start_index + 1)
    sticker_name = pack_meta[start_index+len(name_string)+1:end_index-1]  # lower bound needs +1 to exclude the beginning " mark. -1 to make upper bound the , which is excluded from the range # noqa: E501
    return sticker_name


def get_ids(id_string, pack_meta):
    start_index = pack_meta.find(id_string)
    end_index = pack_meta.find(",", start_index + 1)
    sticker_id = pack_meta[start_index+len(id_string):end_index]
    return start_index, sticker_id, pack_meta[end_index:]


def validate_savepath(pack_name):
    decoded_name = decode_escapes(pack_name)
    save_name = "".join(i for i in decoded_name if i not in r'\/:*?"<>|')

    # python version selection
    if sys.version_info[0] < 3:
        # https://github.com/bamos/dcgan-completion.tensorflow/issues/20
        # compatibility python v2
        try:
            os.makedirs(str(save_name))
        except OSError:
            print("Skipping creation of %s because it exists already." % str(save_name))  # noqa: E501
    else:
        # python version >= 3
        os.makedirs(str(save_name), exist_ok=True)  # exist_ok = True doesn't raise exception if directory exists. Files already in directory are not erased # noqa: E501

    return save_name


def get_gif(pack_id, list_ids, pack_name):
    pack_name = validate_savepath(pack_name)

    url = 'http://dl.stickershop.LINE.naver.jp/products/0/0/1/{}/iphone/stickerpack@2x.zip'.format(pack_id)
    filename = str(pack_id) + "-"+ url.split('/')[-1]
    save_path = os.path.join('output',str(pack_name), filename)
    upzip_path = os.path.join('output',str(pack_name), 'upzip')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    os.makedirs(os.path.dirname(upzip_path), exist_ok=True)
    resize_path = os.path.join('output',str(pack_name), 'resize')
    os.makedirs(resize_path, exist_ok=True)
    animation_path = os.path.join('output', str(pack_name), 'upzip', "animation@2x")
    req = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(req.content)
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(upzip_path)

    files = [f for f in listdir(animation_path) if isfile(join(animation_path, f))]
    for filename in glob.glob(animation_path+"/*.png"):
        image = APNG.open(filename)
        apngFile = resize_apng(animation_path, image, filename)
        apngFile.save(resize_path+"\\" + str(filename).split('\\')[-1])





def get_gif1(pack_id, list_ids, pack_name):
    pack_name = validate_savepath(pack_name)
    i = 0
    for x in list_ids:
        save_path = os.path.join('output',str(pack_name), str(x) + '.apng')
        #url = 'https://sdl-stickershop.line.naver.jp/products/0/0/1/{}/iphone/animation/{}@2x.png'.format(pack_id, x)  # noqa: E501
        url = 'http://dl.stickershop.LINE.naver.jp/products/0/0/1/{}/iphone/stickerpack@2x.zip'.format(pack_id)
        image = requests.get(url, stream=True)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        i = i + 1
        with open(save_path, 'wb') as f:
            for chunk in image.iter_content(chunk_size=10240):
                if chunk:
                    # print(image_temp)
                    # image_temp.save('result.apng')
                    f.write(chunk)
                        # image.save("result.apng")
                        # f.write(chunk)
        image_temp = APNG.open(save_path)
        temp = resize(image_temp.to_bytes())
        temp.save(save_path)


    
def get_png(pack_id, list_ids, pack_name):
    pack_name = validate_savepath(pack_name)
    for x in list_ids:
        save_path = os.path.join(str(pack_name), str(x) + '.png')
        url = 'http://dl.stickershop.line.naver.jp/stickershop/v1/sticker/{}/iphone/sticker@2x.png'.format(x)  # noqa: E501
        image = requests.get(url, stream=True)
        with open(save_path, 'wb') as f:  # http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py Understood! with construct is a fancy way of try/catch that cleans up, even with exceptions thrown  # noqa: E501
            for chunk in image.iter_content(chunk_size=10240):  # chunk_size is in bytes # noqa: E501
                if chunk:
                    f.write(chunk)
        output_path = os.path.join(str(pack_name),str(x))
        subprocess.run(['apngdis', save_path, output_path] )


def get_pack_meta(pack_id):

    pack_url = "http://dl.stickershop.line.naver.jp/products/0/0/1/{}/android/productInfo.meta".format(pack_id)  # noqa: E501
    pack_meta = requests.get(pack_url)

    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html Status codes
    # It seems that normal request gives 200. Not sure what it means for program if non200 code is given. Will work with 200 for now.  # noqa: E501

    if pack_meta.status_code == 200:
        return pack_meta
    else:
        print("{} did not return 200 status code, possibly invalid sticker ID. Program exiting...".format(pack_id))  # noqa: E501
        sys.exit()


unicode_sanitizer = re.compile(r'''  # compile pattern into object, use with match()
    ( \\U........      # 8-digit hex escapes, backslash U followed by 8 non-newline characters  # noqa: E501
    | \\u....          # 4-digit hex escapes, bksl u followed by 4 non-newline characters  # noqa: E501
    | \\x..            # 2-digit hex escapes, bksl x followed by 2 non-newline characters  # noqa: E501
    | \\[0-7]{1,3}     # Octal escapes, bksl followed by 1 to 3 numbers within range of 0-7  # noqa: E501
    | \\N\{[^}]+\}     # Unicode characters by name, uses name index
    | \\[\\'"abfnrtv]  # Single-character escapes, e.g. tab, backspace, quotes
    )''', re.VERBOSE)  # re.UNICODE not necessary in Py3, matches Unicode by default. re.VERBOSE allows separated sections  # noqa: E501


def decode_escapes(orig):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')
    return unicode_sanitizer.sub(decode_match, orig)  # sub returns string with replaced patterns  # noqa: E501




def padding(img, expected_size):
    desired_size = expected_size
    delta_width = desired_size - img.size[0]
    delta_height = desired_size - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)


def resize_with_padding(img, expected_size):
    img.thumbnail((expected_size[0], expected_size[1]))
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)


if __name__ == '__main__':
    main()


'''
[1] http://stackoverflow.com/questions/11435331/python-requests-and-unicode
Solve Unicode with r.content instead of r.text
[2] w+ creates file if it doesn't exist, truncates if it exists. b is for binary, Windows is picky. Never hurts to add b for platform friendliness
[3] http://stackoverflow.com/questions/3260057/how-to-check-variable-against-2-possible-values-python
leads to http://stackoverflow.com/questions/13186542/functions-in-python-dictionary
For multiple functions per key: http://stackoverflow.com/questions/9205081/python-is-there-a-way-to-store-a-function-in-a-list-or-dictionary-so-that-when
How clever.
http://stackoverflow.com/a/9139961 If I didn't have a check for key in dict, this would've been another way.
[4] Originally had a conditional in the while state to check if the start_index was -1 to make sure it doesn't get added.
But a single pop at the end is much better than the if check in every loop iteration.
[5] http://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python
Regular expression saves the day.
'''  # noqa: E501

'''
putting "# nopep8" (or "# noqa") on the last line of a multiline string disables all physical checks for lines in the string
https://github.com/PyCQA/pycodestyle/pull/243
'''