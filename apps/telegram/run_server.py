import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8100))
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        reload=True,
        reload_dirs=[os.path.dirname(os.path.abspath(__file__))],
    )
