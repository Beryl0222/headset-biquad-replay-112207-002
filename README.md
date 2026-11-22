# 双版耳机固件的定点双二阶滤波算子

双字宽设备的滤波系数、数字饱和语义与双声道采集记录。样例均为合成记录。

使用 CPython 3.11 读取资料。当前资料工具与关联测试只需要标准库。数值开发环境的可用库锁定在 requirements.txt 中，可在新的虚拟环境执行 python3 -m pip install -r requirements.txt。


    python3 records.py device_records.json
    python3 -m unittest -v

[数据约定](DATA.md)解释输入时序、坐标及数值口径。

还可生成一套默认 30 秒、八声道的合成 PCM 回放，用于检查采样号、切换提案和播放回执的输入契约。单位、文件格式及事件见数据约定。

    python3 generate_capture.py /tmp/filter-capture
    python3 records.py /tmp/filter-capture/capture.json
