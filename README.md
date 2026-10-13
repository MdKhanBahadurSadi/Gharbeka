# GharBeka

> **"We Rotate Problems. You Pay to Unrotate Them."**

**GharBeka** is a humorous desktop subscription-software parody for Windows 10/11. The application parodies predatory SaaS subscription tiers by charging users fictional subscriptions to "unrotate" a sideways screen.

---

## Phase 1: Foundation & UI (Current Phase)

Phase 1 establishes the desktop foundation, styling architecture, and interactive simulation dashboard:

- **Simulation Mode**: Strictly software-mocked; does **not** alter actual Windows display settings or registry keys.
- **Custom Monitor Illustration**: Locally rendered vector monitor with real-time simulated orientation feedback.
- **Modern SaaS Dark Aesthetic**: Dark charcoal surfaces, purple (`#8b5cf6`) and electric-blue (`#38bdf8`) accents, rounded cards, and responsive layouts.
- **Satirical Subscription Tiers**:
  - **Free Tier** (`৳0/forever free`): Manual neck tilting and community prayers.
  - **Premium Tier** (`৳499/month`): 1-click unrotate simulation and anti-dizziness algorithm.
  - **Enterprise Tier** (`৳4,999/month`): 24/7 dedicated neck chiropractor SLA and bespoke angle insurance.
- **Payment Processing**: Fully disabled (satirical feedback only).

---

## Project Structure

```
GharBeka/
├── main.py              # Application entry point
├── requirements.txt     # Dependency definitions (PySide6, pytest)
├── README.md            # Project documentation and setup guide
├── src/
│   ├── __init__.py      # Package metadata
│   ├── main_window.py   # Main window layout, monitor widget, interaction handlers
│   └── styles.py        # Color palette constants and Qt Style Sheets (QSS)
└── tests/
    └── test_app.py      # Automated pytest suite for UI, simulation, and resizing
```

---

## Installation & Requirements

### Prerequisites
- Windows 10 or Windows 11
- Python 3.10+ (tested on Python 3.13.2)

### Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Running the Application

To launch the desktop interface:

```powershell
python main.py
```

---

## Running Automated Tests

Run the test suite using `pytest`:

```powershell
pytest -v
```

All tests execute in headless/offscreen mode without requiring user interaction.
