import uvicorn
import os
import sys

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Ticket to Ride Backend API on port {port}")
    print(f"📡 Host: 0.0.0.0")
    print(f"🌐 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print(f"📋 Python version: {sys.version}")
    
    try:
        uvicorn.run(
            "railway-main:app", 
            host="0.0.0.0", 
            port=port, 
            log_level="info", 
            access_log=True,
            reload=False
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
