import gradio as gr
from src.recognition import Recognition
from configparser import ConfigParser
from src.toWav import AudioConverter
import os

# 读取modellist.ini文件，获取模型名称
conf = ConfigParser()
conf.read('modellist.ini',encoding='utf-8')

# 使用正确的section名称
model_list = conf.options('Models')

def start_identifying(audio_paths, model):
    rec = Recognition(str(model))  # 确保模型是字符串类型
    results_text = []  # 用于存储所有音频识别的文本结果
    results_sentences = []  # 用于存储所有音频识别的完整结果

    for audio_path in audio_paths:
        try:
            result = rec.begin(audio_path)
            text_result = result.get('text')
            sentences_result = result.get('sentences', [])
            
            results_text.append(str(text_result))    
            results_sentences.extend(sentences_result)

            # 保存文件前检查输出文件夹是否存在，如果不存在则创建
            output_folder = '.\output'
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 保存 text_result 到文件
            audio_filename = os.path.basename(audio_path)
            text_filename = f"{output_folder}\\{os.path.splitext(audio_filename)[0]}-全文.txt"
            with open(text_filename, 'w', encoding='utf-8') as text_file:
                text_file.write(text_result)

            # 如果 sentences_result 中有包含 'spk' 键的字典，则生成带说话人信息的 txt 文件
            if any('spk' in sentence for sentence in sentences_result):
                spk_filename = f"{output_folder}\\{os.path.splitext(audio_filename)[0]}-带说话人.txt"
                with open(spk_filename, 'w', encoding='utf-8') as spk_file:
                    for sentence in sentences_result:
                        if 'spk' in sentence:
                            spk_file.write(f"[{sentence['start']} - {sentence['end']}] - [说话人{sentence['spk'] + 1}] - {sentence['text']}\n")

        except Exception as e:
            print("Error occurred while processing audio path:", audio_path, "- skipping.")
            print(str(e))

    # 更新 Textbox 中的结果
    result_textbox = f"[{os.path.basename(audio_paths[0])}]\n" + results_text[0]
    return result_textbox

def input_folder_check():
    # 检查输入文件夹是否存在，如果不存在则创建
    input_folder = '.\input'
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

def convert_to_wav():
    result = AudioConverter().convert_audio_files()
    return result

with gr.Blocks(title="Simple Local Speech2Text") as app:
    with gr.Tab(label='识别音频'):
        with gr.Row():
            with gr.Column():
                model_list_radio = gr.Radio(label="模型选择", choices=model_list, type='value',)
                audio_file_path = gr.FileExplorer(label="待分析语音文件列表", glob='*.wav', file_count='multiple', root_dir=f'.\wav')
                begin_btn = gr.Button(value="开始识别", variant='primary')
                gr.Markdown(value='''### 说明 \n
                            识别结果并非100%准确，仅供参考。\n
                            识别结果将保存至当前目录下的output文件夹中。\n
                            首次使用会先下载模型，通常模型较大，请耐心等候。\n
                            模型会默认下载至系统的临时文件夹下，通常在C:\\Users\\（用户名）\\ .cache\\modelscope\\hub\\iic。\n
                            如果网速较慢，可能会下载失败，具体显示为无法输出结果，请尝试重新点击识别。\n
                            如果下载实在太慢，可以通过https://www.modelscope.cn/models/ + modellist.ini中的模型网址进入网站下载并放到上面的文件夹路径中\n                      
                            预设模型介绍：\n\n
                            paraformer-large-Chinese：普通话(支持判断说话人）\n
                            paraformer-large_English:英语模型\n
                            UniASR-Cantonese：粤语模型\n
                            UniASR-Chinese_Dialects：支持东北、甘肃、贵州、河南、湖北、湖南、江西、宁夏、山西、陕西、山东、四川、天津、云南十四种带口音方言.\n
                            UniASR-Japanese：日语\n
                            UniASR-Minnan：闽南语\n
                            其他模型可自行到魔搭社区下载：https://modelscope.cn/models?page=1&tasks=auto-speech-recognition&type=audio \n
                            但默认代码不一定支持全部模型，请自行修改。
                            ''')
            with gr.Column():
                result_textbox = gr.Textbox(label="预览输出结果（只显示第一个文件结果）", lines=20)

        # 指令执行
        begin_btn.click(start_identifying, inputs=[audio_file_path, model_list_radio], outputs=result_textbox)

    with gr.Tab(label='转换音频'):
        with gr.Row():
            with gr.Column():
                input_folder_check()
                audio_file_path = gr.FileExplorer(label="待转换音频文件", file_count='multiple', root_dir=f'.\input')
                convert_result = gr.Textbox(label="转换结果", value="请先将需要转换的音频文件放到input文件夹，支持.mp3/.flac/.ogg格式")
                begin_btn = gr.Button(value="开始转换", variant='primary')
            with gr.Column():
                gr.Markdown(value='''### 使用说明\n本页面用于将.mp3/.flac/.ogg格式音频文件转换为 WAV 格式。请先把需要转换的文件放至程序所在的input文件夹。\n如果本机内未安装ffmpeg，将会自行下载安装。\n\n转换过程中可能需要一些时间，请耐心等候。''')

            begin_btn.click(convert_to_wav, outputs=convert_result)

app.launch(inbrowser=True)
