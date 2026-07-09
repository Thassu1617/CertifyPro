import sys, traceback
try:
    from app import create_app
    app = create_app()
except Exception as e:
    print("STARTUP ERROR:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise
