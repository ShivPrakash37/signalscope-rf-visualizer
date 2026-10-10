# SignalScope Visualizer — Final Starter Project

## 1) Run the dashboard (demo mode)
1. Install Python 3.10 or newer.
2. Open a terminal inside this folder.
3. Install the web dependency:
   `python -m pip install flask`
4. Start:
   `python app.py`
5. Open `http://127.0.0.1:5050` in your browser.

Demo mode displays simulated spectrum peaks, waterfall history, and a signal activity graph. It does **not** measure nearby real signals.

## 2) Optional real RF mode (RTL-SDR)
You need a compatible RTL-SDR USB receiver, antenna, and the operating-system's RTL-SDR driver/library.

Install Python packages:
`python -m pip install flask numpy pyrtlsdr`

Start the dashboard with SDR input:
`python app.py --sdr --center-mhz 100`

Then open `http://127.0.0.1:5050`. The default center frequency is an example only. Set frequency and sample rate to match your hardware and lawful reception requirements. Hardware/driver installation varies by OS.

If SDR setup fails, the page displays an error. The app defaults to localhost (127.0.0.1) and is not exposed to your network.

## Important limitations
- The browser cannot detect RF signals by itself.
- Real RF input requires compatible SDR hardware.
- This is a spectrum visualizer, not a universal detector.
- Peaks do not reliably identify individual devices, reveal exact location, or decode encrypted communications.
- Use only lawful, permitted reception; do not intercept private communications.

## Files
- `app.py`: local Flask server; demo source by default, optional RTL-SDR source
- `templates/index.html`: live dashboard
- `requirements.txt`: Python dependencies
