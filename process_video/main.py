from pydub import AudioSegment
import math
import os
import glob
import sys
import re
from datetime import datetime, timedelta
# 音频翻译成英文
from openai import OpenAI
import json
import subprocess

# 读取config.json文件
with open('config.json', 'r') as config_file:
    loaded_config = json.load(config_file)
api_key = loaded_config.get('OPENAI_API_KEY')
# print(api_key)
# sys.exit()
# os.environ['OPENAI_BASE_URL'] = 'https://www.api.rovy.me/v1'
os.environ['OPENAI_API_KEY'] = api_key
client = OpenAI()


# 指定FFmpeg的路径
# ffmpeg_path = r"E:\Software\ffmpeg-master-latest-win64-gpl\bin"
# os.environ["PATH"] += os.pathsep + ffmpeg_path

def split_audio_with_ffmpeg(file_path, segment_length_ms):
    # 确保输出目录存在
    output_dir = "./process_video"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 计算分割后的音频长度，ffmpeg 需要的是秒
    segment_length_s = segment_length_ms / 1000
    print(f"segment_length_s: {segment_length_s}")
    # 构建ffmpeg命令
    cmd = [
        'ffmpeg',
        '-i', file_path,
        '-f', 'segment',
        '-segment_time', str(segment_length_s),
        '-c', 'copy',
        os.path.join(output_dir, 'segment_%03d.mp3')
    ]

    # 执行ffmpeg命令
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)




def split_audio(file_path, segment_length_ms):
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    segments_count = math.ceil(duration_ms / segment_length_ms)

    for i in range(segments_count):
        start_ms = i * segment_length_ms
        end_ms = min((i + 1) * segment_length_ms, duration_ms)
        segment = audio[start_ms:end_ms]
        segment.export(f"./process_video/segment_{i}.mp3", format="mp3")


def generate_corrected_transcript(temperature, system_prompt, text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
    )
    # print(response)
    # print(type(response))
    return response.choices[0].message.content


# isTranslate = False
# 遍历文件列表


def str_to_timedelta(time_str):
    return datetime.strptime(time_str, '%H:%M:%S,%f') - datetime(1900, 1, 1)


def timedelta_to_str(time_delta):
    hours, remainder = divmod(time_delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:06.3f}".format(int(hours), int(minutes), seconds).replace('.', ',')


def adjust_subtitle_time(subtitle, time_offset):
    try:
        time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
        start_time_str, end_time_str = time_pattern.search(subtitle).groups()
        start_time = str_to_timedelta(start_time_str) + time_offset
        end_time = str_to_timedelta(end_time_str) + time_offset
        adjusted_subtitle = re.sub(time_pattern, f'{timedelta_to_str(start_time)} --> {timedelta_to_str(end_time)}',
                                   subtitle)
        return adjusted_subtitle
    except:
        return subtitle


def merge_subtitles(subtitle_files, video_durations):
    merged_subtitle = ""
    time_offset = timedelta()
    subtitle_index = 1

    for subtitle_file, duration in zip(subtitle_files, video_durations):
        # print(subtitle_file, duration)
        with open(subtitle_file, 'r', encoding='utf-8') as f:  # Use UTF-8 encoding
            print(subtitle_file)
            subtitles = f.read().strip().split('\n\n')
            for subtitle in subtitles:
                print(subtitle)
                if not subtitle.strip():
                    continue
                adjusted_subtitle = adjust_subtitle_time(subtitle, time_offset)
                adjusted_subtitle = re.sub(r'^\d+', str(subtitle_index), adjusted_subtitle, count=1)
                merged_subtitle += adjusted_subtitle + "\n\n"
                subtitle_index += 1
        time_offset += timedelta(seconds=duration)

    return merged_subtitle.strip()


def mp3_to_srt():
    # 打印当前所在目录
    # print(os.getcwd())
    cwd_prefix = "process_video/"
    # 使用示例
    # file_path = "name.mp3"  # 你的音频文件路径
    # 获取当前目录下所有的.mp3文件
    mp3_files = glob.glob(cwd_prefix + '*.mp3')

    # 检查是否至少有一个.mp3文件
    if mp3_files:
        # 只取第一个.mp3文件
        file_path = mp3_files[0]
        print(f'file_path: {file_path}')
        # 去掉文件路径前面的 './'
        # file_path = file_path.lstrip('./')
        # 打印输出，正在处理名为 file_path 的文件
        print(f"正在处理名为 {file_path} 的文件")
    else:
        print("没有找到任何.mp3文件")
        file_path = None
        # 当需要停止程序时
        return "没有找到任何.mp3文件"
        # sys.exit()
    segment_length_ms = 20 * 60 * 1000  # 每个片段的长度，这里设置为30秒
    # split_audio(file_path, segment_length_ms)
    split_audio_with_ffmpeg(file_path, segment_length_ms)

    # 获取当前目录下所有以 'segment_' 开头的 .mp3 文件
    segment_files = glob.glob(cwd_prefix + 'segment_*.mp3')
    if segment_files == []:
        segment_files = mp3_files[0]

    print(f"segment_files: {segment_files}")
    for filename in segment_files:
        with open(filename, "rb") as audio_file:
            translate = client.audio.translations.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt",
            )
            # 根据音频文件名生成SRT文件名
        srt_filename = filename.replace('.mp3', '.srt')

        # 存储翻译结果到SRT文件
        with open(srt_filename, "w", encoding='utf-8') as f:
            f.write(translate)

        print(f"Translation for {filename} saved to {srt_filename}")

    # 示例使用 glob 查找文件和假定的视频持续时间
    subtitle_files = glob.glob(cwd_prefix + 'segment*.srt')
    subtitle_files.sort()  # 确保按顺序处理文件

    video_durations = [20 * 60 for _ in subtitle_files]  # 假设每段视频20分钟

    merged_subtitle = merge_subtitles(subtitle_files, video_durations)

    # 去除'.mp3'后缀
    file_name_without_extension = file_path.rsplit('.', 1)[0]

    # 拼接新的文件路径
    new_file_path = f"{file_name_without_extension}.srt"
    # 保存合并后的字幕文件
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(merged_subtitle)

    return "字幕文件生成成功"

# mp3_to_srt()
