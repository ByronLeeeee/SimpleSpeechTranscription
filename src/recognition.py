from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import configparser
import os


class Recognition:
    
    def __init__(self, model_type=None):
        # Initialize the Recognition class with optional model_type parameter
        self.model_name = model_type
        self.model_path = None
        self.model = None

    def _model_selection(self):
        # 选择基于提供的 model_type 的模型路径的辅助方法
        config = configparser.ConfigParser()
        config_file = 'modellist.ini'
        
        # 检查配置文件是否存在
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"{config_file} 未找到")
        
        config.read(config_file,encoding='utf-8')
        model_info = config['Models']
        
        # 检查提供的 model_type 是否受支持
        if self.model_name in model_info:
            self.model_path = model_info[self.model_name] 
        else:
            return '不支持的模型类型'


    def begin(self, audio_path, output_format='wav', ffmpeg_args=None):
        # Start the recognition process
        if not self.model:
            # Initialize the model if not already initialized
            self._model_selection()
            self.model = pipeline(
                task=Tasks.auto_speech_recognition,
                model=self.model_path)
        
        # Check if the audio file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file {audio_path} not found")
        
        # Set default ffmpeg arguments if not provided
        if not ffmpeg_args:
            ffmpeg_args = ['-ac', '1', '-ar', '16000']
        
        # Check if the output file has the correct format
        if audio_path.endswith(f'.{output_format}'):
            wav_file = audio_path
        else:
            # Convert the audio file to WAV format using ffmpeg
            wav_file = audio_path.replace(f'.{output_format}', '.wav')
            os.system(f'ffmpeg -i {audio_path} {" ".join(ffmpeg_args)} {wav_file}')

        # Perform speech recognition on the WAV file
        rec_result = self.model(audio_in=wav_file)

        return rec_result