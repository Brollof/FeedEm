import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_fullpath(filename: str) -> str:
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, filename)


def save_count(filepath: str, cnt: int) -> None:
    with open(filepath, "w") as file:
        print(cnt)
        file.write(str(cnt))


URL = "https://nakarmpsa.olx.pl/"
TIMEOUT_S = 10
FEED_PERIOD_S = (5, 10)


logger = logging.getLogger("feed")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(get_fullpath("feeding.log"))
formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

count_file = get_fullpath("count.log")
count = 0

if os.path.exists(count_file):
    with open(count_file, "r") as file:
        count = int(file.read().strip())


while True:
    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    pets = driver.find_elements(By.CLASS_NAME, "single-pet")
    pets.sort(key=lambda p: p.get_attribute("data-pet-votes"), reverse=True)

    pet_idx = random.randint(0, 4)
    pet_to_feed = pets[pet_idx]
    pet_name = pet_to_feed.get_attribute("data-pet-name")
    pet_votes = pet_to_feed.get_attribute("data-pet-votes")
    pet_type = pet_to_feed.get_attribute("data-pet-type")
    pet_id = pet_to_feed.get_attribute("id")

    logger.info("Waiting...")
    start = time.perf_counter()
    try:
        button = WebDriverWait(driver, TIMEOUT_S).until(EC.element_to_be_clickable((By.CLASS_NAME, "single-pet-control-feed")))
    except Exception as e:
        logger.error(f"Timeout exception: {e}")
        continue

    end = time.perf_counter()
    logger.info(f"Waited {end - start} s")

    logger.info(f"Feeding {pet_name} ({pet_type}) with {float(pet_votes):.2f} %")
    button.click()
    logger.info("Done!")

    count += 1
    save_count(count_file, count)

    sleep_time = random.randint(*FEED_PERIOD_S)
    logger.info(f"Sleeping {sleep_time} seconds...")
    time.sleep(sleep_time)
    driver.close()
