"""
Master application entrypoint for the API Consumer Analytics project.
Allows launching individual servers or all 3 services concurrently.
"""
import sys
import uvicorn
from backend.app.config import settings

def start_all():
    from run import main as run_all_main
    run_all_main()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        if target == "admin":
            uvicorn.run("backend.app.main_admin:app", host=settings.HOST, port=settings.ADMIN_PORT, reload=False)
        elif target == "calculator":
            uvicorn.run("backend.app.main_calculator:app", host=settings.HOST, port=settings.CALCULATOR_PORT, reload=False)
        elif target == "consumer":
            uvicorn.run("backend.app.main_consumer:app", host=settings.HOST, port=settings.CONSUMER_PORT, reload=False)
        else:
            print("Usage: python -m backend.app.main [admin|calculator|consumer]")
    else:
        start_all()
