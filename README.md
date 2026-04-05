# fio_lab

使用 `fio` 对存储设备进行基础测试、块大小测试、并发与队列深度测试、I/O 引擎测试，并保存结果与图表。

## 目录说明

- `scripts/`：测试脚本与图表生成脚本
- `results/`：当前整理后的测试结果 JSON
- `results/repeat_runs/`：重复测试得到的原始数据
- `images/`：生成好的图表
- `报告.tex`：实验报告

## 主要脚本

- `scripts/fio基础测试.sh`
- `scripts/fio块大小测试.sh`
- `scripts/fio队列深度测试.sh`
- `scripts/fio引擎测试.sh`
- `scripts/generate_charts.py`

## 说明

- `results/*.json` 是当前采用的结果文件
- `results/repeat_runs/**/*.json` 是计算均值时使用的原始数据
- 图表可通过 `python3 scripts/generate_charts.py` 重新生成
