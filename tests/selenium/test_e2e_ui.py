"""Selenium E2E browser tests for TuneTrail React + Flask application."""

import socket
import threading
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

from backend.app import create_app


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    """Run Flask serving built frontend/dist on a free localhost port."""
    from database.seed import seed_database

    db_file = tmp_path_factory.mktemp("e2e_db") / "e2e_tunetrail.db"
    seed_database(db_file, force=True)

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "selenium-e2e-secret",
            "DATABASE_PATH": str(db_file),
        }
    )
    port = _find_free_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    """Launch headless Edge or Chrome WebDriver."""
    driver = None
    try:
        edge_opts = EdgeOptions()
        edge_opts.add_argument("--headless=new")
        edge_opts.add_argument("--disable-gpu")
        edge_opts.add_argument("--window-size=1280,900")
        driver = webdriver.Edge(options=edge_opts)
    except Exception:
        try:
            chrome_opts = webdriver.ChromeOptions()
            chrome_opts.add_argument("--headless=new")
            chrome_opts.add_argument("--disable-gpu")
            chrome_opts.add_argument("--window-size=1280,900")
            driver = webdriver.Chrome(options=chrome_opts)
        except Exception as exc:
            pytest.skip(f"No headless Edge/Chrome WebDriver available: {exc}")

    yield driver
    if driver is not None:
        driver.quit()


def test_e2e_login_dashboard_library_and_recommendations(live_server, browser):
    wait = WebDriverWait(browser, 10)
    browser.get(live_server)

    # 1. Click "Fill Demo Listener" and Sign In
    fill_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Fill Demo Listener')]"))
    )
    fill_btn.click()

    submit_btn = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()

    # 2. Verify Dashboard renders
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Listener Dashboard"))

    # 3. Navigate to Music Library and search
    lib_btn = browser.find_element(By.XPATH, "//nav//button[contains(., 'Music Library')]")
    lib_btn.click()
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Music Library"))

    search_input = browser.find_element(By.CSS_SELECTOR, "input[type='search']")
    search_input.send_keys("Neon")
    time.sleep(0.5)
    assert "Neon Horizon" in browser.page_source

    # 4. Play a track and verify PlayerBar appears
    play_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "article.track-card button.btn-primary"))
    )
    play_btn.click()
    player_bar = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "aside.player-bar")))
    assert "Neon Horizon" in player_bar.text

    # 5. Navigate to AI For You recommendations
    rec_btn = browser.find_element(By.XPATH, "//nav//button[contains(., 'AI For You')]")
    rec_btn.click()
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "AI Recommendation Studio"))
    cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.track-card")))
    assert len(cards) >= 5
