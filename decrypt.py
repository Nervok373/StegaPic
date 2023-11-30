import random

from PIL import Image
from re import findall


def stego_decrypt(path_img: str, keys_file_path: str,
                  mood=str, key_word="") -> dict:
    """
    Decrypting text from image

    :param path_img:
        the path to the image that is being decryption, with extension

    :param keys_file_path:
        the path to txt file(path without .txt extension) with pixels cords

    :param mood:
        1: pixels from random generator
        2: pixels from keys_file_path

    :param key_word:
        seed for random generator, if None then random.randint(-10000, 10000)

    :return: dict with "ok": True or False, and "text" with text from img or Exception
    """

    if mood == "1":
        try:
            img = Image.open(path_img)
            width = img.size[0]
            height = img.size[1]

            pix = img.load()
            random.seed(key_word if key_word else random.randint(-10000, 10000))
            keys, text = [], []

            loop = True
            while loop:
                key = (random.randint(1, width - 10),
                       random.randint(1, height - 10))
                while key in keys:
                    key = (random.randint(1, width - 10),
                           random.randint(1, height - 10))
                keys.append(key)

                if pix[key] == (55, 66, 77):
                    loop = False
                else:
                    e = sum(pix[key])
                    if e > 126:
                        e += 898
                        text.append(chr(e))
                    else:
                        text.append(chr(e))

            return {"ok": True, "text": ''.join(text)}

        except Exception as e:
            return {"ok": False, "text": e}

    elif mood == "2":
        try:
            a, text, keys = [], [], []
            img = Image.open(path_img)
            img = img.convert('RGB')
            pix = img.load()

            f = open(keys_file_path, 'r')
            y = str([line.strip() for line in f])

            for i in range(len(findall(r'\((\d+)\,', y))):
                keys.append((int(findall(r'\((\d+)\,', y)[i]),
                             int(findall(r'\,\s(\d+)\)', y)[i])))

            for key in keys:
                a.append(pix[key])

            # сглаживание
            around = [pix[(key[0]-1, key[1]-1)], pix[(key[0], key[1]-1)], pix[(key[0]+1, key[1]-1)],
                      pix[(key[0]-1, key[1])],                            pix[(key[0]+1, key[1])],
                      pix[(key[0]-1, key[1]+1)], pix[(key[0], key[1]+1)], pix[(key[0]+1, key[1]+1)]]

            rgb_average = [[], [], []]
            for i in around:
                rgb_average[0].append(i[0]),
                rgb_average[1].append(i[1]),
                rgb_average[2].append(i[2])

            rgb_average[0] = (sum(rgb_average[0]) // len(rgb_average[0]))-50
            rgb_average[1] = (sum(rgb_average[1]) // len(rgb_average[1]))-50
            rgb_average[2] = (sum(rgb_average[2]) // len(rgb_average[2]))-50
            # ---

            for e in a:
                e[0] -= rgb_average[0]
                e[1] -= rgb_average[1]
                e[2] -= rgb_average[2]

                e = sum(e)
                if e > 126:
                    e += 898
                    text.append(chr(e))
                else:
                    text.append(chr(e))

            return {"ok": True, "text": ''.join(text)}

        except Exception as e:
            return {"ok": False, "text": e}
