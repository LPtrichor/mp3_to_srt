import gradio as gr
from dotenv import load_dotenv
import sys
import importlib
import os
from fastapi import FastAPI
from process_video.main import mp3_to_srt


app = FastAPI()
class ChatBotManager:
    def __init__(self):
        load_dotenv()
        self.app = app
        self._init_file_upload()  # 初始化文件上传路由

    def _init_file_upload(self):
        # 使用Gradio界面来实现文件上传
        def upload_file(file_obj, file_name):
            # if file_obj is not None:
            #     save_path = f"uploads/{file_obj.name}"
            #     with open(save_path, "wb") as buffer:
            #         shutil.copyfileobj(file_obj.file, buffer)
            #     return "文件上传成功"
            # return "没有上传文件"
            if file_obj is None:
                return "没有上传文件"
            if not file_name:
                return "文件名不能为空"
            # 确保uploads目录存在
            os.makedirs("uploads", exist_ok=True)
            # save_path = f"uploads/{file_name}"
            save_path = f"process_video/{file_name}"
            with open(save_path, "wb") as buffer:
                buffer.write(file_obj)
            return f"文件 {file_name} 上传成功"

        def provide_file_for_download():
            # mp3_to_srt()
            # 列出./process_video目录下的所有.srt文件
            srt_files = ["./process_video/" + f for f in os.listdir("./process_video") if f.endswith(".srt")]
            print(srt_files)
            # print(srt_files)
            return srt_files
            # with open("test.srt", "rb") as file:
            #     return file.read(), "file.srt"

        def clean():
            # 删除process_video目录下的所有.srt文件
            srt_files = ["./process_video/" + f for f in os.listdir("./process_video") if f.endswith(".srt")]
            for srt_file in srt_files:
                os.remove(srt_file)
            # 删除process_video目录下的所有.mp3文件
            mp3_files = ["./process_video/" + f for f in os.listdir("./process_video") if f.endswith(".mp3")]
            for mp3_file in mp3_files:
                os.remove(mp3_file)
            return "清除成功"

        with gr.Blocks() as file_upload_interface:
            # gr.Markdown("# 上传音频文件")
            # file_input = gr.File(label="选择一个音频文件", type="binary")
            # submit_button = gr.Button("上传")
            # output = gr.Text(label="上传结果")
            #
            # file_input.change(fn=upload_file, inputs=[file_input], outputs=[output])
            gr.Markdown("# 上传音频文件")
            file_input = gr.File(label="选择一个音频文件", type="binary")
            file_name_input = gr.Textbox(label="输入文件名", placeholder="请输入文件名...")
            submit_button = gr.Button("上传")
            output = gr.Text(label="上传结果")
            produce_srt = gr.Button("生成字幕")
            srt_produce = gr.Text(label="生成字幕结果")
            clean_srt = gr.Button("清除之前的字幕和音频文件")
            clean_result = gr.Text(label="清除结果")
            # 返回字幕文件给用户下载
            # output_text = gr.Text(label="处理结果")
            # output_link = gr.Text(label="下载字幕文件", interactive=True, visible=False)

            # 字幕下载
            # file_input.change(fn=upload_file, inputs=[file_input, file_name_input], outputs=[output])
            submit_button.click(fn=upload_file, inputs=[file_input, file_name_input], outputs=[output])
            produce_srt.click(fn=mp3_to_srt, inputs=[], outputs=[srt_produce])
            clean_srt.click(fn=clean, inputs=[], outputs=[clean_result])
            # output_link.change(fn=download_link, inputs=[output_link], outputs=[output_link])


            download_button = gr.Button("下载字幕文件")
            file_download = gr.File(label="下载字幕文件")

            # 当下载按钮被点击时，调用 provide_file_for_download 函数
            # 并将返回的文件内容和文件名传递给 file_download 组件以供下载
            download_button.click(fn=provide_file_for_download, inputs=[], outputs=file_download)

        # 将Gradio界面挂载到FastAPI应用
        gr.mount_gradio_app(self.app, file_upload_interface, path="/")

    def _init_file_download(self):
        def provide_file_for_download():
            # mp3_to_srt()
            # 列出./process_video目录下的所有.srt文件
            srt_files = ["./process_video/" + f for f in os.listdir("./process_video") if f.endswith(".srt")]
            print(srt_files)
            # print(srt_files)
            return srt_files
            # with open("test.srt", "rb") as file:
            #     return file.read(), "file.srt"

        with gr.Blocks() as demo:
            download_button = gr.Button("下载字幕文件")
            file_download = gr.File(label="下载字幕文件")

            # 当下载按钮被点击时，调用 provide_file_for_download 函数
            # 并将返回的文件内容和文件名传递给 file_download 组件以供下载
            download_button.click(fn=provide_file_for_download, inputs=[], outputs=file_download)

        # 将Gradio界面挂载到FastAPI应用
        gr.mount_gradio_app(self.app, demo, path="/download")

    def start(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8123)
        # uvicorn.run(f"chatbot_manager:app", host="0.0.0.0", port=8123, reload=True)


if __name__ == "__main__":
    chatbot_manager = ChatBotManager()
    chatbot_manager.start()
