def main():
    """
    Main thread:
        for each source in sources do get_source
        can we hold a websocket connection? one for all sources or each?
        if on air then spawn a ffmpeg subprocess and a (optional) danmaku process
        need to rewrite a new processor for ffmpeg, danmaku and after record things
        it's a new python file and it can handle those process gracefully
        when the ffmpeg exit, danmaku should also exit
        when the danmaku exit, try to reconnect with last timestamp if ffmpeg is still recording
        and finally do the after-recording things
    Uploader thread:
        do the upload things
    Validator thread:
        do the validator things
    :return:
    """
    pass


if __name__ == '__main__':
    main()
