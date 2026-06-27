"""Tests: no false alarms on clean frames; every jammer type detected at high rate."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import channel, jammers
from core.detector import JammingDetector


def _detector():
    return JammingDetector().train(channel.frames(40, snr_db=15.0, seed=100))


def _rate(det, frames):
    return sum(det.analyze(f)["jammed"] for f in frames) / len(frames)


def test_clean_no_false_alarms():
    det = _detector()
    clean = channel.frames(40, snr_db=15.0, seed=500)
    assert _rate(det, clean) <= 0.05


def test_tone_detected():
    det = _detector()
    test = [jammers.tone(f) for f in channel.frames(40, snr_db=15.0, seed=500)]
    assert _rate(det, test) > 0.9


def test_barrage_detected():
    det = _detector()
    test = [jammers.barrage(f) for f in channel.frames(40, snr_db=15.0, seed=500)]
    assert _rate(det, test) > 0.9


def test_sweep_detected():
    det = _detector()
    test = [jammers.sweep(f) for f in channel.frames(40, snr_db=15.0, seed=500)]
    assert _rate(det, test) > 0.9


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS ", name)
    print("All tests passed.")
