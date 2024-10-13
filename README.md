# 基于OCR的小猿口算自动PK脚本

本项目基于纯视觉方案，无须root且不受接口或程序版本的影响。

只支持比大小，平均8秒/10题（CPU）；GPU推理也许会更快，我没条件测试。

## 快速开始

1. 克隆本仓库
2. 安装依赖
3. 将需要被检测的窗口名填入`config.json`中的window_name
4. 根据你的设备更改检测区域以及`main.py`中`draw_less_than`和`draw_more_than`函数中的绘制坐标。
5. 连接一个可以被调试的安卓设备
6. 运行`main.py`