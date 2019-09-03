import datetime
import json
import os
import re
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
    :return: video's duration in seconds, False if video is not valid
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

    rename(input_file, chunk)

    return True


def rename(input_file, chunk):
    has_part = True
    while has_part:
        for each_file in os.listdir(os.path.dirname(input_file)):
            # fixme: hard-coded file extension
            if re.search(r'part\d{3}\.mp4', each_file) is None:
                has_part = False
                continue

            has_part = True
            part = int(re.findall(r'part(\d{3})\.mp4', each_file)[0])

            # why bytes???
            date = each_file.split('.')[0]

            if part == 0:
                # first part
                dst_filename = date + '.mp4'
                print('{} -> {}'.format(each_file, dst_filename))
                os.rename(each_file, dst_filename)
                continue

            dst_filename = str(
                datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=chunk / 3600)) + '.mp4'
            print('{} -> {}'.format(each_file, dst_filename))
            os.rename(each_file, dst_filename)


if __name__ == '__main__':
    record(
        'https://aldirect.hls.huya.com/backsrc/'
        '94525224-2460685313-10568562945082523648-2789274524-10057-A-0-1.m3u8',
        './{}.mp4'.format(datetime.datetime.now())
    )
