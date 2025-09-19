from PIL import Image, ImageDraw, ImageFont
import math


def draw_arrow(draw, xy, fill=None, width=2):
    (x0, y0), (x1, y1) = xy
    draw.line([(x0, y0), (x1, y1)], fill=fill, width=width)

    # Arrowhead size
    arrow_length = 10 + width * 2
    arrow_angle = math.radians(25)

    # Vector of line
    dx = x1 - x0
    dy = y1 - y0
    angle = math.atan2(dy, dx)

    # Left and right arrowhead lines
    left_x = x1 - arrow_length * math.cos(angle - arrow_angle)
    left_y = y1 - arrow_length * math.sin(angle - arrow_angle)
    right_x = x1 - arrow_length * math.cos(angle + arrow_angle)
    right_y = y1 - arrow_length * math.sin(angle + arrow_angle)

    draw.line([(x1, y1), (left_x, left_y)], fill=fill, width=width)
    draw.line([(x1, y1), (right_x, right_y)], fill=fill, width=width)

def display_grid(grid, jumps, cells=None, output_path="grid_output.png"):
    rows = len(grid)
    cols = len(grid[0])
    
    tile_size = 2
    cell_size = tile_size * 32
    img_width = cols * cell_size
    img_height = rows * cell_size
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    print("drawing")
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    for row in range(rows):
        for col in range(cols):
            cell_value = grid[row][col]
            
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            if cell_value is None:
                draw.rectangle([x1, y1, x2, y2], fill='white', outline='black')
            else:
                
                if len(cell_value) == 1 and cells:
                    ridx, bank, x, y = cell_value[0]
                    cell = cells[(bank, x, y)]
                    collision = cell.collision
                    for j in range(32):
                        for i in range(32):
                            if collision[j][i] == 1:
                                draw.rectangle([x1 + i*tile_size, y1 + j*tile_size, x1 + i*tile_size + tile_size, y1 + j*tile_size + tile_size], fill='blue')
                else:
                    draw.rectangle([x1, y1, x2, y2], fill='lightblue' if len(cell_value) <= 1 else 'gray', outline='black')
                
                hex_strings = []
                for entry in cell_value:
                    if entry:
                        ridx, bank, x, y = entry
                        hex_strings.append(f"{ridx:x}:{bank:x}{x:x}{y:x}")
                
                if hex_strings:
                    text = "\n".join(hex_strings)
                    # Center text in cell
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    text_x = x1 + (cell_size - text_width) // 2
                    text_y = y1 + (cell_size - text_height) // 2
                    
                    draw.text((text_x, text_y), text, fill='black', font=font)
    
    for p in [False, True]:
        for jump in jumps:
            if len(jump) == 5 and jump[0] == p:
                color_bool, x0, y0, x1, y1 = jump
                color = 'green' if color_bool else 'red'
                
                # Convert grid coordinates to pixel coordinates (top-left of cells)
                start_x = x0 * cell_size
                start_y = y0 * cell_size
                end_x = x1 * cell_size
                end_y = y1 * cell_size
                
                # Draw the jump line
                if (abs(end_x - start_x) + abs(end_y - start_y)) < cell_size:
                    draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=2)
                else:
                    draw_arrow(draw, [(start_x, start_y), (end_x, end_y)], fill=color, width=2)
    
    img.save(output_path)
    img.show()
    
    return img