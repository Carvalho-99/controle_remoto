#!/usr/bin/env python3
"""
RemotePC Server v2 — Windows
Autenticação por PIN + controle completo de mouse, teclado e mídia
Requisitos: pip install websockets pynput
"""

import asyncio
import json
import os
import socket
import threading
import http.server
import websockets
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# ─── CONFIGURAÇÃO ──────────────────────────────────────────────
PIN       = "1234"   # ← MUDE AQUI o seu PIN
WS_PORT   = 8765
HTTP_PORT = 8766
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ───────────────────────────────────────────────────────────────

mouse    = MouseController()
keyboard = KeyboardController()
authenticated = set()  # IPs autenticados

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# ─── VOLUME ────────────────────────────────────────────────────
def vol_up():   keyboard.press(Key.media_volume_up);   keyboard.release(Key.media_volume_up)
def vol_down(): keyboard.press(Key.media_volume_down); keyboard.release(Key.media_volume_down)
def vol_mute(): keyboard.press(Key.media_volume_mute); keyboard.release(Key.media_volume_mute)

# ─── BRIGHTNESS (Windows PowerShell) ───────────────────────────
def set_brightness(direction):
    delta = "+10" if direction == "up" else "-10"
    script = (
        "$m=(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness;"
        f"$n=[Math]::Max(0,[Math]::Min(100,$m+({delta})));"
        "(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,$n)"
    )
    os.system(f'powershell -WindowStyle Hidden -Command "{script}"')

# ─── KEYS ──────────────────────────────────────────────────────
SPECIAL_KEYS = {
    "enter": Key.enter, "space": Key.space, "backspace": Key.backspace,
    "escape": Key.esc, "tab": Key.tab, "delete": Key.delete,
    "left": Key.left, "right": Key.right, "up": Key.up, "down": Key.down,
    "home": Key.home, "end": Key.end, "page_up": Key.page_up, "page_down": Key.page_down,
    "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
    "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
    "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
    "caps_lock": Key.caps_lock, "num_lock": Key.num_lock,
    "print_screen": Key.print_screen, "insert": Key.insert,
    "media_play": Key.media_play_pause,
    "media_next": Key.media_next,
    "media_prev": Key.media_previous,
}

def press_key(key_name):
    if key_name in SPECIAL_KEYS:
        keyboard.press(SPECIAL_KEYS[key_name]); keyboard.release(SPECIAL_KEYS[key_name])
    elif len(key_name) == 1:
        keyboard.press(key_name); keyboard.release(key_name)

def do_combo(mod, key):
    mod_map = {"ctrl": Key.ctrl, "alt": Key.alt, "shift": Key.shift, "win": Key.cmd}
    if mod == "ctrl_shift":
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.shift): press_key(key)
    elif mod == "ctrl_alt":
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.alt): press_key(key)
    elif mod in mod_map:
        with keyboard.pressed(mod_map[mod]): press_key(key)

# ─── COMMAND DISPATCHER ────────────────────────────────────────
def handle_command(data):
    cmd = data.get("cmd")

    if cmd == "mousemove":
        mouse.move(int(data.get("dx", 0)), int(data.get("dy", 0)))
    elif cmd == "click":
        btn = Button.left if data.get("button","left") == "left" else Button.right
        mouse.click(btn, 1)
    elif cmd == "double_click":
        mouse.click(Button.left, 2)
    elif cmd == "right_click":
        mouse.click(Button.right, 1)
    elif cmd == "middle_click":
        mouse.click(Button.middle, 1)
    elif cmd == "scroll":
        mouse.scroll(0, -float(data.get("dy", 0)))

    elif cmd == "vol_up":   vol_up()
    elif cmd == "vol_down": vol_down()
    elif cmd == "vol_mute": vol_mute()

    elif cmd == "brightness":
        set_brightness(data.get("direction","up"))

    elif cmd == "media":
        mmap = {"play_pause": Key.media_play_pause, "next": Key.media_next, "prev": Key.media_previous}
        k = mmap.get(data.get("action",""))
        if k: keyboard.press(k); keyboard.release(k)

    elif cmd == "key":
        press_key(data.get("key",""))

    elif cmd == "combo":
        do_combo(data.get("mod","ctrl"), data.get("key",""))

    elif cmd == "type":
        keyboard.type(data.get("text",""))

    elif cmd == "lock":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif cmd == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif cmd == "shutdown":
        os.system("shutdown /s /t 30")
    elif cmd == "restart":
        os.system("shutdown /r /t 30")
    elif cmd == "cancel_shutdown":
        os.system("shutdown /a")

# ─── WEBSOCKET ─────────────────────────────────────────────────
async def ws_handler(websocket):
    addr = websocket.remote_address[0]
    print(f"[+] Conexão: {addr}")
    await websocket.send(json.dumps({"type": "auth_required" if addr not in authenticated else "auth_ok"}))
    try:
        async for msg in websocket:
            data = json.loads(msg)
            if data.get("cmd") == "auth":
                if data.get("pin") == PIN:
                    authenticated.add(addr)
                    await websocket.send(json.dumps({"type": "auth_ok"}))
                    print(f"[✓] {addr} autenticado")
                else:
                    await websocket.send(json.dumps({"type": "auth_fail"}))
                continue
            if addr not in authenticated:
                await websocket.send(json.dumps({"type": "auth_required"}))
                continue
            try:
                handle_command(data)
            except Exception as e:
                print(f"[!] Erro comando: {e}")
    except websockets.exceptions.ConnectionClosed:
        authenticated.discard(addr)
        print(f"[-] Desconectado: {addr}")

# ─── HTTP ──────────────────────────────────────────────────────
class AppHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = os.path.join(SCRIPT_DIR, "remotepc_app.html")
        try:
            with open(path, "rb") as f: content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)
    def log_message(self, *a): pass

def start_http():
    http.server.HTTPServer(("0.0.0.0", HTTP_PORT), AppHandler).serve_forever()

# ─── MAIN ──────────────────────────────────────────────────────
async def main():
    ip = get_local_ip()
    threading.Thread(target=start_http, daemon=True).start()
    print("=" * 54)
    print("  RemotePC v2 — Windows")
    print("=" * 54)
    print(f"  IP  : {ip}")
    print(f"  PIN : {PIN}")
    print(f"\n  Celular → http://{ip}:{HTTP_PORT}\n")
    print("  Ctrl+C para encerrar")
    print("=" * 54)
    async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Encerrado.")
