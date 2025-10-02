import sys
from queue import PriorityQueue
from collections import deque
from table import Table
from display import *
from typing import Dict, Tuple
import json
import re
import copy

BIT_EAST = 1
BIT_WEST = 2
BIT_NORTH = 4
BIT_SOUTH = 8

DIRS = [
    BIT_EAST,
    BIT_WEST,
    BIT_NORTH,
    BIT_SOUTH,
]

REVERSE_DIRECTIONS = {
    BIT_EAST : BIT_WEST,
    BIT_WEST : BIT_EAST,
    BIT_NORTH : BIT_SOUTH,
    BIT_SOUTH : BIT_NORTH,
}

NO_REPLICATE = -1

def romaddr(bank, ramaddr):
    return 0x4000 * bank + (ramaddr % 0x4000)

SPAWN_ROOM_IDX = 1
SPAWN_AREA = "Surface"
AREA_2_LOWER = "Lower Chozo Temple"
AREA_2_UPPER = "Upper Chozo Temple"
AREA_3 = "Hydro Station"
AREA_4_UPPER = "Weapons Facility"
AREA_4_LOWER = "Jungle"
AREA_5 = "Tower"
AREA_6 = "Omega Environment"
FINAL_AREA = "Metroid Nest"

CAVES_1 = "Upper Acid Caves"
CAVES_2 = "Eastern Acid Caves"
CAVES_3 = "Lower Acid Caves"
CAVES_4 = "Western Acid Caves"

area_names = [
    SPAWN_AREA,
    CAVES_1,
    AREA_2_LOWER,
    AREA_2_UPPER,
    AREA_3,
    CAVES_2,
    AREA_4_LOWER,
    AREA_4_UPPER,
    CAVES_3,
    AREA_5,
    AREA_6,
    CAVES_4,
    FINAL_AREA
]

room_names = {
    0xF55: "Landing Site",
    0xA44: "Surface Corridor",
    0xFA6: "Morph Tutorial",
    0xC12: "Aim-Down Tutorial",
    0xF30: "First Save",
    0xF51: "Shallow Slime",
    0xF01: "First Alpha",
    0xBD0: "Wading Pool",
    
    0xA00: "First Acid",
    0xA90: "No Swimming Zone",
    0xA22: "No Diving Zone",
    0xB31: "Acid Pancakes",
    
    0xB11: "Temple Access",
    0xBA1: "Cullugg Pillar Room",
    0x95D: "Temple Exterior",
    0xD62: "Temple Save",
    0xD83: "Bomb Tutorial",
    0xDBD: "Wallfire Shaft",
    0xD54: "Bomb Access",
    0xD44: "Bomb Room",
    0xB11: "Pre-Temple Corridor",
    0xC20: "Pre-Temple Shaft",
    0xDB1: "Temple Shaft East",
    0xD72: "Temple Shaft West",
    0xD83: "Temple E-Tank Room",
    0xD95: "Temple Ice Beam Access",
    0xD85: "Temple Ice Beam Room",
    0xD81: "Double Missile Room",
    0xB1A: "Spider Access",
    0xE30: "Spider Room",
    0xDC4: "Triple Missile Room",
    0xE70: "Post-Spider Alpha",
    0xC31: "Cobweb's Treasure",
    0xB9A: "Pancake Access Shaft",
    0xBAB: "Pancake Room",
    0xBDB: "Pancake Alpha",
    0xB8B: "Not Pancake Access Shaft",
    0xB5C: "Not Pancake Room",
    0xB4C: "Not Pancake Alpha",
    0xB9C: "Not Not Pancake Alpha",
    0xB42: "Septogg Sandpits",
    0xB22: "Cawron Alpha",
    
    0x9D3: "Hydro Exterior",
    0xD75: "Hydro Save East",
    0xD25: "Hydro Save West",
    0xD7D: "High Jump Cache",
    0xA47: "Caves Fork",
    0xBBF: "Lower Octroll Alley",
    0xCA5: "Octroll Alley Shaft",
    0xB04: "Upper Octroll Alley",
    0xC40: "East Caves Entrance",
    0xA06: "Acid Dive Start",
    0xC9C: "Acid Dive Main Climb",
    0xC47: "Acid Dive Left Climb",
    0xC66: "Acid Dive Right Climb",
    0xB12: "Flying Flittway",
    0xA61: "Acid Alpha",
    0xB5F: "Vanishing Flittway",
    0xA62: "Acid Gamma",
    0x977: "Facility Exterior",
    0xE0B: "Autom E-Tank Room",
    0xE2B: "Autom Alpha",
    0xE7B: "Autom Alley",
    0xE3A: "Plasma Gamma",
    0xBCC: "Jungle Save",
    0xC3A: "Jungle Entrance",
    0xB7A: "Jungle Exit",
    0xC60: "Jungle Heart",
    0xB83: "Entangled Alpha",
    0xBB3: "Entangled Gamma",
    0xC91: "Jungle Descent",
    0xC88: "Jungle Floor",
    0xA28: "Quad-state Room",
    0xA66: "Missile Block Room",
    0x911: "Tower Exterior",
    0x912: "Dark Chamber",
    0xEA2: "Screw Attack Room",
    0xEA3: "Screw Zeta",
    0xEA4: "Non-Euclidean Room",
    0xEB5: "Tower Shaft",
    0xEA5: "Tower Plasma Room",
    0xEA6: "Tower Spazer Room",
    0xEA7: "Tower Wave Beam Room",
    0xEA8: "Tower Ice Beam Room",
    0xB76: "Tower Access",
    0xEAA: "Tower Save",
    0xA7E: "Loop Acid",
    0xC09: "Spike Barrier Room",
    0xAD8: "Jail",
    0xA99: "Final Save",
    0xFCB: "Soda Fountain",
    0xD02: "Egg Viewing Shaft",
    0xE3D: "Queen Recharge Room",
    0xE1D: "Queen's Retreat",
    0xE31: "Queen's Hallway",
    0xFEF: "Queen Fight",
}

object_names = {
    #0x75: "missile-block",
    #0xF8: "missile-door",
    #0x6D: "metroid-surprise",
    
    0x80: "plasma",
    0x82: "ice",
    0x84: "wave",
    0x86: "spazer",
    0x88: "bombs",
    0x8A: "screw-attack",
    0x8C: "varia",
    0x8E: "high-jump",
    
    0x90: "space-jump",
    0x93: "spider",
    0x97: "energy-tank",
    0x99: "missile-tank",
    0x9B: "energy-recharge",
    0x9C: "spring-ball",
    0x9D: "missile-recharge",
    
    0xA0: "alpha",
    0xA3: "gamma",
    0xA4: "alpha",
    0xA6: "egg",
    0xAD: "zeta",
    0xB3: "omega",
    0xCE: "larva",
    
    #0xDB: "fake-egg",
}

