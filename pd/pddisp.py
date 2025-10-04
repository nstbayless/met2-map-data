import json
from PIL import Image
import os
import sys

if not os.path.exists("pd/pdimg.png"):
    print("Please run from the root directory")
    sys.exit(1)

halfgrid_x = 8
halfgrid_y = 8

grid_x = halfgrid_x*2
grid_y = halfgrid_y*2

MARGIN = 1

def split_image_into_tiles(image_path):
    img = Image.open(image_path)
    width, height = img.size
    tiles = {}
    
    print(f"{width}×{height}")

    for y in range(0, height, halfgrid_y):
        for x in range(0, width, halfgrid_x):
            box = (x, y, x + halfgrid_x, y + halfgrid_y)
            tile = img.crop(box)
            tiles[(x // halfgrid_y, y // halfgrid_y)] = tile

    return tiles

tiles = split_image_into_tiles("pd/pdimg.png" if len(sys.argv) < 2 else sys.argv[1])


output_dir = 'pd/preview'
os.makedirs(output_dir, exist_ok=True)

with open('met2.json', 'r') as f:
    met2 = json.load(f)
    
BIT_EAST = 1
BIT_WEST = 2
BIT_NORTH = 4
BIT_SOUTH = 8

BIT_DIAG_NW = 16
BIT_DIAG_SW = 32
BIT_DIAG_SE = 64
BIT_DIAG_NE = 128

bit_direction = {
    BIT_EAST: (1, 0),
    BIT_WEST: (-1, 0),
    BIT_NORTH: (0, -1),
    BIT_SOUTH: (0, 1),
}

TL = 0
TR = 1
BL = 2
BR = 3

NORMAL = 1
HPIPE = 2
VPIPE = 3
DARK = 4
ERROR = 5

DOOR_NORTH = 6
DOOR_WEST = 7
DOOR_SOUTH = 8
DOOR_EAST = 9

AREA_EXIT_NORTH = 10
AREA_EXIT_WEST = 11
AREA_EXIT_SOUTH = 12
AREA_EXIT_EAST = 13

HJUMP = 14
VJUMP = 15

NE_SHUNT_UPPER = 16
NE_SHUNT_LOWER = 17

DARK_DOOR_NORTH = 19
DARK_DOOR_WEST = 20
DARK_DOOR_SOUTH = 21
DARK_DOOR_EAST = 22

RECHARGE_ENERGY = 23
RECHARGE_MISSILE = 24
RECHARGE_BOTH = 25
ITEM = 26
SAVE = 27
ALPHA = 28
GAMMA = 29
ZETA = 30
OMEGA = 31
LARVA = 32
QUEEN = 33
UNKNOWN = 34
GUNSHIP_LEFT = 35
GUNSHIP_RIGHT = 36

FEATURE_TILES = {
    "missile-tank": ITEM,
    "energy-tank": ITEM,
    "screw-attack": ITEM,
    "bombs": ITEM,
    "ice": ITEM,
    "wave": ITEM,
    "spazer": ITEM,
    "plasma": ITEM,
    "bomb": ITEM,
    "spider": ITEM,
    "varia": ITEM,
    "high-jump": ITEM,
    "spring-ball": ITEM,
    "space-jump": ITEM,
    "screw-attack": ITEM,
    
    "save": SAVE,
    
    "energy-recharge": RECHARGE_ENERGY,
    "missile-recharge": RECHARGE_MISSILE,
    "both-recharge": RECHARGE_BOTH,
    
    "alpha": ALPHA,
    "hatch-alpha": ALPHA,
    "gamma": GAMMA,
    "zeta": ZETA,
    "omega": OMEGA,
    "larva": LARVA,
    "queen": QUEEN,
    "egg": UNKNOWN,
    "unknown": UNKNOWN,
    
    "ship-left": GUNSHIP_LEFT,
    "ship-right": GUNSHIP_RIGHT,
}

DOOR_TILE = {
    BIT_WEST: DOOR_WEST,
    BIT_NORTH: DOOR_NORTH,
    BIT_SOUTH: DOOR_SOUTH,
    BIT_EAST: DOOR_EAST,
}

DARK_DOOR_TILE = {
    BIT_WEST: DARK_DOOR_WEST,
    BIT_NORTH: DARK_DOOR_NORTH,
    BIT_SOUTH: DARK_DOOR_SOUTH,
    BIT_EAST: DARK_DOOR_EAST,
}

AREA_EXIT_TILE = {
    BIT_WEST: AREA_EXIT_WEST,
    BIT_NORTH: AREA_EXIT_NORTH,
    BIT_SOUTH: AREA_EXIT_SOUTH,
    BIT_EAST: AREA_EXIT_EAST,
}

def idx2x2(y, x):
    return [(y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)]

def draw_tile(dst, x, y, type, edgebits=0):
    if type <= 0:
        return
    
    idx = [(0, 1) for _ in range(4)]
    
    if edgebits & BIT_DIAG_NW:
        idx[TL] = (3, 0)
    if edgebits & BIT_DIAG_SW:
        idx[BL] = (3, 1)
    if edgebits & BIT_DIAG_SE:
        idx[BR] = (3, 2)
    if edgebits & BIT_DIAG_NE:
        idx[TR] = (3, 3)
    
    if edgebits & BIT_NORTH:
        idx[TL] = (1, 0)
        idx[TR] = (1, 0)
    if edgebits & BIT_WEST:
        idx[TL] = (1, 1)
        idx[BL] = (1, 1)
    if edgebits & BIT_SOUTH:
        idx[BL] = (1, 2)
        idx[BR] = (1, 2)
    if edgebits & BIT_EAST:
        idx[TR] = (1, 3)
        idx[BR] = (1, 3)
    
    if edgebits & BIT_WEST and edgebits & BIT_NORTH:
        idx[TL] = (2, 0)
    if edgebits & BIT_WEST and edgebits & BIT_SOUTH:
        idx[BL] = (2, 1)
    if edgebits & BIT_EAST and edgebits & BIT_SOUTH:
        idx[BR] = (2, 2)
    if edgebits & BIT_EAST and edgebits & BIT_NORTH:
        idx[TR] = (2, 3)
        
    if type == HPIPE:
        idx = [(5, 0), (5, 0), (5, 1), (5, 1)]
    if type == VPIPE:
        idx = [(5, 2), (5, 3), (5, 2), (5, 3)]
    if type == ERROR:
        idx = [(0, 3), (0, 3), (0, 3), (0, 3)]
    if type == DARK:
        for i, (yi, xi) in enumerate(idx):
            if (yi, xi) == (0, 2):
                idx[i] = (0, 3)
            else:
                idx[i] = (yi+6, xi)
    if type == DOOR_NORTH:
        idx = [(10, 0), (10, 1), (0, 3), (0, 3)]
    if type == DOOR_SOUTH:
        idx = [(0, 3), (0, 3), (11, 0), (11, 1)]
    if type == DOOR_WEST:
        idx = [(10, 3), (0, 3), (11, 3), (0, 3)]
    if type == DOOR_EAST:
        idx = [(0, 3), (10, 2), (0, 3), (11, 2)]
    if type == DARK_DOOR_NORTH:
        idx = [(18, 0), (18, 1), (0, 3), (0, 3)]
    if type == DARK_DOOR_SOUTH:
        idx = [(0, 3), (0, 3), (19, 0), (19, 1)]
    if type == DARK_DOOR_WEST:
        idx = [(18, 3), (0, 3), (19, 3), (0, 3)]
    if type == DARK_DOOR_EAST:
        idx = [(0, 3), (18, 2), (0, 3), (19, 2)]
    if type == AREA_EXIT_NORTH:
        idx = idx2x2(12, 0)
    if type == AREA_EXIT_WEST:
        idx = idx2x2(12, 2)
    if type == AREA_EXIT_SOUTH:
        idx = idx2x2(14, 0)
    if type == AREA_EXIT_EAST:
        idx = idx2x2(14, 2)
    if type == HJUMP:
        idx = [(6, 0), (6, 0), (6, 1), (6, 1)]
    if type == VJUMP:
        idx = [(6, 2), (6, 3), (6, 2), (6, 3)]
    if type == NE_SHUNT_LOWER:
        idx = idx2x2(16, 0)
    if type == NE_SHUNT_UPPER:
        idx = idx2x2(16, 2)
    if type == ITEM:
        idx = idx2x2(20, 0)
    if type == SAVE:
        idx = idx2x2(20, 2)
    if type == RECHARGE_ENERGY:
        idx = idx2x2(22, 0)
    if type == RECHARGE_MISSILE:
        idx = idx2x2(22, 2)
    if type == RECHARGE_BOTH:
        idx = idx2x2(24, 0)
    if type == ALPHA:
        idx = idx2x2(24, 2)
    if type == GAMMA:
        idx = idx2x2(26, 0)
    if type == ZETA:
        idx = idx2x2(26, 2)
    if type == OMEGA:
        idx = idx2x2(28, 0)
    if type == LARVA:
        idx = idx2x2(28, 2)
    if type == QUEEN:
        idx = idx2x2(30, 0)
    if type == UNKNOWN:
        idx = idx2x2(30, 2)
    if type == GUNSHIP_LEFT:
        idx = idx2x2(32, 0)
    if type == GUNSHIP_RIGHT:
        idx = idx2x2(32, 2)
    
    for yi in range(2):
        for xi in range(2):
            ty, tx = idx[yi*2 + xi]
            img = tiles[(tx, ty)]
            dst.paste(img, (int(x*2 + xi) * halfgrid_x, int(y*2 + yi) * halfgrid_y), img)

for area in met2["areas"] + [None]:
    if area:
        print(area["name"])
        x0 = area['x0']
        y0 = area['y0']
        x1 = area['x1']
        y1 = area['y1']
        name = area['name']
        rooms = area["rooms"]
    else:
        x0 = 0
        y0 = 0
        name = "world"
        x1 = met2["world"]["w"]
        y1 = met2["world"]["h"]
        rooms = range(len(met2["rooms"]))
        
    x0 -= MARGIN
    y0 -= MARGIN
    x1 += MARGIN
    y1 += MARGIN
    
    w = x1 - x0
    h = y1 - y0
    area_img = Image.new('RGBA', (w * grid_x, h * grid_y))
    blanktile = tiles[(0, 0)]
    for x in range(w):
        for y in range(h):
            for xi in range(2):
                for yi in range(2):
                    area_img.paste(blanktile, ((x*2 + xi) * halfgrid_x, (y*2 + yi) * halfgrid_y))
    
    for ridx in rooms:
        room = met2["rooms"][ridx]
        rx = room["x"]
        ry = room["y"]
        cells = room["cells"]
        for yoffset, row in enumerate(cells):
            for xoffset, cell in enumerate(row):
                edgebits = 0
                for (checkbit, dx, dy) in [(BIT_WEST, -1, 0), (BIT_NORTH, 0, -1), (BIT_EAST, 1, 0), (BIT_SOUTH, 0, 1), (BIT_DIAG_NW, -1, -1), (BIT_DIAG_SW, -1, 1), (BIT_DIAG_SE, 1, 1), (BIT_DIAG_NE, 1, -1)]:
                    nx = xoffset + dx
                    ny = yoffset + dy
                    if (nx < 0) or (ny < 0) or (nx >= len(row)) or (ny >= len(cells)):
                        edgebits |= checkbit
                    else:
                        if cells[ny][nx] <= 0:
                            edgebits |= checkbit
                if type(cell) != int:
                    print(cell, name, ridx)
                    cell = ERROR
                draw_tile(area_img, xoffset + rx - x0, yoffset + ry - y0, cell, edgebits)
    
    # doors
    for ridx in rooms:
        room = met2["rooms"][ridx]
        for door in room["doors"]:
            x = room["x"] + door["x"] - x0
            y = room["y"] + door["y"] - y0
            cell = room["cells"][door["y"]][door["x"]]
            dir = door["dir"]
            if (door["exit_states"]):
                if cell == NORMAL:
                    draw_tile(area_img, x, y, DOOR_TILE[dir])
                if cell == DARK:
                    draw_tile(area_img, x, y, DARK_DOOR_TILE[dir])
            if "to-area" in door:
                draw_tile(area_img, x + bit_direction[dir][0], y + bit_direction[dir][1], AREA_EXIT_TILE[dir])
            elif "jump" in door:
                ndx, ndy = door["jump"]
                if ndy == 0:
                    for i in range(min(x + ndx, x), max(x + ndx, x)):
                        if i != x + ndx and i != x:
                            draw_tile(area_img, i, y, HJUMP)
                elif ndy == -1 and ndx == 1:
                    draw_tile(area_img, x + 0.5, y, NE_SHUNT_LOWER)
                elif ndy == 1 and ndx == -1:
                    draw_tile(area_img, x - 0.5, y, NE_SHUNT_UPPER)
                    
    # features
    for ridx in rooms:
        room = met2["rooms"][ridx]
        roomfeatures = dict()
        if "features" in room:
            for feature in room["features"]:
                ftype = feature["type"]
                roomx = feature["x"]
                roomy = feature["y"]
                x = roomx + room["x"] - x0
                y = roomy + room["y"] - y0
                if ftype in FEATURE_TILES:
                    if (x, y) not in roomfeatures:
                        roomfeatures[(x, y)] = set()
                    roomfeatures[(x, y)].add(ftype)
                elif ftype == "ship":
                    roomfeatures[(x,y)] = {"ship-left"}
                    roomfeatures[(x+1,y)] = {"ship-right"}
                elif ftype == "arachnus":
                    roomfeatures[(x,y)] = {"unknown"}
                else:
                    print(f"unrecognized feature: {ftype}")
        
        for (x, y), roomfeature in roomfeatures.items():
            if "energy-recharge" in roomfeature and "missile-recharge" in roomfeature:
                roomfeature.add("both-recharge")
            if "alpha" in roomfeature and "omega" in roomfeature:
                roomfeature.add("unknown")
            if "spring-ball" in roomfeature:
                roomfeature.add("unknown")
            
            tile = max(FEATURE_TILES[feature] for feature in roomfeature)
            if tile >= 0:
                draw_tile(area_img, x, y, tile)
    
    area_img.save(os.path.join(output_dir, f"{name}.png"))