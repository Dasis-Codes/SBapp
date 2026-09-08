import traceback
from app import create_app

try:
    app = create_app()
except Exception as e:
    print("CRITICAL BOOT ERROR:")
    traceback.print_exc()
    raise e

if __name__ == '__main__':
    app.run()