#!/usr/bin/env python
"""
HomeHQ — Waitress + WhiteNoise Production Server
──────────────────────────────────────────────────
Static files are served directly by WhiteNoise middleware — no nginx,
no separate static file server needed. Works fully offline and air-gapped.

Usage:
    python serve.py                        # localhost:8000
    python serve.py --host 0.0.0.0        # all interfaces (LAN access)
    python serve.py --port 8080           # custom port
    python serve.py --host 0.0.0.0 --port 8080 --threads 8
    python serve.py --no-collectstatic    # skip collectstatic on startup

Environment variables:
    HOMEHQ_HOST     Override host    (default: 127.0.0.1)
    HOMEHQ_PORT     Override port    (default: 8000)
    HOMEHQ_THREADS  Override threads (default: 4)
"""

import os
import sys
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homehq.settings')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def main():
    parser = argparse.ArgumentParser(
        description='Start the HomeHQ Waitress + WhiteNoise server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--host',
        default=os.environ.get('HOMEHQ_HOST', '127.0.0.1'),
        help='Host to bind to (default: 127.0.0.1). Use 0.0.0.0 for LAN access.',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.environ.get('HOMEHQ_PORT', 8000)),
        help='Port to listen on (default: 8000)',
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=int(os.environ.get('HOMEHQ_THREADS', 4)),
        help='Number of Waitress worker threads (default: 4)',
    )
    parser.add_argument(
        '--no-collectstatic',
        action='store_true',
        help='Skip running collectstatic on startup',
    )
    args = parser.parse_args()

    import django
    django.setup()

    from django.core.management import call_command

    # ── System checks ─────────────────────────────────────────────────────────
    print("Running system checks...")
    try:
        call_command('check', verbosity=0)
    except SystemExit:
        print("ERROR: Django system check failed. Aborting.")
        sys.exit(1)

    # ── collectstatic ─────────────────────────────────────────────────────────
    # WhiteNoise serves from STATIC_ROOT, so we must populate it before serving.
    # This is fast on repeat runs — only changed files are reprocessed.
    if not args.no_collectstatic:
        print("Collecting static files...")
        try:
            call_command('collectstatic', verbosity=1, interactive=False)
        except Exception as e:
            print(f"WARNING: collectstatic failed: {e}")
            print("Continuing anyway — static files may be stale or missing.")
    else:
        print("Skipping collectstatic (--no-collectstatic)")

    # ── Start Waitress ────────────────────────────────────────────────────────
    from homehq.wsgi import application
    from waitress import serve

    lan_note = ""
    if args.host == "0.0.0.0":
        import socket
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            lan_note = f"\n  Local Network : http://{local_ip}:{args.port}"
        except Exception:
            pass

    print(f"""
╔══════════════════════════════════════════════╗
║         HomeHQ  ·  Waitress + WhiteNoise     ║
╚══════════════════════════════════════════════╝

  Listening on : http://{args.host}:{args.port}{lan_note}
  Threads      : {args.threads}
  Static files : Served by WhiteNoise (no separate server needed)
  Press Ctrl+C to stop.
""")

    try:
        serve(
            application,
            host=args.host,
            port=args.port,
            threads=args.threads,
            connection_limit=100,
            channel_timeout=60,
            cleanup_interval=30,
            max_request_body_size=50 * 1024 * 1024,  # 50 MB for file uploads
            ident='HomeHQ/Waitress',
        )
    except KeyboardInterrupt:
        print("\nHomeHQ stopped.")


if __name__ == '__main__':
    main()
