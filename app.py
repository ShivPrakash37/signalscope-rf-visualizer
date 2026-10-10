import argparse
import threading
import time
import math
import random
from flask import Flask, jsonify, render_template

app = Flask(__name__)
state = {"mode": "demo", "bins": [], "center_hz": 2_450_000_000, "sample_rate": 2_000_000, "error": None}
lock = threading.Lock()
stop_event = threading.Event()

def demo_loop():
    """Generates illustrative data only; it is NOT a measurement of nearby RF signals."""
    n = 512
    while not stop_event.is_set():
        bins = []
        centers = [random.randint(45, 100), random.randint(180, 250),
                   random.randint(300, 370), random.randint(400, 470)]
        amps = [random.uniform(15, 32) for _ in centers]
        for i in range(n):
            value = -92 + random.uniform(0, 5)
            for c, a in zip(centers, amps):
                value += a * math.exp(-((i-c)/random.uniform(3.5, 8.5))**2 / 2)
            bins.append(round(min(-25, value), 2))
        with lock:
            state.update(mode="demo", bins=bins, center_hz=2_450_000_000,
                         sample_rate=100_000_000, error=None)
        stop_event.wait(0.7)

def sdr_loop(center_hz, sample_rate):
    try:
        import numpy as np
        from rtlsdr import RtlSdr
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.center_freq = center_hz
        sdr.gain = "auto"
        with lock:
            state["mode"] = "RTL-SDR"
            state["error"] = None
        try:
            while not stop_event.is_set():
                samples = sdr.read_samples(256 * 1024)
                window = np.hanning(len(samples))
                spectrum = np.fft.fftshift(np.fft.fft(samples * window))
                power = 20 * np.log10(np.abs(spectrum) + 1e-12)
                # Normalize display to a relative scale while retaining changes in power.
                floor = float(np.percentile(power, 10))
                vals = np.clip(power - floor - 45, -95, -25)
                step = max(1, len(vals)//512)
                bins = [round(float(vals[i]), 2) for i in range(0, len(vals), step)][:512]
                with lock:
                    state.update(mode="RTL-SDR", bins=bins, center_hz=center_hz,
                                 sample_rate=sample_rate, error=None)
        finally:
            sdr.close()
    except Exception as e:
        with lock:
            state["mode"] = "error"
            state["error"] = str(e)
            state["bins"] = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/spectrum")
def spectrum():
    with lock:
        return jsonify(dict(state))

def main():
    parser = argparse.ArgumentParser(description="SignalScope RF spectrum visualizer")
    parser.add_argument("--sdr", action="store_true", help="Read spectrum from a compatible RTL-SDR device")
    parser.add_argument("--center-mhz", type=float, default=100.0, help="SDR center frequency in MHz (default: 100)")
    parser.add_argument("--sample-rate", type=float, default=2.4e6, help="Sample rate in samples/second")
    parser.add_argument("--host", default="127.0.0.1", help="Local-only by default")
    parser.add_argument("--port", type=int, default=5050)
    args = parser.parse_args()

    if args.sdr:
        worker = threading.Thread(target=sdr_loop, args=(int(args.center_mhz*1e6), int(args.sample_rate)), daemon=True)
    else:
        worker = threading.Thread(target=demo_loop, daemon=True)
    worker.start()
    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    finally:
        stop_event.set()

if __name__ == "__main__":
    main()
