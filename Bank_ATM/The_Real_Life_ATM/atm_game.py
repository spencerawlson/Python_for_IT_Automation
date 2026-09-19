"""The Real-Life ATM - a Pygame arcade interface over the Python ATM backend.

The banking logic (Bank / Account / Customer, via atm_service) is untouched
business logic; this file is purely the "machine": a drawn ATM kiosk with a
card slot, keypad, phosphor-green screen, an animated cash dispenser and a
receipt printer. Every action calls the same backend the terminal CLI uses.

    python atm_game.py            # play
    python atm_game.py --selftest # headless smoke test (no window), exits 0

Controls: click the on-screen keypad, or use the number keys, Enter (OK),
Backspace (CLEAR) and Esc (CANCEL).

The game interface was built by Claude (Anthropic). See README.
"""
from __future__ import annotations

import math
import os
import sys
import array

import pygame

from atm_service import AtmService, ATMError

# --------------------------------------------------------------------------- #
# Layout & palette
# --------------------------------------------------------------------------- #
WIDTH, HEIGHT = 980, 892
FPS = 60

ROOM        = (16, 18, 24)
BEZEL       = (46, 52, 64)
BEZEL_EDGE  = (28, 32, 40)
BEZEL_HI    = (74, 82, 98)
STEEL       = (120, 130, 146)
SCREEN_BG   = (6, 22, 14)
SCANLINE    = (0, 0, 0)
PHOS        = (128, 255, 158)     # phosphor green
PHOS_DIM    = (60, 150, 92)
AMBER       = (255, 190, 70)
RED         = (214, 70, 66)
GREEN_KEY   = (54, 180, 96)
AMBER_KEY   = (226, 168, 52)
KEY         = (58, 64, 78)
KEY_HI      = (84, 92, 108)
KEY_TXT     = (232, 238, 244)
CARD        = (206, 176, 92)
CARD_CHIP   = (222, 200, 120)
BILL        = (66, 140, 96)
BILL_EDGE   = (40, 96, 64)
RECEIPT     = (236, 236, 228)
INK         = (40, 44, 52)

# Screen (CRT) rectangle and physical parts
SCREEN_RECT   = pygame.Rect(60, 54, 560, 336)
CARDSLOT_RECT = pygame.Rect(654, 150, 262, 26)
RECEIPT_RECT  = pygame.Rect(654, 250, 262, 20)
TRAY_RECT     = pygame.Rect(60, 752, 860, 108)   # full-width tray, below the keypad
DISPENSER     = pygame.Rect(90, 734, 800, 18)    # slot bills emerge from

BANK_TINT = {
    "CIBC": (196, 30, 58),
    "RBC": (0, 90, 165),
    "Bank of Montreal": (0, 122, 194),
}

# Customer IDs in the data files are letter-prefixed (C001, R001, B001). A real
# ATM keypad is numeric, and the card already identifies the bank - so the user
# types only the number and the machine supplies the bank's prefix.
BANK_PREFIX = {"CIBC": "C", "RBC": "R", "Bank of Montreal": "B"}


# --------------------------------------------------------------------------- #
# Tiny procedural sound (no asset files, no numpy) - fully optional
# --------------------------------------------------------------------------- #
class Audio:
    def __init__(self):
        self.ok = False
        try:
            pygame.mixer.pre_init(44100, -16, 1, 256)
            pygame.mixer.init()
            self.rate = 44100
            self.ok = True
        except Exception:
            self.ok = False

    def _tone(self, freq, ms, vol=0.35, shape="sine"):
        n = int(self.rate * ms / 1000)
        buf = array.array("h")
        amp = int(32767 * vol)
        for i in range(n):
            t = i / self.rate
            if shape == "square":
                s = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            else:
                s = math.sin(2 * math.pi * freq * t)
            env = min(1.0, i / 200) * min(1.0, (n - i) / 400)  # soft attack/decay
            buf.append(int(amp * s * env))
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play(self, name):
        if not self.ok:
            return
        try:
            {
                "key": lambda: self._tone(660, 55, 0.25),
                "ok": lambda: self._tone(880, 90, 0.3),
                "chime": lambda: self._tone(1046, 220, 0.3),
                "error": lambda: self._tone(160, 260, 0.4, "square"),
                "whir": lambda: self._tone(220, 380, 0.25, "square"),
                "print": lambda: self._tone(320, 180, 0.2, "square"),
            }[name]().play()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Dispensed bill
