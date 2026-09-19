# The Real-Life ATM

A bank ATM built in Python — an object-oriented banking backend with **two front
ends** on top of it: the original terminal program, and a graphical **arcade ATM
game** you can actually operate (card slot, keypad, phosphor-green screen, an
animated cash dispenser and a receipt printer).

The whole point of the design is that the **banking logic is the backend** and the
interface is just the machine wrapped around it. The exact same `Bank` / `Account`
/ `Customer` code powers the plain CLI *and* the game.

```
                     ┌─────────────────────────┐
  atm.py (terminal)  │                         │
                     ├──▶  atm_service.py  ──▶  Bank ─▶ Account ─▶ Customer
  atm_game.py (game) │      (clean backend       │        (your OOP logic +
                     │       API, no I/O)        │         flat-file storage)
                     └─────────────────────────┘
```

---

## Run it

```bash
pip install -r requirements.txt      # installs pygame-ce (game only)

python atm_game.py                   # the graphical ATM game
python atm.py                        # the simple terminal version
python atm_game.py --selftest        # headless self-test (drives a full withdrawal, no window)
```

Requires Python 3.12+ (developed on 3.14).

## Controls (game)

- **Click** the on-screen keypad, or use your keyboard **number keys**
- **Enter** = OK · **Backspace** = CLEAR · **Esc** = CANCEL

## How to log in

Each bank's card number is a letter + three digits, but the keypad is numeric — the
machine already knows the bank, so you just type the **three digits** and enter your
PIN.

| Bank | Type digits | PIN | Name | Balance |
|------|-------------|-----|------|---------|
| CIBC | `001` | `1234` | John Smith | $1,000 |
| CIBC | `002` | `2345` | Sarah Johnson | $2,500 |
| RBC  | `001` | `4567` | David Wilson | $1,500 |
| BMO  | `001` | `7890` | Robert Taylor | $2,000 |

(Full lists live in `banks/*.txt`.)

## Features

- **Three banks on one ATM network** — CIBC, RBC, Bank of Montreal, each with its own
  customers, colours and transaction log.
- **PIN security** — three attempts, then the machine **retains the card** (with an
  on-screen animation), matching the original logic.
- **Deposit & withdraw** with **real persistence** — balances are written back to the
  bank file, so they survive between sessions.
- **Animated cash dispenser** — withdrawals are broken into real bill denominations
  ($100 / $50 / $20 / $10 / $5) that drop into the tray; withdrawals are enforced in
  multiples of $5.
- **Receipt printer** — a receipt slides out after each transaction.
- **Transaction logging** — every deposit/withdrawal is appended to
  `transactions/<bank>_transactions.txt` with a timestamp, amount and new balance.

## Project layout

| File | Role |
|------|------|
| `customer.py` | `Customer` — identity and PIN check |
| `account.py` | `Account` — balance, deposit/withdraw, transaction logging |
| `bank.py` | `Bank` — loads customers from file, persists balances |
| `atm_service.py` | clean backend API used by every interface (no printing/input) |
| `atm.py` | the original terminal ATM, now on the clean backend |
| `atm_game.py` | the graphical Pygame ATM game |
| `banks/*.txt` | customer records: `ID\|Name\|PIN\|Account\|Balance` |
| `transactions/*.txt` | per-bank transaction logs |

## Credits

- **Banking backend & original ATM** — Spencer Rawlson Spady. The object-oriented
  design (`Bank`, `Account`, `Customer`), the flat-file data model and the original
  terminal flow are his.
- **Game interface** — the graphical Pygame ATM (`atm_game.py`) was designed and built
  by **Claude (Anthropic)**, along with a supporting refactor: extracting the clean
  `atm_service.py` backend, adding balance persistence, and fixing the transaction-log
  formatting so real values are written.

## Roadmap

- **Web version (spencerlab.tech)** — wrap `atm_service` in a small API (FastAPI) and
  build a browser ATM, to publish alongside the rest of the lab.

---

*A learning project. PINs are stored in plain text in the demo data files — fine for a
simulation, not how a real ATM stores credentials.*
