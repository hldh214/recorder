import json
import subprocess


def record(input_url, output_file):
    ff = subprocess.Popen([
        'ffmpeg', '-hide_banner', '-i', input_url, '-c', 'copy', output_file
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        print(line.decode(), end='')


def duration(input_file):
    """
    :param input_file: video's path
    :return: video's duration, False if video is not valid
    """
    proc = subprocess.run([
        'ffprobe', '-print_format', 'json',
        '-show_format', '-i', input_file
    ], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    res = json.loads(proc.stdout)

    if not res:
        return False

    return int(float(res['format']['duration']))


def valid(input_file):
    return bool(duration(input_file))


def split(input_file, chunk=10 * 3600):
    pass


if __name__ == '__main__':
    record(
        'https://aldirect.hls.huya.com/backsrc/'
        '94525224-2460685313-10568562945082523648-2789274524-10057-A-0-1.m3u8',
        './out.mp4'
    )
