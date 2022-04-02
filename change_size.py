from PIL import Image, ImageSequence,ImageOps
from PIL import features
from apng import APNG
import time
import glob
import os
import cv2
import numpy as np
from apng_square_and_optimize import *

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
    x, y, z = 0, 0, 0
    pix = img.load()
    img.thumbnail((expected_size[0], expected_size[1]))
    # print(img.size)
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding, fill=(0,0,0,0))

def resize_png(img_path, expected_size, png_file_size):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    height, width, channels = img.shape
    new_height, new_width = expected_size
    delta_width = new_width - width
    delta_height = new_height - height
    pad_width = delta_width // 2
    pad_height = delta_height // 2

    img_with_border = cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
    # img_with_border = img
    cv2.imwrite(img_path, img_with_border, [int(cv2.IMWRITE_PNG_COMPRESSION), 80])

    img_file_size = os.path.getsize(img_path)
    if(png_file_size < img_file_size):
        img = Image.open(img_path)
        assert img.mode == 'RGBA'
        out_pil = img.convert(mode="P", palette=Image.ADAPTIVE)
        out_pil.save(img_path, "PNG", quality=95, optimize=True)
        #img = img.convert("P", palette=Image.ADAPTIVE, colors=256)


def resize_apng(path, img, fn):
    i = 0
    im_list = []
    path = path+"\\"+str(fn).split('\\')[-1].split('.')[0]
    os.makedirs(path, exist_ok=True)
    frame_len = len(img.frames)
    png_file_size = 300 * 1024 / frame_len
    for png, control in img.frames:
        filename = path+"\{i}.png".format(i=i)
        png.save(filename)
        img = resize_png(filename, [512,512], int(png_file_size))
       # img = resize_with_padding(Image.open(filename), [512, 512])
        #img = img.save(filename, 'PNG')
        im_list.append(img)
        i+=1
    apngImg = APNG()
    for filename in glob.glob(path + "/*.png"):
        apngImg.append_file(filename)
    return apngImg


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
                image = Image.open(open("image/{i}.png".format(i=i), 'rb'))
                image = resize_with_padding(image, [512,512])
                image.save("image/{i}-{i}.png".format(i=i),optimize=True,quality=30)
                os.remove("image/{i}.png".format(i=i))
                im_list.append(image)
                i += 1
            apng_image=[]
            path = r"image/*.png"

            for filename in glob.glob(path): #assuming gif
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
