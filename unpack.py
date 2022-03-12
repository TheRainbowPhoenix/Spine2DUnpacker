from typing import List

import yaml
from PIL import Image, ImageOps
import os

if not os.path.exists("images"):
    os.mkdir("images")


class SpineAltas:
    def __init__(self):
        self.size = [0, 0]
        self.format = ''
        self.map_fname = ''
        self.image = None
        self.filter = []
        self.repeat = ''

        self.scale = 1

        self.items = {}
        self._index = 0

    def read_headers(self, lines: List[str]):
        data_count = 0
        while self._index < len(lines):
            l = lines[self._index]
            if l == '':
                self._index += 1
                continue

            if data_count >= 5:
                break

            if l.endswith(".png"):
                self.map_fname = l
                self.image = Image.open(l)
                data_count += 1
            elif l.startswith("size: "):
                self.size = [int(i) for i in l.split(" ")[-1].split(",")]
                Iwidth, Iheight = self.image.size
                if self.size[0] != Iwidth:
                    self.scale = Iwidth/self.size[0]
                data_count += 1
            elif l.startswith("format: "):
                self.format = l.split(" ")[-1]
                data_count += 1
            elif l.startswith("filter: "):
                self.filter = l.split(" ")[-1].split(",")
                data_count += 1
            elif l.startswith("repeat: "):
                self.repeat = l.split(" ")[-1]
                data_count += 1
            else:
                print(f"Unknown line : \"{l}\"")

            self._index += 1

        if self.map_fname == "":
            raise Exception("No content in file !!")

    def read_blocs(self, lines: List[str]):
        current_item = ""
        while self._index < len(lines):
            l = lines[self._index]
            if l == '':
                self._index += 1
                continue

            if not ": " in l:
                current_item = l
                self.items[current_item] = {}
            # In a item and got whitespaces
            elif current_item != "" and l[0] in [' ', '\t']:
                ll: List[str] = l.strip().split(": ")
                if ll[0].startswith("rotate"):
                    self.items[current_item]["rotate"] = True if "true" in ll else False
                elif ll[0].startswith("xy"):
                    x, y = [int(i) for i in ll[-1].split(", ")]
                    self.items[current_item]["x"] = x
                    self.items[current_item]["y"] = y
                elif ll[0].startswith("size"):
                    x, y = [int(i) for i in ll[-1].split(", ")]
                    self.items[current_item]["size"] = {
                        'x': x,
                        'y': y
                    }
                # elif ll[0].startswith("orig"):
                #     self.items[current_item]["orig"] = [int(i) for i in ll[-1].split(", ")]
                elif ll[0].startswith("index"):
                    pass
                else:
                    print(f"Unknown line : \"{l}\"")

            self._index += 1

    def expot_img(self):
        for key in self.items:
            # if key != "CSB":
            #     continue
            item = self.items[key]

            im1 = self.image.crop((
                item['x'] * self.scale,
                item['y'] * self.scale,
                (item['x'] + item["size"]['x']) * self.scale,
                (item['y'] + item["size"]['y']) * self.scale
            ))

            if "rotate" in item and item["rotate"] == True:
                im1 = self.image.crop((
                    item['x'] * self.scale,
                    item['y'] * self.scale,
                    (item['x'] + item["size"]['y']) * self.scale,
                    (item['y'] + item["size"]['x']) * self.scale
                )).rotate(-90, expand=True)


            #     im1 = im1.rotate(item["rotate"])

            filename = f"images/{key}.png"
            # im1.show()
            im1.save(filename, "PNG")




if __name__ == '__main__':
    import sys

    atlas_fname = "HCG_Boss4.atlas"
    map_fname = ""

    atlas = SpineAltas()

    with open(atlas_fname, 'r') as file:
        lines = [i.rstrip() for i in file.readlines()]

    atlas.read_headers(lines)
    atlas.read_blocs(lines)
    atlas.expot_img()

    print(atlas.items)


