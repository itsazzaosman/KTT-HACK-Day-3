import os
import json
from PIL import Image, ImageDraw

def ensure_directories():
    """Create the images cache directory if it doesn't exist."""
    os.makedirs('images', exist_ok=True)

def draw_grid(draw, total_count, group1_count, color1, color2, shape_type='circle'):
    """Draws a clean grid of shapes for easy blob counting."""
    cols = 10
    cell_w = 60
    cell_h = 60
    
    # Calculate starting offsets to roughly center the grid
    rows = (total_count // cols) + 1
    start_x = (800 - (min(total_count, cols) * cell_w)) // 2
    start_y = (600 - (rows * cell_h)) // 2

    for i in range(total_count):
        row = i // cols
        col = i % cols
        
        x0 = start_x + (col * cell_w) + 10
        y0 = start_y + (row * cell_h) + 10
        x1 = x0 + cell_w - 20
        y1 = y0 + cell_h - 20

        # Use color1 for the first group, color2 for the added/subtracted group
        color = color1 if i < group1_count else color2

        if shape_type == 'circle':
            draw.ellipse([x0, y0, x1, y1], fill=color)
        elif shape_type == 'square':
            draw.rectangle([x0, y0, x1, y1], fill=color)

def process_visuals():
    json_path = "data/T3.1_Math_Tutor/curriculum_full.json"
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}. Run the data generator first.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        curriculum = json.load(f)

    print(f"Loaded {len(curriculum)} items. Generating visual grids...")
    
    # Define our visual mappings
    styles = {
        'tomatoes': {'color1': 'red', 'color2': 'darkred', 'shape': 'circle'},
        'mangoes': {'color1': 'orange', 'color2': 'darkorange', 'shape': 'circle'},
        'goats': {'color1': 'saddlebrown', 'color2': 'peru', 'shape': 'square'},
        'cows': {'color1': 'black', 'color2': 'gray', 'shape': 'square'},
        'generic': {'color1': 'dodgerblue', 'color2': 'limegreen', 'shape': 'circle'},
        'subtraction': {'color1': 'dodgerblue', 'color2': 'lightgray', 'shape': 'circle'}
    }

    generated_count = 0

    for item in curriculum:
        visual_tag = item.get('visual')
        if not visual_tag:
            continue
            
        filepath = f"images/{visual_tag}.png"
        
        # Skip if already generated
        if os.path.exists(filepath):
            continue

        # Create a blank white canvas
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        parts = visual_tag.split('_')
        
        # Parsing logic based on our generator tags
        try:
            if parts[0] in styles:
                # e.g., tomatoes_10
                obj_type = parts[0]
                count = int(parts[1])
                style = styles[obj_type]
                draw_grid(draw, count, count, style['color1'], style['color2'], style['shape'])
                
            elif parts[0] == 'compare':
                # e.g., compare_8_4 (Draw both to show relative size)
                c1, c2 = int(parts[1]), int(parts[2])
                style = styles['generic']
                draw_grid(draw, c1 + c2, c1, style['color1'], style['color2'], style['shape'])
                
            elif parts[0] == 'add':
                # e.g., add_12_14
                c1, c2 = int(parts[1]), int(parts[2])
                style = styles['generic']
                draw_grid(draw, c1 + c2, c1, style['color1'], style['color2'], style['shape'])
                
            elif parts[0] == 'sub':
                # e.g., sub_16_9 (Draw total, but grey out the subtracted amount)
                total, sub = int(parts[1]), int(parts[2])
                style = styles['subtraction']
                draw_grid(draw, total, total - sub, style['color1'], style['color2'], style['shape'])
                
            elif parts[0] == 'wp' and parts[1] == 'add':
                # e.g., wp_add_26_7_goats
                c1, c2, obj_type = int(parts[2]), int(parts[3]), parts[4]
                style = styles.get(obj_type, styles['generic'])
                draw_grid(draw, c1 + c2, c1, style['color1'], style['color2'], style['shape'])

            img.save(filepath)
            generated_count += 1
            
        except Exception as e:
            print(f"Skipping {visual_tag} due to parsing error: {e}")

    print(f"✅ Generated {generated_count} new images in the /images folder.")

if __name__ == "__main__":
    ensure_directories()
    process_visuals()