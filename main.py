from rosreestr2coord import Area
import io
import urllib.request
import random
from cairo import ImageSurface, FORMAT_ARGB32, Context
import mercantile
from tkinter import *

#Функция получение статической карты по промежуткам
def get_map(west, south, east, north, zoom):
    tiles = list(mercantile.tiles(west, south, east, north, zoom))

    min_x = min([t.x for t in tiles])
    min_y = min([t.y for t in tiles])
    max_x = max([t.x for t in tiles])
    max_y = max([t.y for t in tiles])

    tile_size = (256, 256)
    map_image = ImageSurface(
        FORMAT_ARGB32,
        tile_size[0] * (max_x - min_x + 1),
        tile_size[1] * (max_y - min_y + 1)
    )

    ctx = Context(map_image)

    for t in tiles:
        server = random.choice(['a', 'b', 'c'])
        url = 'http://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
            server=server,
            zoom=t.z,
            x=t.x,
            y=t.y
        )
        f = urllib.request.Request(url, headers={"User-agent": "My test app"})
        response = urllib.request.urlopen(f)
        img = ImageSurface.create_from_png(io.BytesIO(response.read()))

        ctx.set_source_surface(
            img,
            (t.x - min_x) * tile_size[0],
            (t.y - min_y) * tile_size[0]
        )
        ctx.paint()

    return {
        'image': map_image,
        'bounds': {
            "west": min([mercantile.bounds(t).west for t in tiles]),
            "east": max([mercantile.bounds(t).east for t in tiles]),
            "south": min([mercantile.bounds(t).south for t in tiles]),
            "north": max([mercantile.bounds(t).north for t in tiles]),
        }
    }

def main():
    def search():
        cad_num = entry.get()

        area = Area(cad_num)

        if Area(cad_num).get_coord() != []:

            coord = area.get_coord()

            west = coord[0][0][0][0]
            south = coord[0][0][0][1]
            east = coord[0][0][3][0]
            north = coord[0][0][3][1]

            zoom = 16
            out = get_map(west, south, east, north, zoom)

            leftTop = mercantile.xy(out['bounds']['west'], out['bounds']['north'])
            rightBottom = mercantile.xy(out['bounds']['east'], out['bounds']['south'])

            # расчитываем коэффициенты
            kx = out['image'].get_width() / (rightBottom[0] - leftTop[0])
            ky = out['image'].get_height() / (rightBottom[1] - leftTop[1])
            context = Context(out['image'])

            for c in coord[0][0]:
                x, y = mercantile.xy(c[0], c[1])
                x = (x - leftTop[0]) * kx
                y = (y - leftTop[1]) * ky

                context.line_to(x, y)

            c = coord[0][0][0]
            x, y = mercantile.xy(c[0], c[1])
            x = (x - leftTop[0]) * kx
            y = (y - leftTop[1]) * ky

            context.line_to(x, y)
            context.set_source_rgba(1, 0, 0, 0.5)
            context.set_line_width(3)
            context.stroke()


            with open("map_with_route.png", "wb") as f:
                out['image'].write_to_png(f)

            label["text"] = "Найдено"
            canvas.pack(padx=70)
        else:
            label["text"] = "Не найдено"
            canvas.pack_forget()
    root = Tk()
    entry = Entry()
    entry.pack(pady=10)
    #24:39:0101001:369
    bbt = Button(text="Поиск", width=20, command=search).pack(pady=10)

    label = Label()
    label.pack(pady=10)

    canvas = Canvas(root, height=400, width=700)
    img = PhotoImage(file='map_with_route.png')
    image = canvas.create_image(0, 0, anchor='nw', image=img)

    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2  # середина экрана
    h = h // 2
    w = w - 200  # смещение от середины
    h = h - 200
    root.geometry('400x400+{}+{}'.format(w, h))
    root.title("Тестовое")

    root.mainloop()




if __name__ == '__main__':
    main()
