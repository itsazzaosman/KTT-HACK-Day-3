import os

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        # Tell Python to completely ignore the 'tts' folder
        if 'tts' in dirnames:
            dirnames.remove('tts') 
            
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

size_mb = get_size() / (1024 * 1024)
print(f"✅ Total app footprint (excluding TTS cache): {size_mb:.2f} MB")