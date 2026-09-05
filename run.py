import sys
import time
import multiprocessing
import uvicorn
from backend.app.config import settings
from backend.app.init_db import init_db


def run_gateway():
    print(f"[*] Starting Central Login Gateway on http://localhost:{settings.GATEWAY_PORT}")
    uvicorn.run(
        "backend.app.main_gateway:app",
        host=settings.HOST,
        port=settings.GATEWAY_PORT,
        log_level="info",
        reload=False
    )


def run_admin():
    print(f"[*] Starting Super Admin Portal on http://localhost:{settings.ADMIN_PORT}")
    uvicorn.run(
        "backend.app.main_admin:app",
        host=settings.HOST,
        port=settings.ADMIN_PORT,
        log_level="info",
        reload=False
    )


def run_calculator():
    print(f"[*] Starting Calculator API on http://localhost:{settings.CALCULATOR_PORT} (Docs: http://localhost:{settings.CALCULATOR_PORT}/docs)")
    uvicorn.run(
        "backend.app.main_calculator:app",
        host=settings.HOST,
        port=settings.CALCULATOR_PORT,
        log_level="info",
        reload=False
    )


def run_consumer():
    print(f"[*] Starting Consumer Developer Portal on http://localhost:{settings.CONSUMER_PORT}")
    uvicorn.run(
        "backend.app.main_consumer:app",
        host=settings.HOST,
        port=settings.CONSUMER_PORT,
        log_level="info",
        reload=False
    )


def main():
    print("=" * 75)
    print("  API CONSUMER USAGE & ANALYTICS CONSOLE")
    print("=" * 75)
    print(f"  [*] Central Gateway Portal:    http://localhost:{settings.GATEWAY_PORT}")
    print(f"  [1] Super Admin Portal:        http://localhost:{settings.ADMIN_PORT}")
    print(f"  [2] Calculator API:            http://localhost:{settings.CALCULATOR_PORT}")
    print(f"      FastAPI Swagger Docs:      http://localhost:{settings.CALCULATOR_PORT}/docs")
    print(f"  [3] API Consumer Portal:       http://localhost:{settings.CONSUMER_PORT}")
    print(f"  (*) Port 3000 Status:          UNTOUCHED / PRESERVED")
    print("=" * 75)

    # Initialize SQLite database and demo accounts
    init_db()

    processes = [
        multiprocessing.Process(target=run_gateway, name="GatewayPortal"),
        multiprocessing.Process(target=run_admin, name="AdminPortal"),
        multiprocessing.Process(target=run_calculator, name="CalculatorAPI"),
        multiprocessing.Process(target=run_consumer, name="ConsumerPortal")
    ]

    for p in processes:
        p.daemon = True
        p.start()

    print("\nAll services are running concurrently. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
            for p in processes:
                if not p.is_alive():
                    print(f"Process {p.name} stopped unexpectedly.")
                    sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping all services...")
        for p in processes:
            p.terminate()
            p.join(timeout=2)
        print("All services stopped.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
