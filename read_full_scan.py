import io
import os
import re
import pandas as pd


_AXIS_PATTERN = re.compile(r"[Aa]x(\d+)_(-?\d+(?:\.\d+)?)")   #filename structure, w/ varying number of motors

_HEADER_ROW = 5   #row index of "Freq(Hz),..." (pandas skips blank lines when counting rows)
_FOOTER_LINES = 2   #trailing "END" line + blank line


def build_df(dirpath):
    filenames = [
        os.path.join(dirpath, filename)
        for filename in os.listdir(dirpath)
        if os.path.splitext(os.path.basename(filename))[1] == ".csv"
        and "Log" not in filename   #ignore log file
        and not filename.startswith("._")  #ignore macOS AppleDouble sidecar files
    ]
    dfs = []
    for f in filenames:
        basename = os.path.basename(f)

        with open(f, "rb") as fh:
            raw = fh.read().replace(b"\x00", b"")   #read raw bytes and strip any embedded NUL bytes before parsing

        lines = raw.decode("latin-1").splitlines()   #decoding (latin-1 never fails, e.g. on stray ° bytes)

        if len(lines) <= _HEADER_ROW + _FOOTER_LINES + 1:   #skips corrupted files, such as interrupted measurements
            print(f"Skipping {basename}: file too short ({len(lines)} lines)")
            continue

        data_text = "\n".join(lines[:-_FOOTER_LINES])   #skipping the footer lines
        try:
            df = pd.read_csv(io.StringIO(data_text), header=_HEADER_ROW)   #reading the frequency and S-parameter amplitude and phase
        except (ValueError, pd.errors.EmptyDataError) as e:   #catch any other malformed file
            print(f"Skipping {basename}: could not parse ({e})")
            continue

        df["Freq(Hz)"] /= 1e9   #converting frequency in GHz
        df = df.rename({"Freq(Hz)": "Freq(GHz)"}, axis="columns")

        stem = os.path.splitext(basename)[0]
        axis_matches = _AXIS_PATTERN.findall(stem)      #read positions of each motor
        df = df.assign(**{f"mot{n}": float(v) for n, v in axis_matches})

        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)