#FDX = -6
#FDY = 0
FDX = 5
FDY = -6

AREA_COLORS = {
    SPAWN_AREA: (100, 130, 200),
    
    AREA_2_LOWER: (130, 100, 90),
    AREA_2_UPPER: (150, 130, 60),
    
    AREA_3: (100, 130, 170),
    
    CAVES_1: (150, 80, 50),
    CAVES_2: (140, 80, 100),
    
    AREA_4_UPPER: (160, 160, 80),
    AREA_4_LOWER: (40, 100, 30),
    
    CAVES_3: (130, 40, 20),
    
    AREA_5: (60, 90, 50),
    
    AREA_6: (140, 50, 140),
    
    CAVES_4: (170, 40, 60),
    
    FINAL_AREA: (90, 70, 30),
}

special_objects = {
    0xFEF: [("queen", None, None, 0x80, 0x80)],
    0xF57: [("ship", None, None, 0x80, 0x80)],
    0xFD5: [],
    0xF67: [],
    0xFE5: [],
}

# for pushing different regions apart
special_transitions = {
    
    # landing site
    # (0xF77, BIT_EAST): (11, -6, None),
    
    # area 1
    (0xF50, BIT_EAST): (4, 4, CAVES_1),
    
    # area 2
    (0xC1C, BIT_EAST): (2, 0, AREA_2_LOWER),
    (0xC20, BIT_EAST): (1, -2, AREA_2_UPPER),
    
    # area 3
    (0xc55, BIT_WEST): (-2, 0, AREA_3),
    #(0xD39, BIT_NORTH): (9, 4, None),
    
    # caves east
    (0xA58, BIT_EAST): (7, 14, CAVES_2),
    (0xA06, BIT_WEST): (-6, 0, None),
    
    # area 4
    (0xC50, BIT_EAST): (2, 0, AREA_4_UPPER),
    (0xC52, BIT_EAST): (2, 3, AREA_4_LOWER),
    (0xB6A, BIT_NORTH): (-2, -3, None),
    (0x9DA, BIT_EAST): (3, 0, None),
    
    # caves south
    (0xA2E, BIT_WEST): (-5, 12, CAVES_3),
    (0xA0E, BIT_WEST): (-5, 12, CAVES_3),
    
    # area 5
    (0xCA0, BIT_WEST): (-2, 0, AREA_5),
    (0x907, BIT_EAST): (0, -1, None),
    
    # area 6
    (0xCBA, BIT_WEST): (-5, 2, AREA_6),
    
    # area 7
    (0xF1C, BIT_SOUTH): (0, -10, CAVES_4),
    
    # caves west
    (0xA99, BIT_NORTH): (1, -2, FINAL_AREA),
    
    # Final area
    (0xD13, BIT_WEST): (FDX, FDY, SPAWN_AREA),
    (0xE43, BIT_EAST): (-FDX, -FDY, FINAL_AREA),
    (0xFEF, BIT_WEST): (FDX, FDY, SPAWN_AREA),
    (0xF8A, BIT_EAST): (-FDX, -FDY, FINAL_AREA),
}

special_door_masks = {
    # TODO: double-check these
    (0xFEF, BIT_WEST): 0b0000000000001111111111000000000000,
    (0xFEF, BIT_SOUTH): 0b0000000000000000110000000000000000,
    (0xE1D, BIT_NORTH): 0b0000000000000000110000000000000000,
}

# no warp, but we count it anyway
exceptional_null_transitions = {
    0xE38,
    0xE1B,
    0xD22,
    0xB8C,
    0xB8B,
    0xDA3, 0xDB3,
    0xDB4, 0xDC4,
    0xBAB,
    0xD16,
    0xD9A,
    0xDAB,
    0xD8C,
    0xD5C,
    0xD5D,
    0xB7D,
    0xD7C,
    0xD54,
    0xD44,
    0xDA5,
    0xD06,
    0xD7A,
    0xB8D,
    0xB9B,
    0xB4C,
    0xA44,
    0xE7A,
    0xE8A,
    0xD36,
    0xD54,
    0xDB5,
    0xB4E,
    0xE2B,
    0xD26,
    0xD79,
    0xD8A,
    0xD9B,
    0xD9C,
    0xD23,
    0xD33,
    0xD6C,
    0xD6D,
    0xCC4,
    0xCD4,
    0xE48,
    0xAC9,
    0xAD9,
    0xAAB,
    0xABB,
    0xACB,
    0xB9B,
}

suppress_transition = {
    0xA99: {BIT_EAST},
    0xA9B: {BIT_NORTH, BIT_SOUTH},
    0xA89: {BIT_NORTH, BIT_SOUTH},
    0xAB9: {BIT_NORTH, BIT_SOUTH},
    0xADB: {BIT_NORTH, BIT_SOUTH},
    0xAAB: {BIT_NORTH},
    0xACA: {BIT_NORTH, BIT_WEST, BIT_EAST},
    
    0xB1A: {BIT_SOUTH, BIT_NORTH},
    0xB2A: {BIT_EAST, BIT_NORTH},
    0xBB2: {BIT_SOUTH, BIT_WEST},
    0xBC2: {BIT_NORTH, BIT_SOUTH},
    0xBD2: {BIT_NORTH, BIT_SOUTH},
    0xB9B: {BIT_SOUTH},
    0xBCB: BIT_SOUTH,
    0xB7C: BIT_SOUTH,
    0xB8C: BIT_SOUTH,
    0xB5C: BIT_SOUTH,
    0xB61: {BIT_SOUTH, BIT_NORTH},
    0xB71: {BIT_SOUTH, BIT_NORTH},
    0xB81: {BIT_SOUTH, BIT_NORTH},
    0xBFF: BIT_SOUTH,
    0xBDF: BIT_SOUTH,
    0xB9F: BIT_SOUTH,
    
    0xC4F: {BIT_WEST, BIT_EAST},
    0xC74: BIT_EAST,
    0xC75: BIT_WEST,
    0xC7C: BIT_WEST,
    0xC8C: {BIT_WEST, BIT_NORTH},
    0xC8E: BIT_NORTH,
    0xC8F: {BIT_EAST, BIT_SOUTH},
    
    0xD36: {BIT_EAST, NO_REPLICATE},
    0xD45: {BIT_NORTH, BIT_SOUTH},
    0xD7A: {BIT_SOUTH},
    0xD54: {BIT_NORTH, BIT_SOUTH},
    0xD64: {BIT_NORTH, BIT_SOUTH},
    0xD97: {BIT_WEST, BIT_SOUTH, NO_REPLICATE},
    0xD77: {BIT_EAST, NO_REPLICATE},
    
    0xE1A: {BIT_SOUTH, BIT_NORTH},
    0xE2A: {BIT_SOUTH, BIT_NORTH},
    0xE31: {BIT_NORTH, BIT_EAST},
    
    # egg room
    0xE12: {BIT_WEST, NO_REPLICATE},
    0xE22: {BIT_EAST, NO_REPLICATE},
    0xF8A: {BIT_SOUTH, NO_REPLICATE},
    0xF7A: {BIT_SOUTH, NO_REPLICATE},
    
    # queen absent
    0xFFF: {BIT_EAST, BIT_NORTH, BIT_WEST, NO_REPLICATE},
    
    # queen fight
    0xFEF: {BIT_EAST, BIT_NORTH, NO_REPLICATE},
    
    # queen endgame
    0xF9A: {BIT_EAST, BIT_NORTH, BIT_SOUTH, NO_REPLICATE},
}

