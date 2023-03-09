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
# Credit: https://stackoverflow.com/a/42827058
ffmpeg -hide_banner -ss 02:14:00 -to 02:14:20 -i input.mp4 -c copy output.mp4
```

## merge with ass danmaku

```bash
ffmpeg -hide_banner -i .\output.mp4 -c:a copy -vf "ass=./590890573.ass" output_with_ass.mp4
```

## horizontal to vertical

```bash
# Credit: https://stackoverflow.com/a/34676898
# more blur
ffmpeg -hide_banner -i .\output_with_ass.mp4 -lavfi "[0:v]scale=iw:2*trunc(iw*16/18),boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,setsar=1" output_vertical.mp4

# Credit: https://video.stackexchange.com/a/34389
# less blur
ffmpeg -hide_banner -i .\output_with_ass.mp4 -vf 'split[original][copy];[copy]scale=-1:ih*(16/9)*(16/9),crop=w=ih*9/16,gblur=sigma=20[blurred];[blurred][original]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2' output_vertical.mp4
```
