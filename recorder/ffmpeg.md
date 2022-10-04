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
