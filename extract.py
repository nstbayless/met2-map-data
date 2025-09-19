import sys
from queue import PriorityQueue
from collections import deque
from table import Table
from display import *
from typing import Dict, Tuple
import copy

BIT_EAST = 1
BIT_WEST = 2
BIT_NORTH = 4
BIT_SOUTH = 8

NO_REPLICATE = -1

def romaddr(bank, ramaddr):
    return 0x4000 * bank + (ramaddr % 0x4000)

FDX = -6
FDY = 0

# for pushing different regions apart
special_transitions = {
    
    # landing site
    (0xF77, BIT_EAST): (11, -6),
    
    # area 1
    (0xF50, BIT_EAST): (4, 4),
    
    # area 2
    (0xC1C, BIT_EAST): (2, 0),
    (0xC20, BIT_EAST): (1, -2),
    
    # area 3
    (0xc55, BIT_WEST): (-2, 0),
    #(0xD39, BIT_NORTH): (9, 4),
    
    # area 4
    (0x9DA, BIT_EAST): (3, 0),
    #(0x9C6, BIT_SOUTH): (5, 5),
    #(0xE7A, BIT_EAST): (8, -1),
    (0xC50, BIT_EAST): (2, 0),
    (0xC52, BIT_EAST): (2, 3),
    (0xB6A, BIT_NORTH): (-2, -3),
    
    # cave fork
    #0x1A0: (-5, 5),
    (0xA06, BIT_WEST): (-2, 12),
    
    # double acid cave
    (0xA2E, BIT_WEST): (-5, 12),
    (0xA0E, BIT_WEST): (-5, 12),
    
    # area 5
    (0xCA0, BIT_WEST): (-2, 0),
    (0x907, BIT_EAST): (0, -1),
    
    # area 6
    (0xCBA, BIT_WEST): (-5, 2),
    
    # area 7
    (0xF1C, BIT_SOUTH): (1, -12),
    
    # Final area
    (0xD13, BIT_WEST): (FDX, FDY),
    (0xE43, BIT_EAST): (-FDX, -FDY),
    (0xFEF, BIT_WEST): (FDX, FDY),
    (0xF8A, BIT_EAST): (-FDX, -FDY),
}

# no warp, but we count it anyway
exceptional_null_transitions = {
    0xB8C,
    0xB8D,
    0xB9B,
    0xE7A,
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
    0xD6C,
    0xD6D,
    0xCC4,
    0xE48,
    0xAC9,
    0xAD9,
    0xAAB,
    0xABB,
    0xACB,
}

suppress_transition = {
    0xA99: {BIT_EAST},
    0xA9B: {BIT_NORTH, BIT_SOUTH},
    0xA89: {BIT_NORTH, BIT_SOUTH},
    0xAB9: {BIT_NORTH, BIT_SOUTH},
    0xADB: {BIT_NORTH, BIT_SOUTH},
    0xAAB: {BIT_NORTH},
    0xACA: {BIT_NORTH},
    
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
    0xD54: {BIT_NORTH, BIT_SOUTH},
    0xD64: {BIT_NORTH, BIT_SOUTH},
    0xD97: {BIT_WEST, BIT_SOUTH, NO_REPLICATE},
    0xD77: {BIT_EAST, NO_REPLICATE},
    
    0xE1A: {BIT_SOUTH, BIT_NORTH},
    0xE2A: {BIT_SOUTH, BIT_NORTH},
    0xE31: {BIT_NORTH, BIT_EAST},
    
    # larva room
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

SPAWN_ROOM_IDX = 1

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

# Style: (bgrom, sprrom, coltable, soltable, mttable, [to be continued...])

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
    
    style = (bgrom, spraddr, col, sol, mt)
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
        dx, dy = bit_direction[exit_bit]
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
    bgrom, sprrom, col, sol, mt = style
    return f"bg={pretty_rom_addr(bgrom)}, spr={pretty_rom_addr(sprrom)}, col={col}, sol={sol}, mt={mt}"

class Cell:
    def __init__(self, bank, x, y, style):
        self.bank = bank
        self.x = x
        self.y = y
        self.room: Room = None
        self.style = style
        self.exit_bits = None
        idx = y*16 + x
        
        # points to 16x16 meta-tile data (in same bank)
        self.tiles_addr = peek_u16(self.bank, idx*2)
        self.scroll_blockers = peek_u8(self.bank, 0x200 + idx)
        self.transition = peek_u16(self.bank, 0x300 + idx*2) & 0x1FF
        
        # TODO: what's in the upper 7 bits?
        
        self.load_cell_collision_data()
        
        if not null_transition(self.transition) or (bank, x, y) in exceptional_null_transitions:
            self.identify_plausible_exits()
            
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
        for i, side in enumerate(sides):
            x0, y0, dx, dy, side_bit = side
            if self.scroll_blockers & side_bit:
                for j in range(CELL_TILE_SIZE):
                    x = x0 + dx * j
                    y = y0 + dy * j
                    
                    region = self.region_map[y][x]
                    if region != 0:
                        side_door_tiles[i] += 1
                        if side_door_tiles[i] >= 2:
                            exits.add(side_bit)
                            
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
                            
                        self.colflags[y*2 + yi][x*2 + xi] |= colt
        
class Room:
    def __init__(self, idx, bank, style):
        self.idx = idx
        self.bank = bank
        self.style = style
        self.offset = None
        self.cells: set[Cell] = set()
        
    def add_cell(self, x, y):
        self.cells.add((x, y))
        cell = Cell(self.bank, x, y, self.style)
        cell.room = self
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
    bgaddr, spraddr, col, sol, mt = style
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
        
        for cell_loc in room.cells:
            cx, cy = cell_loc
            mapx = cx + rox
            mapy = cy + roy
            
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
            
            if cell.exit_bits:
                for exit_bit in cell.exit_bits:
                    dx, dy = bit_direction[exit_bit]
                    for tr_loc_style in get_transition_locations_styles(cell.transition, exit_bit, room.style, (cell.bank, cell.x, cell.y)):
                        tr_loc, tr_style = tr_loc_style
                        nbank, nx, ny = tr_loc
                        if ((room.bank, cx, cy), exit_bit) in special_transitions:
                            stdx, stdy = special_transitions[((room.bank, cx, cy), exit_bit)]
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
    
    w = maxx - minx
    h = maxy - miny
    grid = [[None for _ in range(w)] for _ in range(h)]
    for (x, y), v in assigned_room.items():
        grid[y - miny][x - minx] = v
        
    display_grid(grid, [(b, x - minx, y - miny, x2 - minx, y2 - miny) for b, x, y, x2, y2 in jumps], cells)

def main(rom_path):
    global data
    with open(rom_path, 'rb') as rom_file:
        data = rom_file.read()
    
    infer_suppressions()
    identify_rooms()
    rooms_layout()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract.py <path to rom.gb>")
        sys.exit(1)

    rom_path = sys.argv[1]
    main(rom_path)