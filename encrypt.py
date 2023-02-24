from PIL import Image, ImageDraw
from random import randint


def stega_encrypt(path_img:str, text:str,
                  keys_file_path:str, encrypt_img_path:str) -> (str, str):
    keys = []
    img = Image.open(path_img)

    draw = ImageDraw.Draw(img)
    width = img.size[0]
    height = img.size[1]
    f = open(f'{keys_file_path}.txt', 'w')

    for elem in ([ord(elem) for elem in text]):
        key = (randint(1, width - 10), randint(1, height - 10))
        while key in keys:
            key = (randint(1, width - 10), randint(1, height - 10))
        keys.append(key)

        if elem > 1000:
            elem = elem - 898

        residue = elem%3
        if residue==0:
            elem = elem//3
            draw.point(key, (elem, elem, elem))
            f.write(str(key) + '\n')
        else:
            elem = (elem-residue)//3
            draw.point(key, (elem, elem, elem+residue))
            f.write(str(key) + '\n')

    img.save(f"{encrypt_img_path}.png", "PNG")
    f.close()
