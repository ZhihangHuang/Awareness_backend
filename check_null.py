import os

def check_null_bytes(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f'❌ Null byte found in: {path}')
                except Exception as e:
                    print(f'⚠️ Cannot read {path}: {e}')

check_null_bytes('.')
