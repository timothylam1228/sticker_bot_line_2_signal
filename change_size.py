from PIL import Image, ImageSequence,ImageOps
from PIL import features
from apng import APNG
import time
import glob
import os
from scripts.apng_square_and_optimize import *

newsize = (512, 512)
im2 = APNG()
basewidth = 512

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
    # print(img.size)
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)

def create_animated_sticker(rootdir):
    k = 0

    for file in os.listdir(rootdir):
        i = 0
        base, extension = os.path.splitext(file)
        print(extension)
        if extension == '.apng':
            file = os.path.join(rootdir,file)
            im = APNG.open(file)
            im_list = []
            for png, control in im.frames:
                png.save("image/{i}.png".format(i=i))
                image = Image.open("image/{i}.png".format(i=i))
                image = resize_with_padding(image, [512,512])
                image.save("image/{i}-{i}.png".format(i=i),optimize=True,quality=30)
                os.remove("image/{i}.png".format(i=i))
                im_list.append(image)
                i += 1
            apng_image=[]
            path = r"image/*.png"

            for  filename in glob.glob(path): #assuming gif
                print(filename)
                apng_image.append(filename)

            img = im_list[0]
            imgs = im_list[1:]
            APNG.from_files(apng_image, delay=100).save("result-{k}.apng".format(k=k))
            # with open("result-{k}.apng".format(k=k), "rb") as image:
            #     f = image.read()
            #     b = bytearray(f)
            #     print (b[0])
            img.save("output_webp-{k}.webp".format(packname=rootdir,k=k), save_all=True, append_images=imgs, duration=50, loop=0, optimize=False, disposal=2,quality = 50)

            for temp in glob.glob(path):
                os.remove(temp)
            k = k +1
            print('start',k)
