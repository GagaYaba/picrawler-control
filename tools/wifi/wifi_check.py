#!/usr/bin/env python3
"""Vérifie (en LECTURE SEULE) si le PC et le robot PiCrawler sont sur le même WiFi.

Ne modifie rien sur le Pi : seules des commandes `nmcli ... show` / `list` sont lancées.
Aucun mot de passe WiFi n'est lu, affiché ni stocké.

Usage :
    python wifi_check.py                       # pi@192.168.1.200 par défaut
    python wifi_check.py --host 192.168.1.200 --user pi
    python wifi_check.py --add-help MonReseau  # affiche la commande d'ajout (sans l'exécuter)
"""
import argparse
import platform
import shlex
import subprocess
import sys


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr).strip()


def parse_netsh(text):
    """SSID courant depuis `netsh wlan show interfaces` (ignore la ligne BSSID)."""
    for line in text.splitlines():
        key, _, val = line.partition(":")
        if key.strip().lower() == "ssid" and val.strip():
            return val.strip()
    return None


def parse_nmcli_terse(text):
    """Lignes `nmcli -t` -> listes de champs (gère les ':' échappés par '\\:')."""
    rows = []
    for line in text.splitlines():
        fields, cur, esc = [], "", False
        for ch in line:
            if esc:
                cur += ch
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == ":":
                fields.append(cur)
                cur = ""
            else:
                cur += ch
        fields.append(cur)
        rows.append(fields)
    return rows


def pc_ssid():
    system = platform.system()
    if system == "Windows":
        code, out = run(["netsh", "wlan", "show", "interfaces"])
        return parse_netsh(out) if code == 0 else None
    if system == "Linux":
        code, out = run(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"])
        if code == 0:
            for active, *ssid in parse_nmcli_terse(out):
                if active == "yes":
                    return ":".join(ssid)
    return None


def ssh_read(host, user, remote_cmd):
    return run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                f"{user}@{host}", remote_cmd])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="192.168.1.200")
    ap.add_argument("--user", default="pi")
    ap.add_argument("--add-help", metavar="SSID",
                    help="affiche la commande pour ajouter ce réseau (n'exécute rien)")
    args = ap.parse_args()

    if args.add_help:
        print("À lancer SUR LE PI (en SSH, Gaëlle présente, avant de partir) :\n")
        q = shlex.quote(args.add_help)
        print(f"  read -rs -p 'Mot de passe WiFi : ' PSK; echo")
        print(f"  sudo nmcli connection add type wifi con-name {q} ssid {q} \\")
        print('      wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PSK" connection.autoconnect yes')
        print("  unset PSK")
        print("\nCette commande ENREGISTRE le réseau sans y basculer : la session SSH en cours ne coupe pas.")
        print("Le mot de passe est saisi en direct (non affiché), jamais écrit dans un fichier ni ici.")
        print("Ne supprime pas l'ancien réseau : il sert de secours. Réseau avec portail captif (hôtel, école) : voir docs/wifi-cadrage.md.")
        return 0

    mine = pc_ssid()
    print(f"WiFi du PC     : {mine or 'inconnu / non connecté en WiFi'}")

    code, out = ssh_read(args.host, args.user,
                         "nmcli -t -f NAME,TYPE,DEVICE connection show --active")
    if code != 0:
        print(f"Robot ({args.user}@{args.host}) : injoignable en SSH -> {out or 'pas de réponse'}")
        print("\nCauses probables : PC et robot pas sur le même réseau, IP différente, "
              "ou isolation entre appareils (réseau public/hôtel/école).")
        return 2
    active = [r for r in parse_nmcli_terse(out) if len(r) >= 3 and r[1] == "802-11-wireless"]
    robot = active[0][0] if active else None
    print(f"WiFi du robot  : {robot or 'pas de WiFi actif (câble ?)'}")

    code, out = ssh_read(args.host, args.user, "nmcli -t -f NAME,TYPE connection show")
    known = [r[0] for r in parse_nmcli_terse(out) if len(r) >= 2 and r[1] == "802-11-wireless"] if code == 0 else []
    print(f"Réseaux connus du robot : {', '.join(known) or 'aucun'}")

    if mine and mine in known:
        print(f"\nOK : le robot connaît « {mine} ». Il s'y connectera tout seul s'il est à portée.")
        return 0
    if mine:
        print(f"\nATTENTION : le robot ne connaît PAS « {mine} ». Ajoute-le AVANT de partir :")
        print(f"  python wifi_check.py --add-help {shlex.quote(mine)}")
        return 1
    print("\nImpossible de connaître le WiFi du PC, compare à la main.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
