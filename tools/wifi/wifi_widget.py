#!/usr/bin/env python3
"""Petite fenêtre pour voir et ajouter les réseaux WiFi du robot PiCrawler.

Lecture au démarrage (comme wifi_check.py). L'ajout d'un réseau n'écrit sur le Pi
qu'après ton clic sur le bouton de validation ET une confirmation.
Le mot de passe n'est ni affiché, ni enregistré sur le PC.

Usage : python wifi_widget.py [--host 192.168.1.200] [--user pi]
"""
import argparse
import queue
import threading
import tkinter as tk
from tkinter import messagebox

import wifi_check as core

BG, CARD, BTN = "#151515", "#222220", "#2C2C2A"
TXT, MUTED, WARN, OK = "#F2F0E8", "#A8A59B", "#E8A488", "#8FCB9B"
FONT = "Segoe UI"
W, H = 420, 720


class Pill(tk.Canvas):
    """Zone arrondie ; mettre les widgets dans `.inner`."""

    def __init__(self, parent, height=64, r=28):
        super().__init__(parent, width=W - 36, height=height, bg=BG, highlightthickness=0)
        w = W - 36
        pts = [r, 0, w - r, 0, w, 0, w, r, w, height - r, w, height, w - r, height,
               r, height, 0, height, 0, height - r, 0, r, 0, 0]
        self.create_polygon(pts, smooth=True, fill=CARD, outline=CARD)
        self.inner = tk.Frame(self, bg=CARD)
        self.create_window(w // 2, height // 2, window=self.inner, width=w - 40, height=height - 8)


class App(tk.Tk):
    def __init__(self, host, user):
        super().__init__()
        self.host, self.user = host, user
        self.title("Réseau du robot")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.q = queue.Queue()
        self.status = None
        self.main_frame = tk.Frame(self, bg=BG)
        self.add_frame = tk.Frame(self, bg=BG)
        self.build_main()
        self.build_add()
        self.show(self.main_frame)
        self.after(100, self.poll)
        self.refresh()

    # ---------- utilitaires ----------
    def show(self, frame):
        for f in (self.main_frame, self.add_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True, padx=18, pady=20)

    def header(self, parent, title, left, right=None):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x")
        for side, (txt, cmd) in (("left", left), ("right", right or ("", None))):
            if txt:
                tk.Button(bar, text=txt, command=cmd, bg=BTN, fg=TXT, bd=0, relief="flat",
                          activebackground="#3A3A37", activeforeground=TXT,
                          font=(FONT, 14), width=3, height=1).pack(side=side)
            else:
                tk.Frame(bar, width=48, bg=BG).pack(side=side)
        tk.Label(bar, text=title, bg=BG, fg=TXT, font=(FONT, 15, "bold")).pack(expand=True)

    def label(self, parent, text, color=MUTED, size=11, **kw):
        return tk.Label(parent, text=text, bg=BG, fg=color, font=(FONT, size), anchor="w", **kw)

    def line(self, parent, text):
        p = Pill(parent, 56)
        lab = tk.Label(p.inner, text=text, bg=CARD, fg=TXT, font=(FONT, 13), anchor="w")
        lab.pack(fill="both", expand=True)
        return p, lab

    # ---------- écran principal ----------
    def build_main(self):
        f = self.main_frame
        self.header(f, "Réseau du robot", ("✕", self.destroy), ("↻", self.refresh))
        self.label(f, "Ton PC").pack(fill="x", padx=8, pady=(18, 4))
        p, self.pc_lab = self.line(f, "…")
        p.pack()
        self.label(f, f"Robot · {self.host}").pack(fill="x", padx=8, pady=(12, 4))
        p, self.robot_lab = self.line(f, "…")
        p.pack()
        self.msg = tk.Label(f, text="", bg=BG, fg=WARN, font=(FONT, 11), anchor="w",
                            justify="left", wraplength=W - 60)
        self.msg.pack(fill="x", padx=8, pady=(6, 0))
        self.label(f, "Réseaux connus du robot").pack(fill="x", padx=8, pady=(12, 4))
        self.known = tk.Label(f, text="", bg=CARD, fg=TXT, font=(FONT, 13), anchor="nw",
                              justify="left", padx=20, pady=14, wraplength=W - 80)
        self.known.pack(fill="x")
        self.add_btn = tk.Button(f, text="＋  Ajouter ce réseau", command=self.open_add,
                                 bg=CARD, fg=TXT, bd=0, relief="flat", anchor="w", padx=20,
                                 activebackground="#2C2C2A", activeforeground=TXT,
                                 font=(FONT, 13, "bold"), height=2, state="disabled")
        self.add_btn.pack(side="bottom", fill="x")
        tk.Label(f, text="Le robot reste connecté pendant l'ajout.", bg=BG, fg=MUTED,
                 font=(FONT, 10)).pack(side="bottom", pady=(0, 8))

    def refresh(self):
        self.msg.config(text="Lecture du robot…", fg=MUTED)
        self.add_btn.config(state="disabled")
        threading.Thread(target=lambda: self.q.put(("status", core.get_status(self.host, self.user))),
                         daemon=True).start()

    def apply_status(self, st):
        self.status = st
        mine = st["pc"]
        self.pc_lab.config(text=mine or "inconnu")
        if st["error"]:
            self.robot_lab.config(text="injoignable")
            self.known.config(text="—")
            self.msg.config(fg=WARN, text="Le robot ne répond pas en SSH. Vérifie qu'il est allumé et sur le "
                            "même réseau que ton PC (ou isolation entre appareils sur un WiFi public).")
            return
        self.robot_lab.config(text=st["robot"] or "pas de WiFi actif")
        self.known.config(text="\n".join(st["known"]) or "aucun")
        self.add_btn.config(state="normal")
        if mine and mine in st["known"]:
            self.msg.config(fg=OK, text=f"Le robot connaît « {mine} ». Rien à faire.")
        elif mine:
            self.msg.config(fg=WARN, text="Le robot est sur un autre réseau que ton PC. "
                            "Ajoute celui-ci pour qu'il s'y connecte.")
        else:
            self.msg.config(fg=WARN, text="WiFi du PC inconnu : saisis le nom du réseau à ajouter.")

    # ---------- écran d'ajout ----------
    def build_add(self):
        f = self.add_frame
        self.header(f, "Ajouter un réseau", ("✕", lambda: self.show(self.main_frame)),
                    ("✓", self.save))
        self.label(f, "Nom du réseau").pack(fill="x", padx=8, pady=(18, 4))
        p = Pill(f)
        self.ssid = tk.Entry(p.inner, bg=CARD, fg=TXT, insertbackground=TXT, bd=0,
                             highlightthickness=0, font=(FONT, 13))
        self.ssid.pack(fill="both", expand=True)
        p.pack()
        self.label(f, "Repris du réseau actuel de ton PC.", size=10).pack(fill="x", padx=8, pady=(4, 0))
        self.label(f, "Mot de passe WiFi").pack(fill="x", padx=8, pady=(16, 4))
        p = Pill(f)
        self.psk = tk.Entry(p.inner, show="•", bg=CARD, fg=TXT, insertbackground=TXT, bd=0,
                            highlightthickness=0, font=(FONT, 13))
        self.psk.pack(fill="both", expand=True)
        p.pack()
        self.label(f, "Envoyé directement au robot, jamais enregistré sur le PC.",
                   size=10).pack(fill="x", padx=8, pady=(4, 0))
        self.err = tk.Label(f, text="", bg=BG, fg=WARN, font=(FONT, 11), anchor="w",
                            justify="left", wraplength=W - 60)
        self.err.pack(fill="x", padx=8, pady=(14, 0))
        tk.Label(f, text="Le réseau est enregistré sans couper la connexion actuelle.\n"
                 "L'ancien réseau reste disponible en secours.", bg=CARD, fg="#D2CFC5",
                 font=(FONT, 11), justify="left", padx=20, pady=16).pack(side="bottom", fill="x")

    def open_add(self):
        self.ssid.delete(0, "end")
        if self.status and self.status["pc"]:
            self.ssid.insert(0, self.status["pc"])
        self.psk.delete(0, "end")
        self.err.config(text="")
        self.show(self.add_frame)
        self.psk.focus_set()

    def save(self):
        ssid, psk = self.ssid.get().strip(), self.psk.get()
        if not ssid:
            self.err.config(text="Le nom du réseau est vide.")
            return
        if not 8 <= len(psk) <= 63:
            self.err.config(text="Un mot de passe WPA fait entre 8 et 63 caractères.")
            return
        if not messagebox.askyesno("Confirmer", f"Enregistrer « {ssid} » sur le robot ?\n"
                                   "Tu dois être devant le robot pour reprendre la main si besoin."):
            return
        self.err.config(fg=MUTED, text="Enregistrement…")
        threading.Thread(target=lambda: self.q.put(("added", core.add_network(self.host, self.user, ssid, psk))),
                         daemon=True).start()
        self.psk.delete(0, "end")  # le mot de passe ne reste pas dans la fenêtre

    def poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "status":
                    self.apply_status(data)
                else:
                    ok, info = data
                    if ok:
                        self.show(self.main_frame)
                        self.refresh()
                    else:
                        self.err.config(fg=WARN, text=f"Échec : {info or 'erreur inconnue'}")
        except queue.Empty:
            pass
        self.after(100, self.poll)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="192.168.1.200")
    ap.add_argument("--user", default="pi")
    a = ap.parse_args()
    App(a.host, a.user).mainloop()
