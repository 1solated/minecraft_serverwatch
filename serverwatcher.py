import os
import subprocess
import logging
from datetime import datetime as dt

LOG_FILE = os.environ['HOME'] + '/minecraft/logs/latest.log'
PTN_JOIN = 'logged in'
PTN_LEFT = 'left the game'

# setup log
logger = logging.getLogger('mylog')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.getcwd() + '/log.log')
logger.addHandler(handler)
fmt = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(fmt)


def stop_server():
    logger.debug('No online player. shutdown server.')
    subprocess.run('sudo shutdown -h now', shell=True)


def is_disabled_time():
    # 起動後15分間はシャットダウン対象外とする
    # systemctlコマンドの結果パターン：'水 2022-09-21 15:26:25 UTC\n'の曜日を削り、経過時間を取得
    res = subprocess.run('systemctl show --property=ActiveEnterTimestamp minecraft.service | cut -d= -f2',
                         shell=True, capture_output=True, text=True)
    time = ' '.join(res.stdout.replace('\n', '').split(' ')[1:])
    started = dt.strptime(time, '%Y-%m-%d %H:%M:%S %Z')
    time_diff = dt.now() - started
    logger.debug('uptime: ' + str(time_diff.seconds))
    if time_diff.seconds < 15 * 60:
        logger.debug('Script exit because it is within 15 minutes after startup.')
        return True
    return False


def check():
    logger.debug('check start!')
    online = 0
    if is_disabled_time():
        return
    with open(LOG_FILE) as f:
        lines = f.read().splitlines()
        for s in lines:
            if PTN_JOIN in s:
                online += 1
            if PTN_LEFT in s:
                online -= 1
        logger.debug('check end! online=' + str(online))
        if online <= 0:
            stop_server()


if __name__ == '__main__':
    check()
