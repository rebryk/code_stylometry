import json
import logging
import os
import sys
import zipfile
from urllib.request import urlopen, urlretrieve

from joblib import Parallel, delayed
from tqdm import tqdm

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    stream=sys.stdout,
    level=logging.INFO
)

URL = 'http://code.google.com/codejam/contest/scoreboard/do'
USERS_FOLDER = 'users'
TMP_FOLDER = 'tmp'
CODEJAM_FOLDER = 'codejam'


def get_code_url(round_id: int, problem_id: int, username: str) -> str:
    return f'{URL}?cmd=GetSourceCode&contest={round_id}&problem={problem_id}&io_set_id=0&username={username}'


def get_username_url(round_id: int, position: int) -> str:
    return f'{URL}?cmd=GetScoreboard&contest_id={round_id}&show_type=all&start_pos={position}' \
        f'&views_time=1&views_file=0&csrfmiddlewaretoken='


def download_user_list(round_id: int, num_players: int):
    file = f'{USERS_FOLDER}/{round_id}.txt'

    if os.path.exists(file):
        return

    with open(file, 'w') as file:
        for position in tqdm(range(1, int(num_players), 30), desc=f'Round id={round_id}'):
            meta_url = get_username_url(round_id, position)
            meta_json = json.load(urlopen(meta_url))

            for row in meta_json['rows']:
                username = row['n']
                file.write(f'{username}\n')


def download_problem(round_id: int, problem_id: int):
    user_file = f'{USERS_FOLDER}/{round_id}.txt'
    tmp_folder = f'{TMP_FOLDER}/{round_id}/{problem_id}'
    target_folder = f'{CODEJAM_FOLDER}/{round_id}/{problem_id}'

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    if not os.path.exists(user_file):
        raise RuntimeError(f'No users for round={round_id}')

    with open(user_file, 'r') as file:
        users = [it.strip() for it in file.readlines()]

    for username in tqdm(users, desc=f'Problem id={problem_id}'):
        target_zip = f'{TMP_FOLDER}/{round_id}/{problem_id}/{username}.zip'
        filename = f'{username}.java'
        target_source = f'{target_folder}/{filename}'

        # Continue if the file is already extracted
        if os.path.exists(target_source):
            continue

        if not os.path.exists(target_zip):
            code_url = get_code_url(round_id, problem_id, username)
            urlretrieve(code_url, target_zip)

        # try-except in case of a bad header
        try:
            with open(target_zip, 'rb') as zip_header:
                zip_archive = zipfile.ZipFile(zip_header)

                for file in zip_archive.namelist():
                    if not file.endswith('.java'):
                        continue

                    zip_archive.extract(file, tmp_folder)
                    os.rename(f'{tmp_folder}/{file}', target_source)
        except:
            # Can happen if the user didn't do a problem
            pass


if __name__ == '__main__':
    with open('metadata.json', 'r') as file:
        metadata = json.load(file)

    rounds = [it for year_json in metadata['competitions'] for it in year_json['round']]
    problems = [(int(r['contest']), int(p['id'])) for r in rounds for p in r['problems']]

    if not os.path.exists(USERS_FOLDER):
        os.mkdir(USERS_FOLDER)

    logging.info(f'Downloading user list...')
    with Parallel(n_jobs=16) as pool:
        pool(delayed(download_user_list)(int(it['contest']), int(it['numPlayers'])) for it in rounds)
    logging.info('Done')

    logging.info(f'Downloading code...')
    with Parallel(n_jobs=16) as pool:
        pool(delayed(download_problem)(*it) for it in problems)
    logging.info('Done')
