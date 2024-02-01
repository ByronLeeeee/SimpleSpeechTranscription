import os
import subprocess
from urllib.request import urlretrieve
from zipfile import ZipFile
from tqdm import tqdm

class AudioConverter:
    """
    将音频文件".mp3", ".flac", ".ogg"转换为 ".wav" 格式的工具类。

    Attributes:
        ffmpeg_path (str): ffmpeg 可执行文件的路径，如果未提供，则尝试从系统路径中查找或下载。
    
    Methods:
        convert_audio_files: 将指定文件夹中的音频文件转换为 WAV 格式，并保存到指定的输出文件夹中。
    """

    def __init__(self, ffmpeg_path=None):
        """
        初始化 AudioConverter 对象。

        Args:
            ffmpeg_path (str, optional): ffmpeg 可执行文件的路径。如果未提供，则尝试从系统路径中查找或下载。
        """
        self.ffmpeg_path = ffmpeg_path
        if not self.ffmpeg_path:
            try:
                subprocess.run(["ffmpeg", "-version"], check=True)
                self.ffmpeg_path = "ffmpeg"
            except FileNotFoundError:
                ffmpeg_env = os.environ.get("FFMPEG")
                if ffmpeg_env:
                    self.ffmpeg_path = ffmpeg_env
                else:
                    self.ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg")
                    self._download_ffmpeg()

    def _download_ffmpeg(self):
        '''
        下载并解压 ffmpeg 至本地路径./ffmpeg/
        '''
        print("未找到本地安装的 ffmpeg，正在下载官方版本...")

        # 指定 ffmpeg-release-essentials.zip 下载链接
        ffmpeg_download_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

        # 指定下载文件名
        ffmpeg_download_filename = "ffmpeg.zip"

        # 下载 ffmpeg-release-essentials.zip
        print("正在下载 ffmpeg...")
        urlretrieve(ffmpeg_download_url, ffmpeg_download_filename)

        # 解压文件
        print("正在解压 ffmpeg...")
        with ZipFile(ffmpeg_download_filename, 'r') as zip_ref:
            zip_ref.extractall()

        # 设置本地 ffmpeg 路径
        self.ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg")
        try:
            subprocess.run([self.ffmpeg_path, "-version"], check=True)
        except FileNotFoundError:
            print("ffmpeg 解压失败，请到https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip 手动下载并解压 ffmpeg-release-essentials.zip 文件到 ffmpeg 文件夹中")
            exit(1)

    def convert_audio_files(self, input_folder="./input/", output_folder= "./wav/"):
        """
        将指定文件夹中的音频文件转换为 WAV 格式，并保存到指定的输出文件夹中。

        Args:
            input_folder (str, optional): 输入文件夹路径，默认为 "./input/"。
            output_folder (str, optional): 输出文件夹路径，默认为 "./wav/"。

        Returns:
            str: 转换结果。
        """
        # 检查输入文件夹是否存在，不存在则提示用户
        if not os.path.isdir(input_folder):
            # 创建输出文件夹
            os.makedirs(input_folder, exist_ok=True)
            result = f"输入文件夹不存在，请先将待转换的音频文件放入{input_folder}文件夹中。"
            return result

        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)

        # 获取输入文件夹中的所有音频文件
        audio_files = [f for f in os.listdir(input_folder) if f.endswith((".mp3", ".flac", ".ogg"))]
        print(audio_files)

        if not audio_files:
            result = f"未发现任何音频文件，请将待转换的音频文件放入{input_folder}文件夹中。"
            return result

        # 初始化进度条
        progress_bar = tqdm(total=len(audio_files), desc="转换进度")

        print(f"发现{len(audio_files)}个音频文件，正在转换中...")
        convert_success = 0
        convert_faults = 0
        # 遍历每个音频文件并转换为 wav
        for audio_file in audio_files:
            input_path = os.path.join(input_folder, audio_file)
            output_path = os.path.join(output_folder, os.path.splitext(audio_file)[0] + ".wav")
            try:
                # 使用本地 ffmpeg 进行转换
                subprocess.run([self.ffmpeg_path, "-i", input_path, output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                convert_success += 1 
            except Exception as e:
                print(f"转换 {input_path} 失败，错误信息：{e}")
                convert_faults += 1

            # 更新进度条和显示当前处理的文件
            progress_bar.update(1)
            progress_bar.set_postfix(当前文件=audio_file)

        # 完成后关闭进度条
        progress_bar.close()

        result = f"音频文件转换完成！共发现{len(audio_files)}个音频文件，成功转换{str(convert_success)}，失败{str(convert_faults)}个。"
        return result

# 使用示例
if __name__ == "__main__":
    # 创建 AudioConverter 实例，如果未提供 ffmpeg_path，则会尝试从环境变量获取或下载官方版本
    converter = AudioConverter()

    # 设置输入和输出文件夹路径
    input_folder = "./input/"
    output_folder = "./wav/"

    # 调用 convert_audio_files 方法进行转换
    result = converter.convert_audio_files(input_folder, output_folder)
    print(result)
