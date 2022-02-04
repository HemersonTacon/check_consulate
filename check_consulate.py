import requests
from datetime import datetime
from time import sleep
import sys
import os
import argparse
from typing import Dict


def beep(interval: float = .5, repetitions: int = 3) -> None:
    """
    Emits a default beep sound of the OS.

    To make it more audible, a number of repetitions can be defined.

    :param interval: interval in seconds between consecutive beeps.
    :param repetitions: number of the beep repetitions.
    :return:
    """
    sys.stdout.flush()
    for _ in range(repetitions):
        sys.stdout.write('\a')
        sys.stdout.flush()
        sleep(interval)


def intermittent_beep(rings: int = 10, interval: int = 15) -> None:
    """
    Emits a beep sound `rings` times apart from `interval` seconds.

    :param rings: the number of times the sound is emitted.
    :param interval: the interval in seconds between consecutive beeps
    :return:
    """

    for _ in range(rings):
        beep(interval=.1, repetitions=10)
        sleep(interval)


def get_cookies() -> Dict[str, str]:
    """
    Retrieve a the cookies from the file `cookie.txt` that must exist in the current working directory.
    :return:
    """
    with open("cookie.txt", mode="r") as f:
        return {"cookie": f.read()}


def check_consulate_for_scheduling(url: str) -> None:
    """
    Given an consulate URL, checks if the there are slots for the service.

    Different sound alerts might be triggered according to the response being the most
    insistent one when there are slots available.

    :param url: consulate URL containing the process id
    :return:
    """

    try:
        print(f"{datetime.now()} Requesting...", end=' ')
        cookies = get_cookies()
        r = requests.get(url, cookies=cookies)
        if r.ok:
            if "Escolha um dia e horário para o atendimento presencial." in r.text:
                if "Não há horários disponíveis no momento. Tente novamente mais tarde!" in r.text:
                    print("No slots available.")

                else:
                    print("Looks like there are spots available!")
                    intermittent_beep()
            else:
                print("Unexpected content on response. Update cookie and try again.")
                beep(interval=.3, repetitions=3)
        else:
            print(f"Request returned status {r.status_code}")
            beep(interval=.3, repetitions=5)
    except Exception as e:
        print("Check internet connection!")
        print(e)
        beep(interval=.3, repetitions=7)


def parse_arguments() -> argparse.Namespace:
    """
    Parse arguments (duh!).
    :return: parsed arguments (...duh)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('interval', type=int,
                        help='Time in minutes between consecutive checks')
    parser.add_argument("-id", "--process_id",
                        help='The process id. It appears on the URL when you select your consulate service.')
    return parser.parse_args()


def get_url(process_id: str) -> str:
    """
    Return formatted URL with given `process_id`.

    :param process_id: id of the process in the consulate system.
    :return:
    """
    return f"https://ec-lisboa.itamaraty.gov.br/process?id={process_id}"


if __name__ == '__main__':

    args = parse_arguments()
    default_id = "your_id_goes_here"
    PROCESS_ID = args.process_id or os.getenv("PROCESS_ID",  default_id)
    url = get_url(PROCESS_ID)
    while True:
        check_consulate_for_scheduling(url)
        sleep(args.interval * 60)
