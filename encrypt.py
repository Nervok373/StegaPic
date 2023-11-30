import random

from PIL import Image, ImageDraw


def stego_encrypt(path_img: str, text: str,
                  keys_file_path: str, encrypt_img_path: str,
                  mood: str, key_word="") -> bool:
    """
    Encrypting text in image

    :param path_img:
        the path to the image that is being recorded, with extension

    :param text:
        the text that is written to the image

    :param keys_file_path:
        if mood==2 then the path to the .txt file to which the modified pixels are written.
        without the .txt extension in the name. For example: tmp/img/keys_file

    :param encrypt_img_path:
        the path to save the finished image, without extension

    :param mood:
        1: without writing pixels to a separate file
        2: with writing pixels to a separate file, need keys_file_path

    :param key_word:
        seed for random generator, if None then random.randint(-10000, 10000)

    :return: True or False if Exception
    """

    try:
        keys = []
        img = Image.open(path_img)
        img = img.convert('RGB')
        pix = img.load()

        draw = ImageDraw.Draw(img)
        width = img.size[0]
        height = img.size[1]
        if mood == "1":
            random.seed(key_word if key_word else random.randint(-10000, 10000))
        elif mood == "2":
            f = open(f'{keys_file_path}.txt', 'w')

        for elem in ([ord(elem) for elem in text]):
            key = (random.randint(1, width - 10),
                   random.randint(1, height - 10))
            while key in keys:
                key = (random.randint(1, width - 10),
                       random.randint(1, height - 10))
            keys.append(key)

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

            if elem > 1000:
                elem = elem - 898

            residue = elem % 3

            if mood == "2":
                f.write(str(key) + '\n')

            if residue == 0:
                elem = elem//3
                draw.point(key, (rgb_average[0]+elem, rgb_average[1]+elem, rgb_average[2]+elem))
            else:
                elem = (elem-residue)//3
                draw.point(key, (rgb_average[0]+elem, rgb_average[1]+elem, rgb_average[2]+elem+residue))

        # для определения конца сообщения
        if mood == "1":
            key = (random.randint(1, width - 10),
                   random.randint(1, height - 10))
            while key in keys:
                key = (random.randint(1, width - 10),
                       random.randint(1, height - 10))
            keys.append(key)

            draw.point(key, (55, 66, 77))

        img.save(f"{encrypt_img_path}.png")
        if mood == "2":
            f.close()

        return True

    except Exception as e:
        return False
