import subprocess


def record(input_url, output_file):
    ff = subprocess.Popen([
        'ffmpeg', '-hide_banner', '-i', input_url, '-c', 'copy', output_file
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in ff.stdout:
        print(line.decode(), end='')


if __name__ == '__main__':
    record(
        'https://aldirect.hls.huya.com/backsrc/'
        '94525224-2460685313-10568562945082523648-2789274524-10057-A-0-1.m3u8',
        './out.mp4'
    )
