# GPA Notebook

A Python desktop GPA calculator with semester tabs, credit weighting, Honors/AP/IB bonuses, and automatic local saving.

[Download the Mac app](https://gpa-notebook-download-lv.lxkshxn30.chatgpt.site)

## Run the desktop app

Python 3 with Tkinter is required when running from source. No third-party runtime packages are needed.

```sh
python3 desktop.py
```

The downloadable Apple silicon Mac build bundles Python. It is a beta release, not Developer-ID signed or Apple-notarized. Calculation tests pass; the packaged interface has not been visually verified.

## Features

- Add and remove courses and semesters.
- Calculate weighted, unweighted, and cumulative GPA using course credits.
- Regular +0, Honors +0.5, AP/IB +1.0 when weighting is enabled.
- A+ and A start at 4.0. F earns zero, including advanced courses.
- P, W, I and blank grades are excluded.
- Desktop coursework saves in `~/Library/Application Support/GPA Notebook/courses.json`.

School grading policies may differ. Browser and desktop coursework are stored separately.

## Optional browser version

```sh
python3 app.py
```

Open http://127.0.0.1:8000. The server runs only on your computer.

## Tests

```sh
python3 -m unittest -v
```

## Build a Mac app

On an Apple silicon Mac with Python and Tkinter:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-build.txt
python -m PyInstaller --noconfirm --windowed --onedir --name "GPA Notebook" --target-arch arm64 desktop.py
```

The app is created in `dist/GPA Notebook.app`. Distribution without macOS warnings requires appropriate Apple signing and notarization, which are not configured here.

## Files

- `desktop.py`: Tkinter desktop interface.
- `app.py`: GPA calculations and optional local HTTP server.
- `test_app.py`: calculation tests.
- `static/`: browser interface.
- `site/index.html`: public download page source.

No coursework, credentials, virtual environments, or local hosting identifiers are included in this repository.