COMBINE_ROOMS = [
    {0xF55, 0xFD3}, # surface
    {0xD97, 0xD77}, # hydro station
    {0xA28, 0xA08}, # double cave
    
    # lower caves
    {0xB26, 0xBE9},
    {0xCB8, 0xC79},
    {0xB86, 0xBF8},
    {0xCD0, 0xCE0},
    {0xA4B, 0xA86},
    
    # nest's acid caves
    {0xC08, 0xCF8},
    
    # queen
    {0xFFF, 0xFEF, 0xF9A},
    
    # egg
    {0xE12, 0xF7A},
]

EMPTY = -1
NORMAL = 1
HPIPE = 2
VPIPE = 3
DARK = 4

SPECIAL_DISPLAY = {
    
    # upper caves
    0xA01: EMPTY, # questionable
    0xA02: EMPTY,
    0xA81: EMPTY,
    0xA91: EMPTY,
    0xAB2: EMPTY,
    0xAB3: EMPTY,
    0xA57: EMPTY, # questionable
    
    # area 2
    0xC30: VPIPE,
    0xDE4: HPIPE,
    0xD93: HPIPE,
    0x95F: EMPTY,
    0x96F: EMPTY,
    0x9DF: EMPTY,
    0x9EF: EMPTY,
    
    # area 3
    0xD8D: HPIPE,
    0xD78: VPIPE,
    0xD79: VPIPE,
    0xD37: VPIPE,
    0xD38: VPIPE,
    0xD6A: HPIPE,
    0x9E6: EMPTY,
    0x9F6: EMPTY,
    
    # eastern caves
    0xA15: EMPTY,
    0xA16: EMPTY,
    
    # area 4
    0xE5B: HPIPE,
    0xE4B: HPIPE,
    
    # area 5
    0xEA1: DARK,
    0xEB1: DARK,
    
    # lower caves
    0xA76: EMPTY,
    0xA78: EMPTY,
    0xA4C: EMPTY, 0xA87: EMPTY,
    
    # nest
    0xACA: VPIPE,
    0xADA: VPIPE,
}

def compressed_location(bank, x, y):
    return (bank << 8) | (x << 4) | y

def uncompressed_location(v):
    return (v >> 8), (v >> 4) & 0xF, v & 0xF

# bank,x,y versions of the above
for t in list(exceptional_null_transitions):
    exceptional_null_transitions.add((t >> 8, (t >> 4) & 0xF, t & 0xF))
for (t, bit), v in copy.copy(special_transitions).items():
    special_transitions[((t >> 8, (t >> 4) & 0xF, t & 0xF), bit)] = v
for t, bit in copy.copy(suppress_transition).items():
    if type(bit) == int:
        bit = {bit}
    suppress_transition[(t >> 8, (t >> 4) & 0xF, t & 0xF)] = set(bit)

SOLTABLE = romaddr(8, 0x7EFA)
COLTABLE = romaddr(8, 0x7EEA)
MTTABLE = romaddr(8, 0x7F1A)
TRANSITION_TABLE = romaddr(5, 0x42E5)
OBJECT_TABLE = romaddr(3, 0x42E0)

INITSAVE = romaddr(0x1, 0x4e64)

CELL_MT_SIZE = 16
CELL_TILE_SIZE = 32

# offset from save start
IS_X = 3
IS_Y = 1

# offset
IS_BANK = 17
IS_SPR = 8
IS_BG = 10
IS_MT = 13
IS_COL = 15
IS_SOL = 18

SCROLL_DATA = 1 * 16*16*2
TRANSITION_INDICES = 16*16*3

data = None

side_bit_name = {
    BIT_EAST: "East",
    BIT_WEST: "West",
    BIT_NORTH: "North",
    BIT_SOUTH: "South",
}

bit_direction = {
    BIT_EAST: (1, 0),
    BIT_WEST: (-1, 0),
    BIT_NORTH: (0, -1),
    BIT_SOUTH: (0, 1),
}

def peek_u8(bank, ramaddr=None):
    if ramaddr is None:
        return data[bank]
    return data[romaddr(bank, ramaddr)]

def peek_u16(bank, ramaddr=None):
    if ramaddr is None:
        return peek_u8(bank) | (peek_u8(bank + 1) << 8)
    return peek_u8(bank, ramaddr) | (peek_u8(bank, ramaddr + 1) << 8)

# rom address (3 bytes)
def peek_bu16(bank, ramaddr=None):
    if ramaddr is None:
        return romaddr(peek_u8(bank), peek_u16(bank+1))
    return romaddr(peek_u8(bank, ramaddr), peek_u16(bank, ramaddr+1))

def get_scroll_blockers(bank, x, y):
    return peek_u8(bank, SCROLL_DATA + y*16 + x)

STYLE_IDX_BGROM = 0
STYLE_IDX_SPRROM = 1
STYLE_IDX_COLT = 2
STYLE_IDX_SOLT = 3
STYLE_IDX_MTT = 4
STYLE_IDX_NAME = 5

# Style: (bgrom, sprrom, coltable, soltable, mttable, name)

