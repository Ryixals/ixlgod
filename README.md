# IXL God

Automates answering IXL English questions by randomly guessing an option, submitting, and dismissing when wrong.

## Installation

```bash
pip install playwright mouse
playwright install chromium
```

## Configuration

Edit the constants at the top of the file:

| Constant | Default |
|:---------|:-------:|
| `LEGACY_MODE` | `False` |
| `DELAY_AFTER_OPTION` | `0.5` |
| `DELAY_AFTER_SUBMIT` | `1.0` |
| `DELAY_AFTER_GOT_IT` | `0.5` |
| `DELAY_BETWEEN_ROUNDS` | `0.25` |
| `POLL_INTERVAL` | `0.25` |
| `SETTLE_TIMEOUT` | `3.0` |
| `CLICK_TIMEOUT` | `1.5` |