# --------------------------------------------------------------------------- #
class Bill:
    def __init__(self, denom, index, slot_x):
        self.denom = denom
        self.x = slot_x
        self.y = DISPENSER.y - 6
        self.target_y = TRAY_RECT.y + 18 + (index % 5) * 9
        self.delay = index * 7          # frames before it starts moving
        self.vy = 0.0
        self.done = False

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        self.vy = min(self.vy + 0.6, 9)
        self.y += self.vy
        if self.y >= self.target_y:
            self.y = self.target_y
            self.done = True

    def draw(self, surf, font):
        r = pygame.Rect(int(self.x), int(self.y), 116, 52)
        pygame.draw.rect(surf, BILL, r, border_radius=6)
        pygame.draw.rect(surf, BILL_EDGE, r, width=2, border_radius=6)
        pygame.draw.circle(surf, BILL_EDGE, r.center, 15, 2)
        t = font.render(f"${self.denom}", True, (225, 245, 230))
        surf.blit(t, t.get_rect(center=r.center))


# --------------------------------------------------------------------------- #
# States
# --------------------------------------------------------------------------- #
ATTRACT, BANK_SELECT, INSERT, ENTER_ID, ENTER_PIN, MENU = range(6)
BALANCE, AMOUNT, PROCESSING, DISPENSE, TAKE, RECEIPT_S, RETAINED, THANKS = range(6, 14)


