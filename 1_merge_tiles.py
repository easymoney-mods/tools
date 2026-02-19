import os
from PIL import Image, ImageFile

# --- TACTICAL CONFIGURATION ---
# Set this to the LOD folder you want to process (0 for max detail, 1, 2, etc.)
LOD_LEVEL = "1"
BASE_DIR = os.path.join("Web", "Anizay", "LODS", LOD_LEVEL)
OUTPUT_FILE = f"Anizay_Map_LOD{LOD_LEVEL}_FLIPPED.jpg"

# Disables safety limits for massive images
Image.MAX_IMAGE_PIXELS = None
# Helps handle slightly corrupted/truncated image files from the export
ImageFile.LOAD_TRUNCATED_IMAGES = True
# ------------------------------

def merge_final_flip():
    print(f"--- OPERATION: LOD {LOD_LEVEL} MERGE WITH Y-FLIP CORRECTION ---")
    print("Scanning for map tiles...")
    
    if not os.path.exists(BASE_DIR):
        print(f"ERROR: Folder not found: {BASE_DIR}")
        return

    # 1. Universal scan to find all tile images
    tiles = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.lower() == "tile.jpg" or file.isdigit():
                parts = root.replace("\\", "/").split("/")
                try:
                    x = int(parts[-2])
                    y = int(parts[-1])
                    tiles.append((x, y, os.path.join(root, file)))
                except (ValueError, IndexError):
                    continue

    if not tiles:
        print(f"CRITICAL ERROR: No image files found in {BASE_DIR}")
        return

    # 2. Calculate grid boundaries
    min_x = min(t[0] for t in tiles)
    max_x = max(t[0] for t in tiles)
    min_y = min(t[1] for t in tiles)
    max_y = max(t[1] for t in tiles)

    with Image.open(tiles[0][2]) as img:
        tile_w, tile_h = img.size

    # 3. Calculate native total dimensions
    grid_w = max_x - min_x + 1
    grid_h = max_y - min_y + 1
    full_w = grid_w * tile_w
    full_h = grid_h * tile_h
    
    print(f"Grid detected: X[{min_x}-{max_x}], Y[{min_y}-{max_y}]")
    print(f"Native total resolution: {full_w} x {full_h} pixels")

    # Create solid black canvas to prevent transparent gaps
    print("Allocating memory for massive image...")
    canvas = Image.new('RGB', (full_w, full_h), (0, 0, 0))

    print("Beginning assembly with Y-FLIP correction...")
    count = 0
    total = len(tiles)
    for x, y, path in tiles:
        try:
            with Image.open(path) as t_img:
                # --- THE DEFINITIVE FIX ---
                pos_x = (x - min_x) * tile_w
                # We use max_y - y to invert the vertical axis
                pos_y = (max_y - y) * tile_h
                
                canvas.paste(t_img, (pos_x, pos_y))
                count += 1
                if count % 200 == 0: print(f"Processed {count}/{total} tiles...")
        except Exception as e:
             print(f"Warning: Issue with file {path}: {e}")

    # 4. Web compatibility resize (Max 16384px limit for browsers)
    TARGET_SIZE = 16384
    if full_w > TARGET_SIZE or full_h > TARGET_SIZE:
        print(f"\n--- TACTICAL RESIZE TO {TARGET_SIZE}px ---")
        print("This prevents browser crashes. May take time (100% CPU)...")
        canvas = canvas.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

    # 5. Final Save
    print(f"\nSaving final file: {OUTPUT_FILE}...")
    canvas.save(OUTPUT_FILE, "JPEG", quality=92, optimize=True)
    print("--- MISSION ACCOMPLISHED. MAP READY. ---")

if __name__ == "__main__":
    merge_final_flip()
    input("Press ENTER to close...")