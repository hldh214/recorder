import datetime
import json
import subprocess

TIMEOUT_US = str(60 * 1000000)


def record(input_url, output_file):
    ff = subprocess.Popen([
        'ffmpeg', '-hide_banner', '-rw_timeout', TIMEOUT_US, '-timeout', TIMEOUT_US,
        '-i', input_url, '-c', 'copy', output_file
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        print(line.decode(), end='')


def show_format(input_file):
    """
    :param input_file: video's path or m3u8 url
    :return: video's format information in json dictionary, None if video is not valid
    """
    proc = subprocess.run([
        'ffprobe', '-print_format', 'json',
        '-show_format', '-i', input_file
    ], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

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

    return res['format']['duration'] if res else False


def valid(input_file):
    """
    :param input_file: video's path or m3u8 url
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
        'ffmpeg', '-hide_banner', '-i', input_file, '-c', 'copy', '-f', 'segment',
        '-segment_time', str(chunk), '{0}.part%03d.{1}'.format(file_without_ext, ext)
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        print(line.decode(), end='')

    return True


if __name__ == '__main__':
    record(
        'https://aldirect.hls.huya.com/backsrc/'
        '94525224-2460685313-10568562945082523648-2789274524-10057-A-0-1.m3u8',
        './{}.mp4'.format(datetime.datetime.now())
    )