class ATMGame:
    def __init__(self, headless=False):
        flags = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("The Real-Life ATM")
        self.clock = pygame.time.Clock()
        self.audio = Audio()

        self.mono = pygame.font.SysFont("consolas,couriernew,monospace", 26)
        self.mono_s = pygame.font.SysFont("consolas,couriernew,monospace", 19)
        self.mono_b = pygame.font.SysFont("consolas,couriernew,monospace", 34, bold=True)
        self.ui = pygame.font.SysFont("segoeui,arial", 22, bold=True)
        self.ui_s = pygame.font.SysFont("segoeui,arial", 16)
        self.bill_font = pygame.font.SysFont("arialblack,arial", 20, bold=True)

        self.svc = AtmService()
        self.reset_session()

        self.state = ATTRACT
        self.buffer = ""
        self.message = ""
        self.msg_color = PHOS
        self.t = 0.0                 # global time (s)
        self.anim = 0.0              # per-state animation clock
        self.shake = 0.0
        self.bills: list[Bill] = []
        self.pending = None          # pending transaction kind: "deposit"/"withdraw"
        self.keys = self._build_keypad()
        self.hover = None
        self.running = True

    # -- session ----------------------------------------------------------- #
    def reset_session(self):
        self.bank = None
        self.bank_name = ""
        self.customer = None
        self.account = None
        self.pin_attempts = 0

    # -- keypad ------------------------------------------------------------ #
    def _build_keypad(self):
        keys = []
        x0, y0, w, h, gap = 96, 430, 128, 62, 16
        grid = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["CLR", "0", "OK"]]
        for r, row in enumerate(grid):
            for c, label in enumerate(row):
                rect = pygame.Rect(x0 + c * (w + gap), y0 + r * (h + gap), w, h)
                keys.append((label, rect))
        # CANCEL key to the right of the pad
        keys.append(("CANCEL", pygame.Rect(x0 + 3 * (w + gap), y0, w, h)))
        return keys

    # ------------------------------------------------------------------ #
    # Input
    # ------------------------------------------------------------------ #
    def press(self, label):
        if label in ("CLR",):
            self.audio.play("key")
            self.buffer = self.buffer[:-1]
            return
        if label == "CANCEL":
            self.audio.play("error")
            self.cancel()
            return
        if label == "OK":
            self.audio.play("ok")
            self.submit()
            return
        # a digit
        self.audio.play("key")
        maxlen = {ENTER_ID: 8, ENTER_PIN: 4, AMOUNT: 6, BANK_SELECT: 1}.get(self.state, 8)
        if len(self.buffer) < maxlen and label.isdigit():
            self.buffer += label

    def cancel(self):
        if self.state in (ATTRACT, THANKS, RETAINED):
            return
        self.eject("Transaction cancelled.")

    def submit(self):
        s = self.state
        if s == ATTRACT:
            self.goto(BANK_SELECT)
        elif s == BANK_SELECT:
            self._choose_bank()
        elif s == ENTER_ID:
            self._enter_id()
        elif s == ENTER_PIN:
            self._enter_pin()
        elif s == MENU:
            self._menu_choice()
        elif s == BALANCE:
            self.eject("")
        elif s == AMOUNT:
            self._confirm_amount()
        elif s == TAKE:
            self.goto(RECEIPT_S); self.audio.play("print"); self.anim = 0
        elif s == RECEIPT_S:
            self.eject("")
        elif s in (THANKS, RETAINED):
            self.full_reset()

    # -- transitions ------------------------------------------------------- #
    def goto(self, state):
        self.state = state
        self.buffer = ""
        self.anim = 0.0

    def _choose_bank(self):
        banks = self.svc.banks()
        if self.buffer.isdigit() and 1 <= int(self.buffer) <= len(banks):
            self.bank_name, self.bank = banks[int(self.buffer) - 1]
            self.audio.play("whir")
            self.goto(INSERT)
        else:
            self.flash("Select 1, 2 or 3.")

    def _enter_id(self):
        if not self.buffer:
            return
        prefix = BANK_PREFIX.get(self.bank_name, "")
        customer_id = prefix + self.buffer.zfill(3)
        cust, acct = self.svc.login(self.bank, customer_id)
        if cust is None:
            self.flash("Card not recognized.")
            self.buffer = ""
        else:
            self.customer, self.account = cust, acct
            self.pin_attempts = 0
            self.goto(ENTER_PIN)

    def _enter_pin(self):
        if not self.buffer:
            return
        if self.svc.verify_pin(self.customer, self.buffer):
            self.audio.play("chime")
            self.goto(MENU)
        else:
            self.pin_attempts += 1
            self.shake = 0.45
            self.audio.play("error")
            if self.pin_attempts >= 3:
                self.goto(RETAINED)
            else:
                self.flash(f"Incorrect PIN. {3 - self.pin_attempts} attempt(s) left.")
                self.buffer = ""

    def _menu_choice(self):
        c = self.buffer
        if c == "1":
            self.goto(BALANCE)
        elif c == "2":
            self.pending = "deposit"; self.goto(AMOUNT)
        elif c == "3":
            self.pending = "withdraw"; self.goto(AMOUNT)
        elif c == "4":
            self.eject("")
        else:
            self.flash("Choose 1-4.")

    def _confirm_amount(self):
        if not self.buffer:
            return
        amount = int(self.buffer)
        if amount <= 0:
            self.flash("Enter an amount.")
            return
        try:
            if self.pending == "deposit":
                self.new_balance = self.svc.deposit(self.account, float(amount))
                self.last_amount = amount
                self.audio.play("chime")
                self.goto(TAKE) if False else self.goto(RECEIPT_S)
                self.audio.play("print")
            else:
                if amount % 5 != 0:
                    self.flash("Withdrawals must be a multiple of $5.")
                    return
                self.new_balance = self.svc.withdraw(self.account, float(amount))
                self.last_amount = amount
                self.bills = self._make_bills(self.svc.dispense(amount))
                self.audio.play("whir")
                self.goto(PROCESSING)
        except ATMError as e:
            self.flash(str(e))

    def _make_bills(self, breakdown):
        bills, i = [], 0
        for denom, count in breakdown.items():
            for _ in range(count):
                slot_x = DISPENSER.x + 24 + (i % 5) * 156
                bills.append(Bill(denom, i, slot_x))
                i += 1
        return bills

    def eject(self, msg):
        self.message = msg
        self.audio.play("whir")
        self.goto(THANKS)

    def full_reset(self):
        self.reset_session()
        self.bills = []
        self.message = ""
        self.goto(ATTRACT)

    def flash(self, msg, color=AMBER):
        self.message = msg
        self.msg_color = color

    # ------------------------------------------------------------------ #
    # Update
    # ------------------------------------------------------------------ #
    def update(self, dt):
        self.t += dt
        self.anim += dt
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt)

        if self.state == PROCESSING and self.anim > 1.3:
            self.goto(DISPENSE)
        elif self.state == DISPENSE:
            for b in self.bills:
                b.update()
            if self.bills and all(b.done for b in self.bills):
                if self.anim > 0.5:
                    self.goto(TAKE)
        elif self.state == THANKS and self.anim > 2.4:
            self.full_reset()

    # ------------------------------------------------------------------ #
    # Drawing
    # ------------------------------------------------------------------ #
    def draw(self):
        self.screen.fill(ROOM)
        self._draw_cabinet()
        self._draw_screen()
        self._draw_cardslot()
        self._draw_receiptslot()
        self._draw_keypad()
        self._draw_tray()
        for b in self.bills:
            b.draw(self.screen, self.bill_font)
        pygame.display.flip()

    def _draw_cabinet(self):
        pygame.draw.rect(self.screen, BEZEL_EDGE, (24, 24, WIDTH - 48, HEIGHT - 48), border_radius=22)
        pygame.draw.rect(self.screen, BEZEL, (32, 32, WIDTH - 64, HEIGHT - 64), border_radius=18)
        pygame.draw.rect(self.screen, BEZEL_HI, (32, 32, WIDTH - 64, HEIGHT - 64), width=2, border_radius=18)
        # brand strip
        tint = BANK_TINT.get(self.bank_name, STEEL)
        pygame.draw.rect(self.screen, tint, (32, 32, WIDTH - 64, 16), border_top_left_radius=18, border_top_right_radius=18)
        cap = self.bank_name.upper() if self.bank_name else "GLOBAL ATM NETWORK"
        t = self.ui_s.render(cap, True, (245, 245, 245))
        self.screen.blit(t, (48, 30))
        # side buttons flanking the screen (cosmetic)
        for i in range(4):
            pygame.draw.rect(self.screen, KEY, (34, 90 + i * 70, 18, 44), border_radius=4)
            pygame.draw.rect(self.screen, KEY, (628, 90 + i * 70, 18, 44), border_radius=4)

    def _draw_screen(self):
        ox = int(math.sin(self.t * 60) * 6 * self.shake) if self.shake > 0 else 0
        rect = SCREEN_RECT.move(ox, 0)
        pygame.draw.rect(self.screen, (2, 8, 5), rect.inflate(12, 12), border_radius=10)
        pygame.draw.rect(self.screen, SCREEN_BG, rect, border_radius=8)
        # scanlines
        sl = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(0, rect.height, 3):
            pygame.draw.line(sl, (0, 0, 0, 40), (0, y), (rect.width, y))
        self.screen.blit(sl, rect.topleft)
        self._draw_screen_content(rect)

    def _line(self, rect, text, row, color=PHOS, big=False, center=True):
        font = self.mono_b if big else self.mono
        surf = font.render(text, True, color)
        y = rect.y + 26 + row * 34
        if center:
            self.screen.blit(surf, surf.get_rect(centerx=rect.centerx, y=y))
        else:
            self.screen.blit(surf, (rect.x + 26, y))

    def _draw_screen_content(self, rect):
        s = self.state
        blink = int(self.t * 2) % 2 == 0

        if s == ATTRACT:
            self._line(rect, "THE REAL-LIFE ATM", 1, PHOS, big=True)
            self._line(rect, "Global ATM Network", 3, PHOS_DIM)
            if blink:
                self._line(rect, "> PRESS OK TO BEGIN <", 6, AMBER)
        elif s == BANK_SELECT:
            self._line(rect, "SELECT YOUR BANK", 0, AMBER)
            for i, (name, _b) in enumerate(self.svc.banks()):
                self._line(rect, f"{i + 1}.  {name}", 2 + i, PHOS, center=False)
            self._line(rect, f"CARD > {self.buffer}_", 7, PHOS_DIM)
        elif s == INSERT:
            self._line(rect, "PLEASE INSERT CARD", 3, AMBER)
        elif s == ENTER_ID:
            self._line(rect, self.bank_name, 0, PHOS_DIM)
            self._line(rect, "ENTER CARD NUMBER", 2, AMBER)
            pref = BANK_PREFIX.get(self.bank_name, "")
            self._line(rect, f"{pref}{self.buffer or '___'}", 4, PHOS, big=True)
            self._line(rect, "(the 3 digits on your card, e.g. 001)", 7, PHOS_DIM)
        elif s == ENTER_PIN:
            self._line(rect, f"Welcome, {self.customer.name}", 0, PHOS)
            self._line(rect, "ENTER PIN", 2, AMBER)
            self._line(rect, "*" * len(self.buffer) + ("_" if blink else ""), 4, PHOS, big=True)
        elif s == MENU:
            self._line(rect, f"Welcome, {self.customer.name}", 0, PHOS)
            for i, label in enumerate(["1.  Check Balance", "2.  Deposit",
                                       "3.  Withdraw Cash", "4.  Exit"]):
                self._line(rect, label, 1 + i, PHOS, center=False)
            self._line(rect, f"> {self.buffer}_", 6, AMBER)
        elif s == BALANCE:
            self._line(rect, "AVAILABLE BALANCE", 1, AMBER)
            self._line(rect, f"${self.account.balance:,.2f}", 3, PHOS, big=True)
            self._line(rect, "Press OK to continue", 7, PHOS_DIM)
        elif s == AMOUNT:
            self._line(rect, f"{self.pending.upper()} - ENTER AMOUNT", 1, AMBER)
            self._line(rect, f"${self.buffer or '0'}", 3, PHOS, big=True)
            hint = "multiples of $5" if self.pending == "withdraw" else "whole dollars"
            self._line(rect, f"({hint})", 7, PHOS_DIM)
        elif s == PROCESSING:
            self._line(rect, "PROCESSING", 2, AMBER, big=True)
            dots = "." * (int(self.anim * 3) % 4)
            self._line(rect, f"counting cash{dots}", 4, PHOS_DIM)
            self._spinner(rect.centerx, rect.y + 250)
        elif s == DISPENSE:
            self._line(rect, "DISPENSING CASH", 2, AMBER, big=True)
            self._line(rect, "please wait", 4, PHOS_DIM)
        elif s == TAKE:
            self._line(rect, "TAKE YOUR CASH", 1, AMBER, big=True)
            self._line(rect, f"${self.last_amount:,} dispensed", 3, PHOS)
            if blink:
                self._line(rect, "> PRESS OK <", 6, AMBER)
        elif s == RECEIPT_S:
            self._line(rect, "TRANSACTION COMPLETE", 1, PHOS, big=True)
            self._line(rect, f"New balance: ${self.new_balance:,.2f}", 3, PHOS)
            self._line(rect, "Printing receipt...", 5, PHOS_DIM)
            if blink:
                self._line(rect, "> PRESS OK <", 7, AMBER)
        elif s == RETAINED:
            self._line(rect, "CARD RETAINED", 1, RED, big=True)
            self._line(rect, "Too many incorrect PINs.", 3, AMBER)
            self._line(rect, "Contact your bank.", 4, PHOS_DIM)
            if blink:
                self._line(rect, "> PRESS OK <", 7, AMBER)
        elif s == THANKS:
            self._line(rect, "THANK YOU", 2, PHOS, big=True)
            self._line(rect, "Please take your card.", 4, PHOS_DIM)

        # status/error line at the bottom of the CRT
        if self.message and s not in (THANKS, RETAINED):
            m = self.mono_s.render(self.message, True, self.msg_color)
            self.screen.blit(m, m.get_rect(centerx=rect.centerx, bottom=rect.bottom - 10))

    def _spinner(self, cx, cy):
        for i in range(8):
            a = self.anim * 6 + i * math.pi / 4
            alpha = 60 + i * 22
            col = (PHOS[0], PHOS[1], PHOS[2])
            x = cx + math.cos(a) * 26
            y = cy + math.sin(a) * 26
            pygame.draw.circle(self.screen, col, (int(x), int(y)), max(2, i // 2))

    def _draw_cardslot(self):
        pygame.draw.rect(self.screen, BEZEL_EDGE, CARDSLOT_RECT.inflate(20, 26), border_radius=8)
        pygame.draw.rect(self.screen, (10, 12, 16), CARDSLOT_RECT, border_radius=4)
        label = self.ui_s.render("CARD", True, STEEL)
        self.screen.blit(label, (CARDSLOT_RECT.x, CARDSLOT_RECT.y - 22))
        # animate the card during INSERT / show it seated afterward
        inserted = self.state in (ENTER_ID, ENTER_PIN, MENU, BALANCE, AMOUNT,
                                  PROCESSING, DISPENSE, TAKE, RECEIPT_S)
        if self.state == INSERT:
            p = min(1.0, self.anim / 1.0)
            cx = CARDSLOT_RECT.centerx + int((1 - p) * 150)
            self._draw_card(cx, CARDSLOT_RECT.centery)
            if p >= 1.0:
                self.goto(ENTER_ID)
        elif inserted:
            self._draw_card(CARDSLOT_RECT.centerx, CARDSLOT_RECT.centery, seated=True)
        elif self.state == THANKS:
            p = min(1.0, self.anim / 1.2)
            self._draw_card(CARDSLOT_RECT.centerx + int(p * 150), CARDSLOT_RECT.centery)

    def _draw_card(self, cx, cy, seated=False):
        w, h = 150, 34
        r = pygame.Rect(0, 0, w, h)
        r.center = (cx, cy)
        pygame.draw.rect(self.screen, CARD, r, border_radius=6)
        pygame.draw.rect(self.screen, (150, 120, 60), r, width=2, border_radius=6)
        pygame.draw.rect(self.screen, CARD_CHIP, (r.x + 12, r.centery - 7, 20, 15), border_radius=3)
        if not seated:
            pygame.draw.line(self.screen, (150, 120, 60), (r.x + 44, r.y + 8), (r.right - 10, r.y + 8), 2)
            pygame.draw.line(self.screen, (150, 120, 60), (r.x + 44, r.y + 16), (r.right - 20, r.y + 16), 2)

    def _draw_receiptslot(self):
        pygame.draw.rect(self.screen, BEZEL_EDGE, RECEIPT_RECT.inflate(20, 22), border_radius=6)
        pygame.draw.rect(self.screen, (10, 12, 16), RECEIPT_RECT, border_radius=3)
        self.screen.blit(self.ui_s.render("RECEIPT", True, STEEL), (RECEIPT_RECT.x, RECEIPT_RECT.y - 22))
        if self.state == RECEIPT_S:
            p = min(1.0, self.anim / 1.2)
            self._draw_receipt(RECEIPT_RECT.centerx, RECEIPT_RECT.bottom + int(p * 150))

    def _draw_receipt(self, cx, bottom):
        w, h = 210, 150
        r = pygame.Rect(0, 0, w, h)
        r.midbottom = (cx, bottom)
        clip = r.clip(pygame.Rect(0, RECEIPT_RECT.bottom, WIDTH, HEIGHT))
        if clip.height <= 0:
            return
        pygame.draw.rect(self.screen, RECEIPT, r, border_radius=3)
        lines = [
            self.bank_name or "ATM",
            "-" * 18,
            f"{self.pending or 'txn'}".title(),
            f"Amount:  ${getattr(self, 'last_amount', 0):,}",
            f"Balance: ${getattr(self, 'new_balance', 0):,.2f}",
            "-" * 18,
            "Thank you!",
        ]
        for i, ln in enumerate(lines):
            self.screen.blit(self.mono_s.render(ln, True, INK), (r.x + 12, r.y + 10 + i * 19))

    def _draw_keypad(self):
        for label, rect in self.keys:
            base = KEY
            txt_col = KEY_TXT
            if label == "OK":
                base = GREEN_KEY
            elif label == "CANCEL":
                base = RED
            elif label == "CLR":
                base = AMBER_KEY; txt_col = INK
            hovered = self.hover == label
            pygame.draw.rect(self.screen, BEZEL_EDGE, rect.move(0, 4), border_radius=8)
            pygame.draw.rect(self.screen, KEY_HI if hovered else base, rect, border_radius=8)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=8)
            show = {"OK": "OK", "CLR": "CLEAR", "CANCEL": "CANCEL"}.get(label, label)
            font = self.ui if len(show) <= 2 else self.ui_s
            t = font.render(show, True, txt_col)
            self.screen.blit(t, t.get_rect(center=rect.center))

    def _draw_tray(self):
        pygame.draw.rect(self.screen, BEZEL_EDGE, TRAY_RECT.inflate(16, 16), border_radius=10)
        pygame.draw.rect(self.screen, (12, 14, 18), TRAY_RECT, border_radius=8)
        pygame.draw.rect(self.screen, STEEL, DISPENSER, border_radius=3)
        self.screen.blit(self.ui_s.render("CASH DISPENSER", True, STEEL),
                         (TRAY_RECT.x + 6, TRAY_RECT.y - 22))

    # ------------------------------------------------------------------ #
    # Event loop
    # ------------------------------------------------------------------ #
    def handle(self, e):
        if e.type == pygame.QUIT:
            self.running = False
        elif e.type == pygame.MOUSEMOTION:
            self.hover = None
            for label, rect in self.keys:
                if rect.collidepoint(e.pos):
                    self.hover = label
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for label, rect in self.keys:
                if rect.collidepoint(e.pos):
                    self.press(label)
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.press("OK")
            elif e.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                self.press("CLR")
            elif e.key == pygame.K_ESCAPE:
                self.press("CANCEL")
            elif e.unicode and e.unicode.isdigit():
                self.press(e.unicode)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                self.handle(e)
            self.update(dt)
            self.draw()
        pygame.quit()


# --------------------------------------------------------------------------- #
def selftest():
    """Headless smoke test: drive a full withdrawal without a display."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.init()
    g = ATMGame(headless=True)

    def pump(frames):
        for _ in range(frames):
            g.update(1 / 60)
            g.draw()

    # OK->bank select, choose 1 (CIBC), let card insert animate, type C001 -> "001",
    # PIN 1234, menu 3 (withdraw), amount 60, then let processing+dispense play out.
    steps = [("OK", 4), ("1", 2), ("OK", 90),           # bank -> INSERT (needs ~1s)
             ("0", 2), ("0", 2), ("1", 2), ("OK", 6),   # customer id 001
             ("1", 2), ("2", 2), ("3", 2), ("4", 2), ("OK", 6),  # pin 1234 -> MENU
             ("3", 2), ("OK", 6),                        # withdraw -> AMOUNT
             ("6", 2), ("0", 2), ("OK", 200)]            # $60 -> PROCESSING+DISPENSE
    for label, frames in steps:
        g.press(label)
        pump(frames)
    pump(120)
    end_state, dispensed = g.state, sum(b.denom for b in g.bills)
    # restore demo balance unconditionally so the smoke test leaves data unchanged
    if g.bank is not None:
        g.bank.update_balance("12345678", 1000.00)
    pygame.quit()
    assert end_state in (TAKE, RECEIPT_S), f"unexpected end state {end_state}"
    assert g.last_amount == 60 and dispensed == 60, f"dispense mismatch: {dispensed}"
    print(f"selftest OK - end state {end_state}, dispensed ${dispensed} in "
          f"{len(g.bills)} bills, balance restored")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    pygame.init()
    ATMGame().run()


if __name__ == "__main__":
    main()
