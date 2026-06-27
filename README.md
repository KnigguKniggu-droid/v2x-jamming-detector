# V2X RF Jamming Detector

> **TL;DR** — Detects & classifies RF jamming on an OFDM V2X link using energy detection +
> spectral analysis. **100% detection and correct classification** of tone / barrage / sweep
> jammers, with 0 false alarms.

### Quickstart
```bash
pip install -r requirements.txt
python cli.py demo          # clean + all jammers: detection + classification
```

Detects and **classifies RF jamming** attacks on a vehicle-to-everything (**V2X**) radio link.
Builds a real **OFDM** physical layer (like 802.11p / C-V2X), passes it through an AWGN
channel, injects jammers, and flags + identifies them from the received spectrum.

The **communications layer** of an autonomous-vehicle security stack — securing the radio
the car talks to other cars and infrastructure over. Pure Python (numpy). Core ECE: DSP,
OFDM, FFT spectral analysis, energy detection.

## How it works
1. **Energy detection** — learn the normal received power from clean frames; a jammer raises
   received power above threshold.
2. **Spectral classification** — take the FFT and look at the spectrum *shape*:
   - a single dominant bin (narrow occupied bandwidth) → **tone / narrowband**
   - a raised, flat noise floor (high spectral flatness) → **barrage / wideband**
   - a contiguous band of elevated bins → **sweep** (a chirp)

Spectral flatness = geometric-mean / arithmetic-mean of the PSD; occupied bandwidth =
fraction of bins above ~2× the average.

## Jammers modeled
| Jammer | Signature | Real-world analogue |
|---|---|---|
| Tone / narrowband | one strong carrier on the band | cheapest jammer to build |
| Barrage / wideband | broadband noise flooding the channel | brute-force denial |
| Sweep | chirp swept across the band | defeats narrowband notch filters |

## Results (OFDM @ 15 dB SNR, 40 frames each)
```
CLEAN   : 0/40 false alarms
TONE    : 40/40 detected, 40/40 classified tone/narrowband
BARRAGE : 40/40 detected, 40/40 classified barrage/wideband
SWEEP   : 40/40 detected, 40/40 classified sweep/other
```

## Run it
```bash
pip install numpy
python cli.py demo            # clean + all jammers: detection + classification
python cli.py run tone        # one: tone | barrage | sweep
python tests/test_detector.py # detection-rate / false-alarm guarantees
```

## Architecture
```
v2x-jamming-detector/
├─ core/
│   ├─ channel.py   # OFDM signal (QPSK + IFFT + cyclic prefix) over an AWGN channel
│   ├─ jammers.py   # tone / barrage / sweep jammers at a chosen jammer-to-signal ratio
│   └─ detector.py  # energy detection + spectral classification
├─ cli.py
└─ tests/
```

## Honest scope & roadmap
- Clean classification at 15 dB SNR; at very low SNR or very low jammer-to-signal ratios the
  energy test weakens — that's the real detection-theory trade-off (P_detect vs P_false-alarm).
- **Next:** ROC curves across SNR/JSR, and add demodulation to report bit-error-rate impact.
- **Hardware path:** feed real IQ samples from a software-defined radio (RTL-SDR ~$30, or a
  HackRF) into the same detector — only the sample source changes.
