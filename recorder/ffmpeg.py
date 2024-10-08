import datetime
import json
import os
import random
import shutil
import subprocess
import tempfile

import tqdm

import recorder

TIMEOUT_US = str(4 * 1000000)  # 4s
USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114',
    'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.2.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15'
)
FFMPEG_BINARY = recorder.config['app'].get('ffmpeg_path', 'ffmpeg')
FFPROBE_BINARY = recorder.config['app'].get('ffprobe_path', 'ffprobe')
ERROR_CHECK_LIST = (
    'illegal reordering_of_pic_nums_idc',
    'illegal memory management control operation',
    'Out of range weight is not implemented',
    'Non-monotonous DTS in output stream',
)


def record(input_url, output_file, max_duration, max_size, headers=None, args=None):
    popen_args = [
        FFMPEG_BINARY, '-y', '-user_agent', random.choice(USER_AGENTS), '-hide_banner',
        # If set, then even streamed/non seekable streams will be reconnected on errors.
        '-reconnect_streamed', '1',
        # Sets the maximum delay in seconds after which to give up reconnecting.
        '-reconnect_delay_max', '16',
        '-rw_timeout', TIMEOUT_US, '-timeout', TIMEOUT_US
    ]

    if headers is not None:
        popen_args.extend(['-headers', '\n'.join(headers)])

    popen_args.extend(['-i', input_url, '-c', 'copy'])

    if max_size:
        popen_args.extend(['-fs', str(max_size)])

    if max_duration:
        popen_args.extend(['-t', str(max_duration)])

    if args is not None:
        popen_args.extend([str(each) for each in args])

    popen_args.append(output_file)

    ff = subprocess.Popen(popen_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        line = line.decode()
        print(line, end='')

        if any([each in line for each in ERROR_CHECK_LIST]):
            recorder.logger.error(f'FFmpeg Error, quitting: {line.strip()}')
            ff.communicate(b'q')
            return ff.wait()

    return ff.wait()


def ffprobe(input_file):
    """
    :param input_file: video's path or stream url
    :return: video's format information in json dictionary, None if video is not valid
    """
    args = [FFPROBE_BINARY]

    if str(input_file).startswith('http'):
        args.extend(['-user_agent', random.choice(USER_AGENTS)])

    args.extend([
        '-loglevel', 'warning', '-hide_banner', '-print_format', 'json', '-rw_timeout', TIMEOUT_US,
        '-show_format', '-show_streams', '-select_streams', 'v', '-i', input_file
    ])

    proc = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    recorder.logger.debug(
        f'ffprobe args: {json.dumps(args)}, stdout: {proc.stdout.decode()}, stderr: {proc.stderr.decode()}'
    )

    try:
        res = json.loads(proc.stdout)
    except ValueError:
        return None

    if not res:
        return None

    return res


def duration(input_file):
    """
    :param input_file: video's path
    :return: video's duration in seconds, False if video is not valid
    """
    res = ffprobe(input_file)

    return int(float(res['format']['duration'])) if res else False


def valid(input_file):
    """
    :param input_file: video's path or stream url
    :return: True if video is valid, False if not
    """
    res = ffprobe(input_file)

    return len(res['streams']) != 0 if res else False


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


def calc_end_time(input_file, start_time_str, datetime_format='%Y-%m-%d %H:%M:%S'):
    current_duration = duration(input_file)

    assert current_duration is not False

    return datetime.datetime.strptime(start_time_str, datetime_format) + datetime.timedelta(seconds=current_duration)


def start_time(input_file):
    res = ffprobe(input_file)

    return int(float(res['format']['start_time'])) if res else False


def get_video_thumb(input_file, output_file=None, time=6, size=320):
    output_file = output_file or tempfile.NamedTemporaryFile(suffix='.jpg').name

    probe = ffprobe(input_file)
    width = int(probe['streams'][0]['width'])
    height = int(probe['streams'][0]['height'])
    # https://trac.ffmpeg.org/wiki/Scaling#KeepingtheAspectRatio
    scale = f'{size}:-1' if width > height else f'-1:{size}'

    subprocess.run([
        FFMPEG_BINARY, '-hide_banner', '-ss', str(time), '-i', input_file,
        '-filter:v', f'scale={scale}', '-vframes:v', '1', output_file
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return output_file


def generate_candidate_thumbnails(input_file, output_dir, size=320, sampling_interval=60):
    probe = ffprobe(input_file)

    if not probe:
        return []

    width = int(probe['streams'][0]['width'])
    height = int(probe['streams'][0]['height'])
    # https://trac.ffmpeg.org/wiki/Scaling#KeepingtheAspectRatio
    scale = f'{size}:-1' if width > height else f'-1:{size}'

    d = duration(input_file)
    assert d is not False

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    count = d // sampling_interval
    count = count if count >= 3 else 3  # at least 3 thumbnails

    thumbnails = []
    for i in tqdm.tqdm(range(1, count + 1), desc=f'Generating {count} thumbnails for {os.path.basename(input_file)}'):
        current_time = d // (count + 1) * i
        output_file = os.path.join(output_dir, f'{i}_{current_time}.jpg')

        cmd = [FFMPEG_BINARY, '-hide_banner', '-ss', str(current_time), '-i', input_file]

        if size is not None:
            cmd.extend(['-filter:v', f'scale={scale}'])

        cmd.extend(['-vframes:v', '1', output_file])

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError as e:
            print(f'FFmpeg Error when generating thumbnail, cmd: {cmd}, output: {e.output.decode()}')
            continue

        # check if the thumbnail is valid
        if not os.path.exists(output_file):
            print(f'FFmpeg Error when generating thumbnail, file not exists: {output_file}')
            continue

        thumbnails.append(output_file)

    return thumbnails


if __name__ == '__main__':
    import fire

    fire.Fire()
