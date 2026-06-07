# ⏰ CLI Alarm Clock

A lightweight command-line alarm clock built in Python. No dependencies beyond the Python standard library — works out of the box on Windows.

---

## Why This Design?

Before writing a single line of code, I used AI to refine requirements and make deliberate scope decisions:

| Decision | Choice | Reason |
|---|---|---|
| Storage | In-memory only | 30-min scope; persistence adds complexity with little user value for a demo |
| Sound | `winsound.Beep` | Zero-install, ships with Python on Windows |
| Threading | `threading.Thread` | Simple background waiter; no async overhead needed |
| CLI parsing | `argparse` | Standard library, self-documenting `--help` |
| Features cut | snooze, recurrence, timezones | Scope discipline — ship clean core, extend later |

This reflects a real engineering principle: **define the problem before writing code**.

---

## Requirements

- Python 3.8+
- Windows (uses `winsound` — built into Python on Windows, no pip install needed)

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/cli-alarm-clock.git
cd cli-alarm-clock
```

No `pip install` required.

---

## Usage

### Set an alarm

```bash
python alarm.py set 07:30
python alarm.py set 14:00 --label "Team standup"
```

The terminal stays open and counts down. Press `Ctrl+C` to cancel.

### List active alarms

```bash
python alarm.py list
```

### Cancel an alarm

```bash
python alarm.py cancel 07:30
python alarm.py cancel --all
```

### Help

```bash
python alarm.py --help
python alarm.py set --help
```

---

## Example Session

```
$ python alarm.py set 09:15 --label "Morning coffee"
  ⏰  Alarm set for 09:15 (Morning coffee) — fires in 4m 32s

  🔔  ALARM! 09:15 — Morning coffee
  (alarm done — press Enter if the prompt is hidden)
```

---

## Project Structure

```
cli-alarm-clock/
├── alarm.py       # Single-file implementation (~150 lines)
└── README.md
```

Intentionally one file. A production version would split into `cli.py`, `alarm_manager.py`, and `sound.py` — but for a 30-minute scoped exercise, a single readable file is the right call.

---

## Engineering Decisions Log

This section documents the thinking behind the code — the part that matters more than the code itself.

### Requirements Refinement (AI-assisted)
Used AI to identify which features belong in a 30-minute MVP vs. a v2:
- **In:** set, list, cancel, beep, countdown display
- **Out:** snooze, persistence, recurrence, GUI, timezone support

### Architecture
- Single `alarms` list with a `threading.Lock` for thread safety
- Each alarm runs in a `daemon=True` thread — auto-exits when the main program exits
- Cancellation uses a `cancelled` flag (cooperative cancellation pattern) rather than forcefully killing threads

### Error Handling
- Invalid time format → clear error message, non-zero exit
- Duplicate alarm → rejected with explanation
- Past time → scheduled for the next day (common UX expectation)
- `Ctrl+C` → graceful cancellation

### Trade-offs
- **No persistence**: Alarms are lost if the terminal closes. Acceptable for scope; a v2 would use a JSON file or SQLite.
- **Single terminal**: Can't set an alarm and use the same terminal — a v2 would use a background daemon process.
- **Windows only**: `winsound` is Windows-specific. Cross-platform would use `playsound` or `pygame`.

---

## What I'd Build Next (v2)

1. **Cross-platform sound** using `playsound` library
2. **Persistence** — save/load alarms from `~/.alarms.json`
3. **Background daemon** so the terminal stays free after setting an alarm
4. **Snooze** — `python alarm.py snooze 5` (5-minute snooze)
5. **Recurring alarms** — `python alarm.py set 07:30 --repeat weekdays`

---

## Author

Built as part of a Senior Software Engineer take-home exercise.  
Focus: engineering decision-making, problem scoping, and AI-directed development.
