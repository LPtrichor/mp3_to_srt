@echo off
:: 设置编码格式为utf-8，避免乱码
chcp 65001
:: 清除当前目录及其子目录下的所有 .mp3 和 .srt 文件
FOR /R %%i IN (*.mp3, *.srt) DO (
    echo 正在删除: "%%i"
    DEL "%%i"
)

echo 清理完成。
pause
