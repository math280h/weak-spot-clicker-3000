import logging
import time
from typing import List, Tuple

import cv2
import keyboard
from numpy import ndarray
import pyautogui


#
# Utility
#


def screenshot(*, location: str) -> None:
    """Takes a screenshot and saves it to the specified location."""
    autogui_screenshot = pyautogui.screenshot()
    autogui_screenshot.save(location)
    logging.debug(f"Screenshot saved in: {location}")


def check_failsafe(*, failsafe: str) -> None:
    """Checks if the failsafe button is currently pressed and exists if true."""
    if keyboard.is_pressed(failsafe):
        logging.critical(f"Detected keypress: {failsafe} - Shutting down.")
        exit(2)


#
# Image operations
#


def generate_mask(*, screenshot_location: str) -> ndarray:
    """Generate mask for weak spot."""
    img = cv2.imread(screenshot_location)

    logging.debug("Creating mask")
    mask_light = cv2.inRange(img, (243, 243, 243), (243, 243, 243))
    mask_dark = cv2.inRange(img, (114, 114, 114), (114, 114, 114))

    mask = cv2.bitwise_or(mask_light, mask_dark)

    return cv2.bitwise_and(img, img, mask=mask)


def find_contours(*, img: ndarray) -> Tuple[tuple, ndarray]:
    """Find contours on the mask of weak spots."""
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray_image, 127, 255, 0)
    return cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


def find_contour_position(*, contours: tuple) -> List[List[int]]:
    """Find the position of the contours."""
    contours_found = []

    for contour in contours:
        moments = cv2.moments(contour)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            contours_found.append([cx, cy])
            logging.debug(f"x: {cx} y: {cy}")

    return contours_found


#
# Main application
#


def abuse(
    *,
    screenshot_location: str,
    move_only: bool = True,
    failsafe: str = "q",
    timeout: int = 0,
    debug: bool = False,
) -> None:
    """Starts the application."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    misses = 0
    last_was_click = False

    while True:
        check_failsafe(failsafe=failsafe)

        if misses >= 5 and last_was_click:
            logging.critical(
                "Failed to click weak spot five times in a row, stopping application."
            )
            exit(1)

        logging.debug("Taking screenshot")
        screenshot(location=screenshot_location)

        logging.debug("Loading screenshot into cv2")
        output = generate_mask(screenshot_location=screenshot_location)

        logging.debug("Finding contours")
        contours, hierarchy = find_contours(img=output)

        logging.debug("Finding positions of contours")
        contours_found = find_contour_position(contours=contours)

        check_failsafe(failsafe=failsafe)

        if contours_found:
            logging.info("Found contours")
            if move_only:
                logging.debug("Moved to contour position")
                pyautogui.moveTo(contours_found[0][0], contours_found[0][1])
                last_was_click = False
            else:
                logging.debug("Clicked to contour position")
                pyautogui.click(x=contours_found[0][0], y=contours_found[0][1])
                last_was_click = True
        else:
            logging.warning("No weak spot found, moving cursor to avoid issues.")
            misses += 1

        logging.debug("Resetting cursor location.")
        pyautogui.moveTo(150, 150)

        logging.debug("Cleaning up contours found array")
        contours_found.clear()

        if timeout > 0:
            time.sleep(timeout)


if __name__ == "__main__":
    print(
        "Weak spot clicker 3000 started, sleeping three seconds before starting operations. Hold `Q` any time to "
        "shutdown"
    )
    time.sleep(3)

    abuse(screenshot_location=r"./Screenshot.png")
