# anechoic_chamber

Python control software for the anechoic chamber of the **Cosmology Lab**, Department of Physics "Giuseppe Occhialini", University of Milano-Bicocca.

The code drives a **Keysight N5245B PNA-X** vector network analyzer (used with VDI / OML frequency-extender heads) and an **OWIS PS90+** motor controller, to run automated scans: the motors move the antenna/device under test through a grid of positions and a VNA sweep is saved at each one.

## Repository structure

| File | Description |
|---|---|
| `anechoic_chamber.py` | `AnechoicChamber` class: high-level interface that combines VNA and motors to run scans and write the log file |
| `vna.py` | `VNA` class: SCPI commands over TCP socket (frequency range, IF bandwidth, averaging, sweeps, display, file saving on the VNA drive) |
| `controller.py` | `Controller` class: connects to the PS90+, auto-detects the motors on axes 1–9, moves them together |
| `motor.py` | `Motor` class: single-axis control (position, mode, velocity, microsteps, limit/reference switches) and model-specific subclasses |
| `read_full_scan.py` | Reads all the CSV files of a scan into a single `pandas` DataFrame |
| `anechoic_movements_old/` | Legacy scripts and notebooks, kept for reference only (not maintained) |

## Requirements

- Python 3
- `numpy`, `pandas`
- The control PC must be on the same network as the instruments. Default addresses (change them in the class constructors if needed):

| Instrument | IP address | Port |
|---|---|---|
| VNA (N5245B) | `169.254.217.24` | `5024` |
| Motor controller (PS90+) | `169.254.217.26` | `8777` |

## Supported motors

Motors are recognised automatically from their OWIS ID code, which sets the step → mm/° conversion and a safe maximum velocity.

| Model | Description | Unit |
|---|---|---|
| LTM80P-300 | 295 mm linear actuator | mm |
| LIMES 170-1000 | 1000 mm linear actuator | mm |
| HVM100N-30 | Elevation stage | mm |
| CROSS-100 | XY wide stage | mm |
| C-CROSS-105 | XY compact stage | mm |
| DMT200N-D90 | Z-axis rotator | ° |
| DMT100-D43 | X-axis rotator | ° |

> The two axes of an XY stage report the same ID, so x and y must be checked manually.

## Quick start

```python
from anechoic_chamber import AnechoicChamber

# VNA: 75–110 GHz, 1 GHz resolution, 100 Hz IF bandwidth, point averaging over 5
ac = AnechoicChamber(start_freq=75, stop_freq=110, freq_resolution=1,
                     IF_bandwidth=100, average_mode='point', average_count=5)

# One argument per connected motor, in axis order:
#   [start, stop, step] -> range (stop included)
#   scalar              -> fixed position
pos = ac.generate_positions([-1, 1, 1], 0, 0, 0, 0)

# Run the scan: path inside D:/_ANECHOIC_CHAMBER_/ on the VNA, and measurement name
ac.scan("test", "log_test", pos)
```

**Parameters**

- `start_freq`, `stop_freq`, `freq_resolution`: GHz
- `IF_bandwidth`: Hz
- `average_mode`: `'OFF'`, `'point'` or `'sweep'` (`average_count` required unless `'OFF'`)
- Positions: mm or °, absolute with respect to the encoder zero

On initialisation the VNA is set up with four windows (S11, S12, S21, S22) and all motors are switched to absolute mode. At the end of a scan the motors go back to zero and the VNA returns to continuous sweep.

## Output

All data are saved **on the VNA drive**:

```
D:/_ANECHOIC_CHAMBER_/<path>/<YYYY_MM_DD>_<measure_name>_<NNN>/
├── log_scan.txt
├── <measure_name>_ax1_<pos>_ax2_<pos>_..._.csv
└── ...
```

- `NNN` is a counter that is increased automatically if a scan with the same name and date already exists.
- Each CSV contains one sweep (displayed traces, in dB); the motor positions are encoded in the file name.
- `log_scan.txt` contains date, start/end time, VNA settings, the list of motors, and one line per sweep with the file name and the positions read from the encoders. The "SCAN COMPLETED SUCCESFULLY" footer is written only if the scan ends without errors.

## Reading the data

```python
from read_full_scan import build_df, sort_by_param

df = build_df("path/to/scan_folder")
df = sort_by_param(df, ["mot1", "Freq(GHz)"])
```

`build_df` returns one DataFrame with the frequency in GHz, the S-parameter columns, and one `mot<n>` column per axis. Truncated or corrupted files (e.g. from an interrupted scan) are skipped with a warning.

## Contact

For questions about the code or the chamber setup, contact Noemi Mezzanzanica (noemi.mezzanzanica@unimib.it).
