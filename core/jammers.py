"""
RF jamming attacks against the V2X link — the real families used to deny vehicle comms:

- TONE / narrowband : a continuous-wave carrier parked on the band (cheap, easy to build).
- BARRAGE / wideband: broadband noise flooding the whole channel (brute force).
- SWEEP             : a chirp sweeping across the band (defeats narrowband notch filters).

Each adds the jammer to a received signal at a given jammer-to-signal power ratio (JSR).
"""
import numpy as np

from .channel import N_SUB


def _scale(signal, jsr):
    return np.sqrt(np.mean(np.abs(signal) ** 2) * jsr)


def tone(signal, freq_bin=20, jsr=8.0):
    n = len(signal)
    t = np.arange(n)
    f = freq_bin / N_SUB
    return signal + _scale(signal, jsr) * np.exp(1j * 2 * np.pi * f * t)


def barrage(signal, jsr=3.0, seed=7):
    rng = np.random.default_rng(seed)
    n = len(signal)
    a = _scale(signal, jsr)
    return signal + (a / np.sqrt(2)) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))


def sweep(signal, jsr=8.0, f0=0.05, f1=0.45):
    n = len(signal)
    t = np.arange(n)
    phase = 2 * np.pi * (f0 * t + (f1 - f0) / (2 * n) * t ** 2)   # linear chirp
    return signal + _scale(signal, jsr) * np.exp(1j * phase)
