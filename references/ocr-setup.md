# 扫描件 OCR 环境与踩坑记录（paddle-ocr 技能）

> 2026-09 实测。PaddleOCR 装在 Anaconda base 环境，**不要用系统 python**。

## 环境

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | 3.12.4 | `E:\Anaconda\python.exe` |
| PaddlePaddle | 3.1.1 | 不要升 3.3.1（OneDNN 兼容错误） |
| PaddleOCR | 3.7.0 | |
| paddlepaddle | 3.1.1 | |
| numpy | 2.5.2 | 见下方兼容矩阵 |
| scipy | 1.18.1 | 旧版 1.13.1 与 numpy 2.x 二进制不兼容 |
| opencv-python | 5.0.0 | 4.10 与 numpy 2.x 不兼容 |
| scikit-learn | 1.9.0 | 旧版 1.4.2 与 numpy 2.x 不兼容 |
| scikit-image | 0.26.0 | 旧版 0.23.2 与 numpy 2.x 不兼容 |

## numpy/scipy 兼容矩阵（踩过的坑）

paddle 全家桶按 numpy 2.x 编译，但 Anaconda 里 scipy/sklearn/skimage/opencv 全是 numpy 1.x 时代的旧版。症状与修复：

| 症状 | 原因 | 修复 |
|---|---|---|
| `numpy.core.multiarray failed to import` | scipy 1.13.1 与 numpy 2.x | `pip install "scipy>=1.16"` |
| `numpy.dtype size changed ... Expected 96 from C header, got 88` | sklearn/skimage 旧版 | `pip install --upgrade scikit-learn scikit-image` |
| `cv2.error: buf is not a numpy array` | opencv 4.10 与 numpy 2.x | `pip install "opencv-python>=5"` |
| `A module compiled using NumPy 1.x cannot be run in NumPy 2.x` | 依赖链中某个包还是 numpy 1.x 编译 | 逐层 `--upgrade` 该包 |

**不要把 numpy 降到 1.x**——paddle 3.x 需要 numpy 2；正确方向是升级 scipy/sklearn/skimage/opencv 到支持 numpy 2 的版本。

## 用法

```bash
# 单份
E:/Anaconda/python.exe <paddle-ocr>/scripts/ocr.py "证书.pdf" --dpi 200
# 批量：输出重定向到文件，再正则抓关键行
E:/Anaconda/python.exe ocr.py "a.pdf" --dpi 200 > ocr_a.txt 2>&1
# 输出格式：[置信度] 文本行
```

- 首次运行自动下载模型到 `C:\Users\Qiuqiu\.paddlex\official_models\`（约 100MB+）
- PDF 页多或图大时降低 DPI：`--dpi 150`
- 无文本层的 PDF 在 extract_ip_pdf.py 输出里 chars<50 标记 SCAN

## 解析踩坑（受理通知书/证书文本）

| 坑 | 说明 | 处理 |
|---|---|---|
| 2022 版受理通知书无发明人 | 2022 年格式"申请号、申请日、申请人和发明创造名称通知如下"，不含发明人 | 发明人留空，不臆造 |
| 竖排文本 | 授权证书中"专\n利\n号""发\n明\n人"被竖排拆行 | 正则去换行后匹配，或匹配 `ZL\s*[\d\s.]+` |
| 跨行名单 | 发明人 10+ 人时列表跨多行，单行正则截断 | 块提取：`发明人：\s*(.*?)(?:下一字段名)` 用 re.S |
| 软著登记号竖排 | "登\n记\n号：2026SR0884001" | 直接全局搜 `20\d{2}SR\d+` |
| PCT"申请人"误匹配 | "申请人或代理人的档案号"先出现 | 精确匹配 `国际申请日\s*\(年/月/日\)` 附近字段 |
| OCR 截断 | 长申请人列表 OCR 丢尾 | 人工核对 parsed.json，与文件名/同族证书交叉验证 |

## 其他

- fill_ip.py 曾因起始行写错**覆盖已有记录**——脚本已改为自动检测已有数据行数，从下一个空行写入；手工填表时同样必须先确认已有行数
- OCR 环境修复后若 Anaconda 其他项目受影响，风险自担（本次仅升级了 scipy/sklearn/skimage/opencv 四个包）
