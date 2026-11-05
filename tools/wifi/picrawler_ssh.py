#!/usr/bin/env python3
"""Lance la connexion SSH au robot ; ouvre d'abord la fenêtre WiFi si les réseaux diffèrent.

Usage : python picrawler_ssh.py [--host 192.168.1.200] [--user pi]
"""
import argparse
import os
import subprocess
import sys

import wifi_check as core

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="192.168.1.200")
ap.add_argument("--user", default="pi")
a = ap.parse_args()

st = core.get_status(a.host, a.user)
if not st["error"] and st["pc"] and st["pc"] not in st["known"]:
    print(f"Le robot ne connaît pas « {st['pc']} » : ouverture de la fenêtre WiFi…")
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "wifi_widget.py"), "--host", a.host, "--user", a.user])
os.execvp("ssh", ["ssh", f"{a.user}@{a.host}"])
