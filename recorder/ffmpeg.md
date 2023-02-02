# ffmpeg commands

## hwaccel for video re-encoding (e.g. fps equalization)

### nvenc

```bash
ffmpeg -hide_banner -hwaccel cuda -hwaccel_output_format cuda -extra_hw_frames 8 -i input.mp4 -c:a copy -c:v h264_nvenc output_nvenc.mp4
```

### h264_qsv

```bash
ffmpeg -hide_banner -init_hw_device qsv=hw -filter_hw_device hw -i input.mp4 -c:a copy -c:v h264_qsv output_qsv.mp4
```

### h264_amf

```bash
ffmpeg -hide_banner -hwaccel dxva2 -c:v h264_dxva2 -i input.mp4 -c:a copy -c:v h264_amf output_amf.mp4
```

## mute part of video

```bash
ffmpeg -hide_banner -i input.mp4 -af "volume=enable='between(t,2*2600+15*60+6,2*3600+18*60+10)':volume=0" -c:v copy output.mp4
```

## cut up video

```bash
# Credit: https://stackoverflow.com/a/42827058/6266737
ffmpeg -hide_banner -ss 02:14:00 -to 02:14:20 -i input.mp4 -c copy output.mp4
```
