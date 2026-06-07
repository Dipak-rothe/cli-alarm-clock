"""
alarm.py - A simple CLI alarm clock for Windows
Usage:
  python alarm.py set 07:30
  python alarm.py set 07:30 --label "Wake up"
  python alarm.py list
  python alarm.py cancel 07:30
  python alarm.py cancel --all
"""

import argparse
import threading
import time
import winsound
import sys
from datetime import datetime

alarms = []
alarms_lock = threading.Lock()


def parse_time(time_str):
    """Parse HH:MM string. Raises ValueError on bad format."""
    try:
        return datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise ValueError(f"Invalid time '{time_str}'. Use HH:MM (24-hour), e.g. 07:30 or 14:00.")


def seconds_until(hh_mm):
    """Return seconds from now until next occurrence of HH:MM (today or tomorrow)."""
    now = datetime.now()
    target = now.replace(
        hour=int(hh_mm[:2]),
        minute=int(hh_mm[3:]),
        second=0,
        microsecond=0,
    )
    diff = (target - now).total_seconds()
    if diff <= 0:
        diff += 86400  # schedule for tomorrow
    return diff


def beep_alert():
    """Play a short beep sequence using Windows built-in winsound."""
    for _ in range(5):
        winsound.Beep(1000, 500)   # 1000 Hz, 500 ms
        time.sleep(0.2)


def find_alarm(time_str):
    """Return the alarm dict matching time_str, or None."""
    with alarms_lock:
        for alarm in alarms:
            if alarm["time"] == time_str:
                return alarm
    return None


def run_alarm(alarm):
    """Sleep until alarm time, then fire — unless cancelled."""
    wait = seconds_until(alarm["time"])

    print(f"    Alarm set for {alarm['time']} ({alarm['label']}) — "
          f"fires in {int(wait // 60)}m {int(wait % 60)}s")

    start = time.time()
    while True:
        if alarm["cancelled"]:
            print(f"\n  ✖  Alarm {alarm['time']} ({alarm['label']}) was cancelled.")
            return
        elapsed = time.time() - start
        if elapsed >= wait:
            break
        time.sleep(1)   

    print(f"\n   ALARM! {alarm['time']} — {alarm['label']}")
    beep_alert()
    print("  (alarm done — press Enter if the prompt is hidden)\n")

def cmd_set(args):
    time_str = args.time

    try:
        parse_time(time_str)
    except ValueError as e:
        print(f"  ✖  {e}")
        sys.exit(1)
   
    h, m = time_str.split(":")
    time_str = f"{int(h):02d}:{int(m):02d}"

    if find_alarm(time_str):
        print(f"  ✖  An alarm for {time_str} already exists. Cancel it first.")
        sys.exit(1)

    label = args.label if args.label else "Alarm"

    alarm = {"time": time_str, "label": label, "cancelled": False, "thread": None}

    t = threading.Thread(target=run_alarm, args=(alarm,), daemon=True)
    alarm["thread"] = t

    with alarms_lock:
        alarms.append(alarm)

    t.start()
    try:
        t.join()
    except KeyboardInterrupt:
        alarm["cancelled"] = True
        print("\n  Interrupted. Alarm cancelled.")

def cmd_list(args):
    with alarms_lock:
        active = [a for a in alarms if not a["cancelled"]]
    if not active:
        print("  No active alarms.")
        return
    print(f"  {'TIME':<8}  LABEL")
    print(f"  {'----':<8}  -----")
    for a in active:
        print(f"  {a['time']:<8}  {a['label']}")

def cmd_cancel(args):
    if args.all:
        with alarms_lock:
            targets = [a for a in alarms if not a["cancelled"]]
        if not targets:
            print("  No active alarms to cancel.")
            return
        for a in targets:
            a["cancelled"] = True
        print(f"  ✔  Cancelled {len(targets)} alarm(s).")
        return

    if not args.time:
        print("  ✖  Provide a time (HH:MM) or use --all.")
        sys.exit(1)

    h, m = args.time.split(":") if ":" in args.time else (None, None)
    if h is None:
        print("  ✖  Invalid time format. Use HH:MM.")
        sys.exit(1)
    time_str = f"{int(h):02d}:{int(m):02d}"

    alarm = find_alarm(time_str)
    if not alarm or alarm["cancelled"]:
        print(f"  ✖  No active alarm found for {time_str}.")
        sys.exit(1)

    alarm["cancelled"] = True
    print(f"  ✔  Alarm {time_str} ({alarm['label']}) cancelled.")

def build_parser():
    parser = argparse.ArgumentParser(
        prog="alarm",
        description="🕐  CLI Alarm Clock — set, list, and cancel alarms from the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python alarm.py set 07:30
  python alarm.py set 14:00 --label "Team standup"
  python alarm.py list
  python alarm.py cancel 07:30
  python alarm.py cancel --all
        """
    )

    sub = parser.add_subparsers(dest="command", required=True)


    p_set = sub.add_parser("set", help="Set a new alarm")
    p_set.add_argument("time", metavar="HH:MM", help="Alarm time in 24-hour format")
    p_set.add_argument("--label", metavar="TEXT", help="Optional label for the alarm")
    p_set.set_defaults(func=cmd_set)

   
    p_list = sub.add_parser("list", help="List active alarms")
    p_list.set_defaults(func=cmd_list)

   
    p_cancel = sub.add_parser("cancel", help="Cancel an alarm")
    p_cancel.add_argument("time", metavar="HH:MM", nargs="?", help="Time of alarm to cancel")
    p_cancel.add_argument("--all", action="store_true", help="Cancel all alarms")
    p_cancel.set_defaults(func=cmd_cancel)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
