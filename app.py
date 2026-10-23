import random
import sys
import time

import mouse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OPTION_SELECTOR = ".MULTIPLE_CHOICE:not(.nonInteractive)"
BUTTON_SELECTOR = ".crisp-button"
START_URL = "https://www.ixl.com/"

LEGACY_MODE = False

DELAY_AFTER_OPTION = 0.5
DELAY_AFTER_SUBMIT = 1.0
DELAY_AFTER_GOT_IT = 0.5
DELAY_BETWEEN_ROUNDS = 0.25
POLL_INTERVAL = 0.25

SETTLE_TIMEOUT = 3.0
CLICK_TIMEOUT = 1.5


def log(msg: str) -> None:
    print(f"[IXL God] {msg}", flush=True)


def os_click(x: float, y: float) -> None:
    mouse.move(x, y, absolute=True, duration=0.08)
    time.sleep(0.05)
    mouse.click()


def wait_for_settle(page, timeout_s: float = SETTLE_TIMEOUT) -> None:
    try:
        page.wait_for_function(
            """() => {
                const imgs = [...document.images];
                const imgsReady = imgs.every(
                    img => img.complete || !img.getAttribute('src')
                );

                const w = window;
                if (!w.__ixlGodSettle) w.__ixlGodSettle = { h: -1, stable: 0 };
                const s = w.__ixlGodSettle;
                const h = document.documentElement.scrollHeight;
                if (h === s.h) s.stable++;
                else { s.h = h; s.stable = 0; }

                return imgsReady && s.stable >= 2;
            }""",
            timeout=timeout_s * 1000,
        )
    except PWTimeout:
        pass


def find_button(page, text: str, data_cy: str | None = None):
    handle = page.evaluate_handle(
        """([text, dataCy]) => {
            const buttons = document.querySelectorAll('.crisp-button');
            for (const b of buttons) {
                if ((b.textContent || '').trim() !== text) continue;
                if (dataCy && b.getAttribute('data-cy') !== dataCy) continue;
                return b;
            }
            return null;
        }""",
        [text, data_cy],
    )
    return handle.as_element()


def find_option(page):
    handle = page.evaluate_handle(
        """(sel) => {
            const opts = document.querySelectorAll(sel);
            if (!opts.length) return null;
            return opts[Math.floor(Math.random() * opts.length)];
        }""",
        OPTION_SELECTOR,
    )
    return handle.as_element()


def playwright_click(element) -> bool:
    if element is None:
        return False

    try:
        element.scroll_into_view_if_needed(timeout=2000)
    except PWTimeout:
        pass

    try:
        box = element.bounding_box()
    except Exception:
        box = None

    if box and box["width"] > 4 and box["height"] > 4:
        pos = {
            "x": box["width"] * random.uniform(0.35, 0.65),
            "y": box["height"] * random.uniform(0.35, 0.65),
        }
        try:
            element.click(position=pos, timeout=CLICK_TIMEOUT * 1000)
            return True
        except Exception as e:
            log(f"Jittered click failed ({type(e).__name__}); retrying center")

    try:
        element.click(timeout=CLICK_TIMEOUT * 1000)
        return True
    except Exception as e:
        log(f"Click failed ({type(e).__name__}: {e})")
        return False


def os_click_element(page, element) -> bool:
    if element is None:
        return False

    try:
        element.scroll_into_view_if_needed(timeout=2000)
    except PWTimeout:
        pass

    try:
        box = element.bounding_box()
    except Exception:
        box = None
    if not box:
        return False

    x = box["x"] + box["width"] / 2 + random.uniform(-2, 2)
    y = box["y"] + box["height"] / 2 + random.uniform(-2, 2)

    win = page.evaluate(
        """() => ({
            screenX: window.screenX,
            screenY: window.screenY,
            outerHeight: window.outerHeight,
            innerHeight: window.innerHeight,
            outerWidth: window.outerWidth,
            innerWidth: window.innerWidth,
        })"""
    )
    chrome_h = win["outerHeight"] - win["innerHeight"]
    chrome_w = win["outerWidth"] - win["innerWidth"]
    abs_x = win["screenX"] + chrome_w / 2 + x
    abs_y = win["screenY"] + chrome_h + y

    os_click(abs_x, abs_y)
    return True


def browser_click(page, element) -> bool:
    if LEGACY_MODE:
        return os_click_element(page, element)
    return playwright_click(element)


def run(page) -> None:
    log("Loop started. Ctrl+C to stop.")
    try:
        while True:
            wait_for_settle(page)

            option = find_option(page)
            if option is None:
                log("No option found — waiting…")
                time.sleep(POLL_INTERVAL)
                continue

            log("Picked option")
            if not browser_click(page, option):
                log("Option click failed — waiting…")
                time.sleep(POLL_INTERVAL)
                continue
            time.sleep(DELAY_AFTER_OPTION)

            wait_for_settle(page)

            submit = find_button(page, "Submit", data_cy="question-submit-button")
            if submit is None:
                log("Submit not found — waiting…")
                time.sleep(POLL_INTERVAL)
                continue

            log("Clicking Submit")
            if not browser_click(page, submit):
                log("Submit click failed — waiting…")
                time.sleep(POLL_INTERVAL)
                continue

            time.sleep(DELAY_AFTER_SUBMIT)

            gotIt = find_button(page, "Got it")
            if gotIt is not None:
                log('Answer incorrect — clicking "Got it"')
                browser_click(page, gotIt)
                time.sleep(DELAY_AFTER_GOT_IT)

            time.sleep(DELAY_BETWEEN_ROUNDS)

    except KeyboardInterrupt:
        log("Stopped by user.")


def main() -> int:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto(START_URL, wait_until="domcontentloaded")

        print()
        print("=" * 60)
        print(" IXL GOD V1.0")
        print(" 1. Wait for the browser to load, then log into IXL")
        print(" 2. Navigate to a multiple choice English skill")
        print(" 3. Press Enter here to start the loop.")
        print(" As it is the first version, it is quite buggy")
        print("=" * 60)
        try:
            input()
        except EOFError:
            pass

        try:
            page.bring_to_front()
        except Exception:
            pass
        time.sleep(0.5)

        run(page)
        browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())