# -> spawn, style
def load_init_save():
    bank = peek_u8(INITSAVE + IS_BANK) # bank
    x = peek_u8(INITSAVE + IS_X)%16 # x
    y = peek_u8(INITSAVE + IS_Y)%16 # y
    spraddr = romaddr(6, peek_u16(INITSAVE + IS_SPR))
    bgrom = peek_bu16(INITSAVE + IS_BG)
    coladdr = peek_u16(INITSAVE + IS_COL)
    mtaddr = peek_u16(INITSAVE + IS_MT)
    solSamus = peek_u8(INITSAVE + IS_SOL)
    col = 4
    sol = 4
    mt = 5
    for i in range(0, 8):
        if peek_u8(SOLTABLE + 4*i) == solSamus:
            sol = i
        if peek_u16(COLTABLE + 2*i) == coladdr:
            col = i
    
    for i in range(0, 10):
        if peek_u16(MTTABLE + 2*i) == mtaddr:
            mt = i
    
    style = (bgrom, spraddr, col, sol, mt, SPAWN_AREA)
    spawn = (bank, x, y)
    return (spawn, style)

def null_transition(transition):
    return transition == 0

def argmax(l):
    i, v = max(enumerate(l), key=lambda x: x[1])
    return i

transitions = dict()

class Transition:
    def __init__(self, idx):
        self.idx = idx
        
        self.ops = self.parse(idx)
    
    def parse(self, idx):
        src = romaddr(TRANSITION_TABLE // 0x4000, peek_u16(TRANSITION_TABLE + idx*2))
        orgsrc = src
        def read_u8():
            nonlocal src
            src += 1
            return peek_u8(src-1)
        def read_u16():
            nonlocal src
            src += 2
            return peek_u16(src-2)
        def read_bu16():
            nonlocal src
            src += 3
            return peek_bu16(src-3)
        
        ops = []
        
        while True:
            opcode = read_u8()
            if opcode == 0xFF:
                break
            op = Table()
            if opcode in [0, 2]:
                op.type = "copy"
                op.src = read_bu16()
                op.dst = read_u16()
                op.size = read_u16()
            elif opcode & 0xF0 == 0x10:
                op.type = "mt"
                op.value = opcode & 0x0F
            elif opcode & 0xF0 == 0x20:
                op.type = "col"
                op.value = opcode & 0x0F
            elif opcode & 0xF0 == 0x30:
                op.type = "sol"
                op.value = opcode & 0x0F
            elif opcode & 0xF0 == 0x40:
                op.type = "warp"
                op.bank = opcode & 0x0F
                yx = read_u8()
                op.x = yx & 0x0F
                op.y = yx >> 4
            elif opcode == 0x50:
                op.type = "queen-retreat"
            elif opcode == 0x60:
                op.type = "damage"
                op.acid = read_u8()
                op.spike = read_u8()
            elif opcode == 0x70:
                op.type = "queen-exit"
            elif opcode & 0xF0 == 0x80:
                op.type = "queen-enter"
                op.bank = opcode & 0x0F
                op.camera_y = read_u16()
                op.camera_x = read_u16()
                op.samus_y = read_u16()
                op.samus_x = read_u16()
                op.x = op.samus_x >> 8
                op.y = op.samus_y >> 8
            elif opcode == 0x90:
                op.type = "if-metroid"
                op.threshold = read_u8()
                op.transition = read_u16()
            elif opcode == 0xA0:
                op.type = "fade"
            elif opcode == 0xB1:
                op.type = "bg"
                op.src = read_bu16()
            elif opcode == 0xB2:
                op.type = "spr"
                op.src = read_bu16()
            elif opcode & 0xF0 == 0xC0:
                op.type = "song"
                op.song = opcode & 0x0F
            elif opcode & 0xF0 == 0xD0:
                op.type = "item"
                op.value = opcode & 0x0F
            else:
                print(f"Unknown opcode: ${opcode:02x}, transition={idx:3x}, offset={src-orgsrc-1}")
                assert(False)
            ops.append(op)
            
        return ops

def get_transition(idx):
    if idx in transitions:
        return transitions[idx]
    t = Transition(idx)
    transitions[idx] = t
    return t

def get_transition_locations_styles(idx, exit_bit, style, warp):
    transition: Transition = get_transition(idx)
    style = list(tuple(style))
    out = []
    dx = 0
    dy = 0
    
    is_queen_retreat = False
    is_queen_exit = False
    
    if exit_bit:
        if warp in suppress_transition and exit_bit in suppress_transition[warp]:
            return []
        stidx = (compressed_location(warp[0], warp[1], warp[2]), exit_bit)
        dx, dy = bit_direction[exit_bit]
        if stidx in special_transitions:
            stdx, stdy, name = special_transitions[stidx]
            if name:
                style[STYLE_IDX_NAME] = name
    warp = (warp[0], (warp[1] + dx + 16) % 16, (warp[2] + dy + 16) % 16)
    for op in transition.ops:
        if op.type == "if-metroid":
            out += get_transition_locations_styles(op.transition, exit_bit, style, (warp[0], (warp[1] - dx + 16) % 16, (warp[2] - dy + 16) % 16))
        elif op.type == "warp":
            warp = (op.bank, (op.x + dx + 16) % 16, (op.y + dy + 16) % 16)
        elif op.type == "queen-enter":
            warp = (op.bank, op.x, op.y)
        elif op.type == "queen-retreat":
            is_queen_retreat = True
        elif op.type == "queen-exit":
            is_queen_exit = True
        elif op.type == "bg":
            style[STYLE_IDX_BGROM] = op.src
        elif op.type == "spr":
            style[STYLE_IDX_SPRROM] = op.src
        elif op.type == "col":
            style[STYLE_IDX_COLT] = op.value
        elif op.type == "sol":
            style[STYLE_IDX_SOLT] = op.value
        elif op.type == "mt":
            style[STYLE_IDX_MTT] = op.value
    
    if warp:
        if is_queen_retreat and exit_bit != BIT_SOUTH:
            pass
        elif is_queen_exit and exit_bit != BIT_WEST:
            pass
        else:
            out.append((warp, style))
    else:
        print(f"Note: missing warp for transition {idx:3x}")
        
    if len(out) >= 2:
        first_warp = out[0][0]
        for warp, _ in out[1:]:
            if warp != first_warp:
                # yes, this can happen.
                # print(f"Inconsistent warps found in transition locations. transition={idx:3x}, warps: {first_warp} vs. {warp}")
                pass
        
    return out

def pretty_rom_addr(rom):
    bank = rom // 0x4000
    if bank == 0:
        return f"0:{rom % 0x4000:04x}"
    else:
        return f"{bank:x}:{0x4000 + (rom % 0x4000):04x}"
def pretty_style(style):
    bgrom, sprrom, col, sol, mt, name = style
    return f"name={name} bg={pretty_rom_addr(bgrom)}, spr={pretty_rom_addr(sprrom)}, col={col}, sol={sol}, mt={mt}"

class Cell:
    def __init__(self, bank, x, y, style):
        self.bank = bank
        self.x = x
        self.y = y
        self.room: Room = None
        self.style = style
        self.exit_bits = None
        # map: dir bit -> list[(door x/y, door length/height)]
        self.door_shapes = {dir: 0 for dir in DIRS}
        idx = y*16 + x
        
        # points to 16x16 meta-tile data (in same bank)
        self.tiles_addr = peek_u16(self.bank, idx*2)
        self.scroll_blockers = peek_u8(self.bank, 0x200 + idx)
        self.transition = peek_u16(self.bank, 0x300 + idx*2) & 0x1FF
        self.objects_rom = romaddr(3, peek_u16(OBJECT_TABLE + 2*(idx + 0x100*(self.bank-9))))
        
        # TODO: what's in the upper 7 bits?
        
        self.contents = []
        self.has_save = False
        self.load_cell_collision_data()
        
        cloc = compressed_location(bank, x, y)
        
        if cloc in special_objects:
            self.contents = copy.copy(special_objects[cloc])
        else:
            self.load_objects()
        
        if not null_transition(self.transition) or (bank, x, y) in exceptional_null_transitions:
            self.identify_plausible_exits()
            
    def load_objects(self):
        addr = self.objects_rom
        while True:
            objn = peek_u8(addr)
            if objn == 0xFF:
                break
            objt = peek_u8(addr + 1)
            objx = peek_u8(addr + 2)
            objy = peek_u8(addr + 3)
            addr += 4
            
            if objt in object_names:
                self.contents.append((
                    object_names[objt],
                    objn, objx, objy
                ))
            elif objn in range(0x40, 0x80):
                print(f"unrecognized object: {objt:x}, {self.bank:x}:{self.x},{self.y}")
                
    def print(self):
        print(f"Cell ({self.bank:x}:{self.x},{self.y}), {pretty_style(self.style)}:")
        #if self.exit_bit:
            #print(f"Exit: {side_bit_name[self.exit_bit]} (Transition={self.transition:3x})")
        if self.region_map:
            for row in self.region_map:
                print(''.join(f"{r:3}" for r in row))
        for row in self.collision:
            print(''.join('X' if tile == 1 else ' ' for tile in row))
        print()
    
    def assign_regions(self):
        size = CELL_TILE_SIZE
        labels = [[0] * size for _ in range(size)]
        regions = []
        regions_size = [0]

        region_id = 1
        directions = [(1,0), (-1,0), (0,1), (0,-1)]

        for y in range(size):
            for x in range(size):
                if self.collision[y][x] == 0 and labels[y][x] == 0:
                    # new region
                    regions.append(region_id)
                    rsize = 0
                    q = deque([(y, x)])
                    labels[y][x] = region_id

                    while q:
                        cy, cx = q.popleft()
                        for dy, dx in directions:
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < size and 0 <= nx < size:
                                if self.collision[ny][nx] == 0 and labels[ny][nx] == 0:
                                    labels[ny][nx] = region_id
                                    q.append((ny, nx))
                                    rsize += 1

                    regions_size.append(rsize)
                    region_id += 1
                    
        self.region_map = labels
        self.regions_size = regions_size
    
    def identify_plausible_exits(self):
        self.assign_regions()
        
        # find which side is the most door-like (most empty space in largest region)
        sides = ((0, 0, 1, 0, BIT_NORTH), (0, CELL_TILE_SIZE-1, 1, 0, BIT_SOUTH), (0, 0, 0, 1, BIT_WEST), (CELL_TILE_SIZE-1, 0, 0, 1, BIT_EAST))
        side_door_tiles = [0, 0, 0, 0]
        exits = set()
        
        for i, (x0, y0, dx, dy, side_bit) in enumerate(sides):
            if self.scroll_blockers & side_bit:
                for j in range(CELL_TILE_SIZE):
                    x = x0 + dx * j
                    y = y0 + dy * j
                    
                    region = self.region_map[y][x]
                    if region != 0:
                        side_door_tiles[i] += 1
                        self.door_shapes[side_bit] |= (1 << j)
                        if side_door_tiles[i] >= 2:
                            exits.add(side_bit)    
                            
            key = (compressed_location(self.bank, self.x, self.y), side_bit)
            if key in special_door_masks:
                self.door_shapes[side_bit] = special_door_masks[key]
                
        
        self.exit_bits = list(exits)
    
    # returns 32x32 array, where 1 represents solid (for samus)
    def load_cell_collision_data(self):
        bgrom, sprrom, colrom, solthresh, mtrom = read_style(self.style)
        
        samus_threshold, projectile_threshold, enemy_threshold = solthresh
        
        self.collision = [[0 for _ in range(CELL_TILE_SIZE)] for _ in range(CELL_TILE_SIZE)]
        self.colflags = [[0 for _ in range(CELL_TILE_SIZE)] for _ in range(CELL_TILE_SIZE)]
        
        for y in range(0, CELL_MT_SIZE):
            for x in range(0, CELL_MT_SIZE):
                # metatile
                mt = peek_u8(self.bank, self.tiles_addr + y*16 + x)
                for yi in range(0, 2):
                    for xi in range(0, 2):
                        # 8x8 tile
                        # TODO: maybe transpose?
                        t = peek_u8(mtrom + mt*4 + yi*2 + xi)
                        colt = peek_u8(colrom + t)
                        
                        if (colt & 0x80):
                            self.has_save = True
                        
                        # t < 4: shot block
                        
                        # mask of special collision types which are non-solid
                        #    01h : 0 Water (also causes morph ball sound effect glitch)
                        #    02h : 1 Half-solid floor (can jump through)
                        #    04h : 2 Half-solid ceiling (can fall through)
                        #    08h : 3 Spike
                        #    10h : 4 Acid
                        #    20h : 5 Shot block
                        #    40h : 6 Bomb block
                        #    80h : 7 Save pillar
                        if (t >= samus_threshold) or (t < 4) or (colt & 0x67):
                            self.collision[y*2 + yi][x*2 + xi] = 0
                        else:
                            self.collision[y*2 + yi][x*2 + xi] = 1
                            
                        if (t < 4):
                            self.colflags[y*2 + yi][x*2 + xi] |= 0x100
                            
                        self.colflags[y*2 + yi][x*2 + xi] |= colt
        
class Room:
    def __init__(self, idx, bank, style):
        self.idx = idx
        self.name = None
        self.bank = bank
        self.style = style
        self.offset = None
        self.duplicates = None
        self.entrances = dict() # (cx, cy, direction) -> {(transition, bank, cx, cy)}
        self.exits = dict() # (cx, cy, direction) -> {(transition, bank, cx, cy)}
        self.cells: set[Cell] = set()
    
    def add_entrance(self, cx, cy, direction, transition, src_bank, src_cx, src_cy):
        key = (cx, cy, direction)
        if key not in self.entrances:
            self.entrances[key] = set()
        self.entrances[key].add((transition, src_bank, src_cx, src_cy))
        
    def add_exit(self, src_cx, src_cy, direction, transition, bank, cx, cy):
        key = (src_cx, src_cy, direction)
        if key not in self.exits:
            self.exits[key] = set()
        self.exits[key].add((transition, bank, cx, cy))
    
    def add_cell(self, x, y):
        cloc = compressed_location(self.bank, x, y)
        self.cells.add((x, y))
        cell = Cell(self.bank, x, y, self.style)
        cell.room = self
        if cloc in room_names:
            self.name = room_names[cloc]
        loc = (self.bank, x, y)
        assert loc not in cells
        cells[loc] = cell
        return cell
    
    def get_transitions(self):
        t = []
        for (x, y) in self.cells:
            cell = cells[(self.bank, x, y)]
            if cell.exit_bits:
                for exit_bit in cell.exit_bits:
                    for transition in get_transition_locations_styles(cell.transition, exit_bit, self.style, (cell.bank, cell.x, cell.y)):
                        t.append(((self.bank, x, y), transition))
        
        return t

# ridx -> Room
rooms: Dict[int, Room] = dict()

# (bank, x, y) -> Cell
cells: Dict[Tuple[int, int, int], Cell] = dict()

def coords_sub(c1, c2):
    return (c1[0] - c2[0], c1[1] - c2[1])

def coords_add(c1, c2):
    return (c1[0] + c2[0], c1[1] + c2[1])

def read_style(style):
    bgaddr, spraddr, col, sol, mt, name = style
    solthresh = (peek_u8(SOLTABLE + sol*4 + 0), peek_u8(SOLTABLE + sol*4 + 1), peek_u8(SOLTABLE + sol*4 + 2))
    return bgaddr, spraddr, romaddr(8, peek_u16(COLTABLE + col*2)), solthresh, romaddr(8, peek_u16(MTTABLE + mt*2))

def infer_suppressions():
    for pass_ in range(0, 2):
        for bank in range(0x9,0xF):
            for y in range(0,16):
                for x in range(0,16):
                    idx = 16*y + x
                    tiles_addr = romaddr(bank, peek_u16(bank, 2*idx))
                    if (bank, x, y) in suppress_transition:
                        if NO_REPLICATE not in suppress_transition[(bank, x, y)]:
                            suppress_transition[tiles_addr] = suppress_transition[(bank, x, y)]
                    if tiles_addr in suppress_transition:
                        suppress_transition[(bank, x, y)] = suppress_transition[tiles_addr]

def identify_rooms():
    # identify all rooms. Don't worry about their euclidean/absolute locations
    spawn, style = load_init_save()
    
    spawn_bank, spawn_x, spawn_y = spawn
    rooms[SPAWN_ROOM_IDX] = Room(SPAWN_ROOM_IDX, spawn_bank, style)
    rooms[SPAWN_ROOM_IDX].offset = (-spawn_x, -spawn_y)
    
    map_room_idx = {
        spawn: SPAWN_ROOM_IDX
    }
    
    next_room_idx = SPAWN_ROOM_IDX + 1
    
    frontier = PriorityQueue()
    frontier.put((SPAWN_ROOM_IDX, spawn, style))
    
    explored = set()
    
    def getNeighbours(location):
        bank, x, y = location
        n = []
        s1 = get_scroll_blockers(bank, x, y)
        for offset in [(-1, 0, BIT_WEST, BIT_EAST), (1, 0, BIT_EAST, BIT_WEST), (0, -1, BIT_NORTH, BIT_SOUTH), (0, 1, BIT_SOUTH, BIT_NORTH)]:
            dx, dy, sbit, revbit = offset
            x2 = (x + dx + 16) % 16
            y2 = (y + dy + 16) % 16
            if sbit & s1:
                continue
            if (x2 < 0 or x2 >= 16):
                continue
            if (y2 < 0 or y2 >= 16):
                continue
            if get_scroll_blockers(bank, x2, y2) & revbit:
                continue
            n.append((bank, x2, y2))
        return n

    while not frontier.empty():
        ridx, location, style = frontier.get()
        bank, x, y = location
        
        if location in explored:
            continue
        if ridx not in rooms:
            rooms[ridx] = Room(ridx, bank, style)
        room: Room = rooms[ridx]
        cell = room.add_cell(x, y)
        explored.add(location)
        map_room_idx[location] = ridx
        
        for n in getNeighbours(location):
            frontier.put((ridx, n, style))

        if cell.exit_bits:
            for exit_bit in cell.exit_bits:
                for tr_loc_style in get_transition_locations_styles(cell.transition, exit_bit, style, (cell.bank, cell.x, cell.y)):
                    tr_loc, tr_style = tr_loc_style
                    frontier.put((next_room_idx, tr_loc, tr_style))
                    next_room_idx += 1
                
    for ridx, room in rooms.items():
        print(f"Room Index: {ridx}, Size: {len(room.cells)}")
        print(f"  transitions: {room.get_transitions()}")
        
        # print ascii art of room solidity
        if False:
            for cell_loc in room.cells:
                cell: Cell = cells[(room.bank, cell_loc[0], cell_loc[1])]
                cell.print()

def identify_duplicate_rooms():
    for ridx, room in rooms.items():
        for (cx, cy) in room.cells:
            cloc = compressed_location(room.bank, cx, cy)
            for duplicate_set in COMBINE_ROOMS:
                if cloc in duplicate_set:
                    if not room.duplicates:
                        room.duplicates = []
                    for cloc_other in duplicate_set:
                        if cloc_other != cloc:
                            cell_other = cells[uncompressed_location(cloc_other)]
                            room.duplicates.append(cell_other.room)
    
    for i in range(10):
        for ridx, room in rooms.items():
            if room.duplicates is not None:
                for r in room.duplicates:
                    if r.duplicates is None:
                        r.duplicates = []
                    for r2 in room.duplicates:
                        if r is not r2 and r2 not in r.duplicates:
                            r.duplicates.append(r2)
                    if room not in r.duplicates:
                        r.duplicates.append(room)
                

class Area:
    def __init__(self, name):
        self.name = name
        self.minx = None
        self.maxx = None
        self.miny = None
        self.maxy = None
        self.rooms = []
        
    def add_room(self, room):
        self.rooms.append(room)
        for (cx, cy) in room.cells:
            x = cx + room.offset[0]
            y = cy + room.offset[1]
            
            if self.minx is None:
                self.minx = x
                self.miny = y
                self.maxx = x + 1
                self.maxy = y + 1
            else:
                self.minx = min(x, self.minx)
                self.miny = min(y, self.miny)
                self.maxx = max(x+1, self.maxx)
                self.maxy = max(y+1, self.maxy)

def define_areas():
    areas = [Area(name) for name in area_names]
    for ridx, room in rooms.items():
        for area in areas:
            if area.name == room.style[STYLE_IDX_NAME]:
                area.add_room(room)
    return areas

def rooms_layout():
    minx = 0
    miny = 0
    maxx = 0
    maxy = 0
    
    assigned_room = dict()
    frontier = [SPAWN_ROOM_IDX]
    processed = set()
    
    jumps = []
    
    while len(frontier) > 0:
        ridx = frontier.pop()
        if ridx in processed:
            continue
        processed.add(ridx)
        room = rooms[ridx]
        rox, roy = room.offset
        
        room.minx = None
        room.miny = None
        room.maxx = None
        room.maxy = None
        
        for cell_loc in room.cells:
            cx, cy = cell_loc
            mapx = cx + rox
            mapy = cy + roy
            
            if room.minx is None:
                room.minx = mapx
                room.miny = mapy
                room.maxx = mapx+1
                room.maxy = mapy+1
            else:
                room.minx = min(room.minx, mapx)
                room.miny = min(room.miny, mapy)
                room.maxx = max(room.maxx, mapx+1)
                room.maxy = max(room.maxy, mapy+1)
            
            room_info = (ridx, room.bank, cx, cy)
            if (mapx, mapy) not in assigned_room:
                assigned_room[(mapx, mapy)] = [room_info]
            else:
                assigned_room[(mapx, mapy)].append(room_info)
            
            minx = min(minx, mapx)
            miny = min(miny, mapy)
            maxx = max(maxx, mapx+1)
            maxy = max(maxy, mapy+1)
            
            cell = cells[(room.bank, cx, cy)]
            cell.color = AREA_COLORS[cell.style[STYLE_IDX_NAME]]
            
            if cell.exit_bits:
                for exit_bit in cell.exit_bits:
                    dx, dy = bit_direction[exit_bit]
                    for tr_loc_style in get_transition_locations_styles(cell.transition, exit_bit, room.style, (cell.bank, cell.x, cell.y)):
                        tr_loc, tr_style = tr_loc_style
                        nbank, nx, ny = tr_loc
                        if ((room.bank, cx, cy), exit_bit) in special_transitions:
                            stidx = ((room.bank, cx, cy), exit_bit)
                            stdx, stdy, _ = special_transitions[stidx]
                            jumps.append((True, mapx + 0.5 + dx/2, mapy + 0.5 + dy/2, mapx + 0.5 + stdx + dx/2, mapy + stdy + 0.5 + dy/2))
                        else:
                            stdx, stdy = 0, 0
                        ncell = cells[tr_loc]
                        assert ncell, f"missing cell: {nbank:x}:{nx},{ny}"
                        nroom: Room = ncell.room
                        preferred_offset = (mapx + dx + stdx - nx, mapy + dy + stdy - ny)
                        if not nroom.offset:
                            nroom.offset = preferred_offset
                        
                        # jump if rooms not aligned
                        if preferred_offset != nroom.offset or True:
                            offset_jdx, offset_jdy = coords_sub(nroom.offset, preferred_offset)
                            jumps.append((False, mapx + 0.5 + dx*(0.4), mapy + 0.5 + dy*(0.4), mapx + 0.5 + dx*0.75 + offset_jdx, mapy + 0.5 + dy*0.75 + offset_jdy))
                        
                        frontier.append(nroom.idx)
                        
                        room.add_exit(cx, cy, exit_bit, cell.transition, nbank, nx, ny)
                        nroom.add_entrance(nx, ny, REVERSE_DIRECTIONS[exit_bit], cell.transition, room.bank, cx, cy)
    
    layout = Table()
    
    layout.jumps = jumps
    layout.assigned_room = assigned_room
    layout.maxx = maxx
    layout.minx = minx
    layout.maxy = maxy
    layout.miny = miny
    layout.areas = define_areas()
    
    layout.w = maxx - minx
    layout.h = maxy - miny
    
    return layout
        
def rooms_display(layout: Table):
    grid = [[None for _ in range(layout.w)] for _ in range(layout.h)]
    for (x, y), v in layout.assigned_room.items():
        grid[y - layout.miny][x - layout.minx] = v
    display_grid(grid, [(b, x - layout.minx, y - layout.miny, x2 - layout.minx, y2 - layout.miny) for b, x, y, x2, y2 in layout.jumps], cells)

def layout_to_json(layout: Table, path="met2.json"):
    j = {"areas": [], "rooms": [], "world": {"w": layout.w, "h": layout.h}}
    
    # define rooms
    handled = set()
    has_special = set()
    layout_idx = dict()
    layout_idx_reverse = dict()
    for ridx, room in rooms.items():
        if ridx in handled:
            continue
        handled.add(ridx)
        idx = len(layout_idx)
        layout_idx[room.idx] = idx
        layout_idx_reverse[idx] = room.idx
        
        myrooms: list[Room] = [room]
        
        name = room.name
        if room.duplicates:
            for r in room.duplicates:
                handled.add(r.idx)
                myrooms.append(r)
                if r.name is not None:
                    name = r.name
        
        x0 = min(r.minx for r in myrooms)
        y0 = min(r.miny for r in myrooms)
        x1 = max(r.maxx for r in myrooms)
        y1 = max(r.maxy for r in myrooms)
        
        jroom = {
            "x": x0 - layout.minx,
            "y": y0 - layout.miny,
            "w": x1 - x0,
            "h": y1 - y0,
            "cells": [[0 for _ in range(x1-x0)] for _2 in range(y1-y0)],
            
            # one for each duplicate
            "states": [],
            
            "doors": [],
            
            "features": [],
        }
        
        if name:
            jroom["name"] = name
        
        combined_doors = dict()
        
        for i, r in enumerate(myrooms):
            statebit = 1 << i
            embedding = [[0 for _ in range(x1-x0)] for _2 in range(y1-y0)]
            for (cx, cy) in r.cells:
                cell = cells[(r.bank, cx, cy)]
                mapx = cx + r.offset[0] 
                mapy = cy + r.offset[1]
                roomx = mapx - x0
                roomy = mapy - y0
                
                if cell.has_save:
                    jroom["features"].append({"type": "save", "x": roomx, "y": roomy})
                for feature in cell.contents:
                    jroom["features"].append({"type": feature[0], "slot": feature[1], "state": i, "x": roomx, "y": roomy, "sx": feature[2], "sy": feature[3]})
                
                tile = 1
                cloc = compressed_location(r.bank, cx, cy)
                if cloc in SPECIAL_DISPLAY:
                    tile = SPECIAL_DISPLAY[cloc]
                    has_special.add(ridx)
                
                #print("r", hex(r.idx))
                #print(f"room range [{x0}, {x1}] × [{y0}, {y1}]; dimensions {x1-x0}×{y1-y0}")
                #print(f"cell cx={cx:x},cy={cy:x}, mx={mapx},my={mapy} rx={roomx},ry={roomy}")
                
                jroom["cells"][roomy][roomx] = tile
                embedding[roomy][roomx] = 1
            
            bgrom, sprrom, col, sol, mt, area_name = r.style
            jroom["states"].append({
                "bank": r.bank,
                "x": x0 - r.offset[0],
                "y": y0 - r.offset[1],
                "cells": embedding,
                "style": {
                    "bgrom": bgrom,
                    "sprrom": sprrom,
                    "collision": col,
                    "solidity": sol,
                    "metatiles": mt,
                }
            })
            
            def add_door(entrance, cx, cy, direction, instance):
                mapx = cx + r.offset[0]
                mapy = cy + r.offset[1]
                roomx = mapx - x0
                roomy = mapy - y0
                key = (roomx, roomy, direction)
                
                cell = cells[(r.bank, cx, cy)]
                
                transition, nbank, nx, ny = instance
                ncell = cells[(nbank, nx, ny)]
                nroom = ncell.room
                nmapx = nx + nroom.offset[0]
                nmapy = ny + nroom.offset[1]
                
                # todo: record destination
                if key not in combined_doors:
                    combined_doors[key] = {
                        "x": roomx,
                        "y": roomy,
                        "dir": direction,
                        "entrance_states": 0,
                        "exit_states": 0,
                        "entrance_transitions": [None for q in myrooms],
                        "exit_transitions": [None for q in myrooms],
                        "mask": 0,
                        "dst_mask": 0,
                    }
                
                door = combined_doors[key]
                door['mask'] |= cell.door_shapes[direction]
                door['dst_mask'] |= ncell.door_shapes[REVERSE_DIRECTIONS[direction]]
                door["entrance_transitions" if entrance else "exit_transitions"][i] = ((transition, nbank, nx, ny))
                door["entrance_states" if entrance else "exit_states"] |= statebit
                if ncell.room.style[STYLE_IDX_NAME] != room.style[STYLE_IDX_NAME] and not entrance:
                    door["to-area"] = area_names.index(ncell.room.style[STYLE_IDX_NAME])
                elif abs(nmapx - mapx) + abs(nmapy - mapy) > 1 and not entrance:
                    door["jump"] = [nmapx - mapx, nmapy - mapy]
            
            # add entrances
            for (cx, cy, direction), instances in r.entrances.items():
                for instance in instances:
                    add_door(True, cx, cy, direction, instance)
            
            # add exits
            for (cx, cy, direction), instances in r.exits.items():
                for instance in instances:
                    add_door(False, cx, cy, direction, instance)
        
        jroom["doors"] += [info for key, info in combined_doors.items()]
        
        if len(jroom["features"]) == 0:
            del jroom["features"]
        j["rooms"].append(jroom)
        
    # swap index of any room containing a special tile to the end of the room list;
    # this ensures the special tiles will be drawn last 
    for ridx, room in rooms.items():
        if ridx in layout_idx:
            lidx = layout_idx[ridx]
            if ridx in has_special:
                for i in range(len(j["rooms"])-1, 0, -1):
                    ridx_swap = layout_idx_reverse[i]
                    if ridx_swap not in has_special:
                        jroom = j["rooms"][lidx]
                        jroom_swap = j["rooms"][i]
                        j["rooms"][lidx] = jroom_swap
                        j["rooms"][i] = jroom
                        layout_idx[ridx] = i
                        layout_idx[ridx_swap] = lidx
                        layout_idx_reverse[i] = ridx
                        layout_idx_reverse[lidx] = ridx_swap
                        assert layout_idx_reverse[i] in has_special
                        break
    
    # define areas
    for area in layout.areas:
        j["areas"].append({
            "name": area.name,
            "x0": area.minx - layout.minx,
            "x1": area.maxx - layout.minx,
            "y0": area.miny - layout.miny,
            "y1": area.maxy - layout.miny,
            "rooms": sorted([
                layout_idx[room.idx] for room in area.rooms if (room.idx in layout_idx)
            ])
        })
    
    with open(path, 'w') as json_file:
        s = json.dumps(j, indent=2)

        def collapse_numeric_lists(match):
            full = match.group(0)           # like "[ 1,\n  2,\n  3 ]"
            inner = full[1:-1]              # strip [ and ]
            items = re.split(r",\s*", inner.strip())
            return "[" + ", ".join(items) + "]"

        s = re.sub(
            r"\[(?:\s*\d+(?:\.\d+)?\s*,?)+\s*\]",
            collapse_numeric_lists,
            s
        )

        json_file.write(s)
        

def main(rom_path):
    global data
    with open(rom_path, 'rb') as rom_file:
        data = rom_file.read()
    
    infer_suppressions()
    identify_rooms()
    identify_duplicate_rooms()
    layout = rooms_layout()
    layout_to_json(layout)
    rooms_display(layout)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract.py <path to rom.gb>")
        sys.exit(1)

    rom_path = sys.argv[1]
    main(rom_path)