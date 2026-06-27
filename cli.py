#!/usr/bin/env python3
"""
v2x-jamming-detector — detect & classify RF jamming on a V2X (OFDM) radio link.

    python cli.py demo            # clean + all jammer types, detection + classification
    python cli.py run tone        # one: tone | barrage | sweep
"""
import argparse

import numpy as np

from core import channel, jammers
from core.detector import JammingDetector

JAMMERS = {"tone": jammers.tone, "barrage": jammers.barrage, "sweep": jammers.sweep}


def run(jammer=None, snr_db=15.0, n=40):
    det = JammingDetector().train(channel.frames(40, snr_db=snr_db, seed=100))
    test = channel.frames(n, snr_db=snr_db, seed=500)
    if jammer:
        test = [JAMMERS[jammer](f) for f in test]
    results = [det.analyze(f) for f in test]
    jammed = sum(r["jammed"] for r in results)
    kinds = {}
    for r in results:
        if r["jammed"]:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1

    print(f"\n=== {jammer.upper() if jammer else 'CLEAN'} ===")
    if jammer:
        print(f"  detection rate : {jammed}/{n} ({jammed/n*100:.0f}%)")
        print(f"  classified as  : {kinds}")
        print(f"  avg power rise : {np.mean([r['power_rise_db'] for r in results]):.1f} dB")
    else:
        print(f"  false alarms   : {jammed}/{n}   (want 0)")
    return jammed


def main():
    p = argparse.ArgumentParser(description="V2X RF jamming detector")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("demo")
    r = sub.add_parser("run")
    r.add_argument("jammer", choices=list(JAMMERS))
    args = p.parse_args()
    if args.cmd == "run":
        run(args.jammer)
    else:
        print("V2X jamming detection — energy + spectral analysis on an OFDM link")
        run(None)
        for j in JAMMERS:
            run(j)
        print("\nClean frames sit at the learned power; jammers raise received power and reshape "
              "the spectrum, which the detector flags and classifies (tone / barrage / sweep).")


if __name__ == "__main__":
    main()
