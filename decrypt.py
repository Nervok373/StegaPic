from PIL import Image
from re import findall


def stega_decrypt(path_img:str, keys_file_path:str) -> str:
    a = []
    text = []
    keys = []
    img = Image.open(path_img)
    pix = img.load()
    f = open(keys_file_path, 'r')
    y = str([line.strip() for line in f])

    for i in range(len(findall(r'\((\d+)\,', y))):
        keys.append((int(findall(r'\((\d+)\,', y)[i]),
                     int(findall(r'\,\s(\d+)\)', y)[i])))

    for key in keys:
        a.append(pix[key])

    for e in a:
        e = sum(e)
        if e > 126:
            e += 898
            text.append(chr(e))
        else:
            text.append(chr(e))


    return ''.join(text)
