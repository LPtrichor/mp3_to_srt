import os
import uvicorn
from fastapi import FastAPI
import gradio as gr
from dotenv import load_dotenv
from process_video.main import mp3_to_srt

load_dotenv()

app = FastAPI()

class ChatBotManager:
    def __init__(self):
        self.app = app
        self._init_file_upload()

    def _init_file_upload(self):
        def upload_file(file_obj):
            if file_obj is None:
                return "没有上传文件"
            file_name = file_obj.name  # 自动从上传的文件中获取文件名
            os.makedirs("uploads", exist_ok=True)
            save_path = os.path.join("uploads", file_name)
            with open(save_path, "wb") as buffer:
                buffer.write(file_obj.read())  # 确保二进制读取
            return f"文件 {file_name} 上传成功"

        def provide_file_for_download():
            srt_files = [os.path.join("uploads", f) for f in os.listdir("uploads") if f.endswith(".srt")]
            return srt_files if srt_files else ["没有可下载的字幕文件"]

        def clean():
            for extension in ['.srt', '.mp3']:
                for file in os.listdir("uploads"):
                    if file.endswith(extension):
                        os.remove(os.path.join("uploads", file))
            return "清除成功"

        with gr.Blocks() as file_upload_interface:
            gr.Markdown("# 上传音频文件")
            file_input = gr.File(label="选择一个音频文件")
            submit_button = gr.Button("上传")
            output = gr.Text(label="上传结果")
            produce_srt = gr.Button("生成字幕")
            srt_produce = gr.Text(label="生成字幕结果")
            clean_srt = gr.Button("清除文件")
            clean_result = gr.Text(label="清除结果")
            download_button = gr.Button("下载字幕文件")
            file_download = gr.Dropdown(label="选择下载的字幕文件", choices=provide_file_for_download())

            submit_button.click(fn=upload_file, inputs=[file_input], outputs=[output])
            produce_srt.click(fn=mp3_to_srt, inputs=[], outputs=[srt_produce])
            clean_srt.click(fn=clean, inputs=[], outputs=[clean_result])
            download_button.click(fn=provide_file_for_download, inputs=[], outputs=file_download)

        gr.mount_gradio_app(self.app, file_upload_interface, path="/")

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=7123)

if __name__ == "__main__":
    chatbot_manager = ChatBotManager()
    chatbot_manager.start()
