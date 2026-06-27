"""
Jamming detector — energy detection + spectral analysis on the received V2X signal.

It learns the normal received power and spectrum from clean frames, then flags a frame as
jammed when its power spikes, and CLASSIFIES the jammer from the spectrum shape:
- a sharp spectral peak (high peak-to-median)      -> TONE / narrowband
- a raised but flat noise floor (high flatness)    -> BARRAGE / wideband
- spread energy that isn't a single peak nor flat  -> SWEEP / other

Spectral flatness = geometric-mean / arithmetic-mean of the PSD (1.0 = perfectly flat noise,
~0 = a single tone).
"""
import numpy as np


class JammingDetector:
    def __init__(self, power_k=4.0, peak_thresh=15.0, flat_thresh=0.45):
        self.power_k = power_k          # std-multiples above clean power -> jamming
        self.peak_thresh = peak_thresh  # peak/median PSD for a narrowband tone
        self.flat_thresh = flat_thresh  # spectral flatness for wideband barrage
        self.p0 = self.pstd = None

    def train(self, clean_frames):
        powers = np.array([np.mean(np.abs(f) ** 2) for f in clean_frames])
        self.p0 = float(powers.mean())
        self.pstd = float(powers.std() + 1e-9)
        return self

    def analyze(self, signal):
        power = float(np.mean(np.abs(signal) ** 2))
        psd = np.abs(np.fft.fft(signal)) ** 2
        psd = psd / (psd.mean() + 1e-12)
        peak_to_med = float(psd.max() / (np.median(psd) + 1e-12))
        flatness = float(np.exp(np.mean(np.log(psd + 1e-12))) / (psd.mean() + 1e-12))

        # occupied bandwidth: fraction of bins above ~2x the average (psd is mean-normalized)
        elevated = float(np.mean(psd > 2.0))

        jam = power > self.p0 + self.power_k * self.pstd
        kind = "none"
        if jam:
            if flatness > self.flat_thresh or elevated > 0.5:
                kind = "barrage/wideband"     # energy spread across the whole band
            elif elevated < 0.04:
                kind = "tone/narrowband"      # a single dominant bin
            else:
                kind = "sweep/other"          # a contiguous band of bins (chirp)
        snr_drop = 10 * np.log10(power / self.p0) if self.p0 else 0.0
        return {"jammed": jam, "kind": kind, "power": round(power, 3),
                "peak_to_median": round(peak_to_med, 1), "flatness": round(flatness, 3),
                "occupied_bw": round(elevated, 3), "power_rise_db": round(snr_drop, 1)}
