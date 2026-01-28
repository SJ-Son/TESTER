import uvicorn
import os

if __name__ == "__main__":
    # Local development server
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
