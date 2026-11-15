#!/usr/bin/env python3
"""Pearl Harbor FINAL — visual build2 (v3 safezone) retimed to Bos VO timing."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

TIM = json.load(open(os.path.join(B.ROOT, "vo", "timing_bos.json")))
TOTAL = TIM["total"]
B.TIM = TIM
B.EV = TIM["events"]
B.STARTS = TIM["scene_starts"] + [TOTAL]
B.TOTAL = TOTAL

import build2 as B2
B2.TOTAL = TOTAL
B2.FR = os.path.join(B.ROOT, "work", "frames4")
os.makedirs(B2.FR, exist_ok=True)

if __name__ == "__main__":
    B2.main()
