"""
A small OFDM physical layer + AWGN channel — the kind of waveform 802.11p / C-V2X use for
vehicle-to-everything (V2X) radio. We build real OFDM symbols (QPSK on subcarriers, IFFT,
cyclic prefix), then pass them through additive white Gaussian noise at a chosen SNR.
"""
import numpy as np

N_SUB = 64   # subcarriers (FFT size)
CP = 16      # cyclic prefix length


def ofdm_signal(n_symbols=20, seed=0):
    """Generate a baseband OFDM signal: random QPSK per subcarrier, IFFT, + cyclic prefix."""
    rng = np.random.default_rng(seed)
    chunks = []
    for _ in range(n_symbols):
        bits = rng.integers(0, 2, (N_SUB, 2))
        syms = ((2 * bits[:, 0] - 1) + 1j * (2 * bits[:, 1] - 1)) / np.sqrt(2)  # QPSK
        time = np.fft.ifft(syms) * np.sqrt(N_SUB)
        chunks.append(np.concatenate([time[-CP:], time]))   # prepend cyclic prefix
    return np.concatenate(chunks)


def awgn(signal, snr_db, seed=1):
    rng = np.random.default_rng(seed)
    p_sig = np.mean(np.abs(signal) ** 2)
    p_noise = p_sig / (10 ** (snr_db / 10))
    noise = np.sqrt(p_noise / 2) * (rng.standard_normal(len(signal)) +
                                    1j * rng.standard_normal(len(signal)))
    return signal + noise


def frames(n_frames, syms_per_frame=4, snr_db=15.0, seed=0):
    """A list of received OFDM frames over an AWGN channel (no jamming)."""
    out = []
    for i in range(n_frames):
        s = ofdm_signal(syms_per_frame, seed=seed + i)
        out.append(awgn(s, snr_db, seed=1000 + seed + i))
    return out
