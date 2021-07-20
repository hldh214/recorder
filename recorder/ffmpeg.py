import datetime
import json
import random
import subprocess

TIMEOUT_US = str(20 * 1000000)  # 20s
MAX_DURATION = str(10 * 3600 - 300)
USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114',
    'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.2.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15'
)
FFMPEG_BINARY = 'ffmpeg'
FFPROBE_BINARY = 'ffprobe'


def record(input_url, output_file, args=None):
    popen_args = [
        FFMPEG_BINARY, '-y', '-user_agent', random.choice(USER_AGENTS), '-hide_banner',
        '-reconnect_streamed', '1', '-reconnect_delay_max', '20',
        '-rw_timeout', TIMEOUT_US, '-timeout', TIMEOUT_US,
        '-i', input_url, '-c', 'copy', '-t', MAX_DURATION
    ]

    if args is not None:
        popen_args.extend(args)

    popen_args.append(output_file)

    ff = subprocess.Popen(popen_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        print(line.decode(), end='')

    return ff.wait()


def show_format(input_file):
    """
    :param input_file: video's path or stream url
    :return: video's format information in json dictionary, None if video is not valid
    """
    args = [FFPROBE_BINARY]

    if str(input_file).startswith('http'):
        args.extend(['-user_agent', random.choice(USER_AGENTS)])

    args.extend(['-print_format', 'json', '-rw_timeout', TIMEOUT_US, '-show_format', '-i', input_file])

    proc = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    res = json.loads(proc.stdout)

    if not res:
        return None

    return res


def duration(input_file):
    """
    :param input_file: video's path
    :return: video's duration in seconds, False if video is not valid
    """
    res = show_format(input_file)

    return int(float(res['format']['duration'])) if res else False


def valid(input_file):
    """
    :param input_file: video's path or stream url
    :return: True if video is valid, False if not
    """
    return True if show_format(input_file) else False


def in_use(input_file):
    # todo: use psutil instead
    return bool(subprocess.run(
        ['fuser', input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ).stdout)


def split(input_file, chunk=10 * 3600 - 300):
    current_duration = duration(input_file)

    split_input_file = input_file.split('.')
    ext = split_input_file[-1]
    file_without_ext = '.'.join(split_input_file[:-1])

    if current_duration < chunk:
        return False

    ff = subprocess.Popen([
        FFMPEG_BINARY, '-hide_banner', '-i', input_file, '-c', 'copy', '-f', 'segment',
        '-segment_time', str(chunk), '{0}.part%03d.{1}'.format(file_without_ext, ext)
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        print(line.decode(), end='')

    return True


if __name__ == '__main__':
    record(
        'https://aldirect.hls.huya.com/backsrc/'
        '94525224-2460685313-10568562945082523648-2789274524-10057-A-0-1.m3u8',
        './{}.flv'.format(datetime.datetime.now())
    )
