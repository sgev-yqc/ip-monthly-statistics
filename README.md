# ip-monthly-statistics

Hermes Agent 技能（skill）：**知识产权月度统计表填写**——根据专利受理通知书、专利授权证书、软著登记证书、论文发布稿等文件，自动填写知识产权月度统计登记表。

适用于国网系/电力行业单位的「知识产权月度统计表」（6 分类 sheet：国内专利-受理 / 国内专利-授权 / 海外专利PCT / 论文 / 软著 / 论著）。

## 设计理念

技能内容分为两部分：

1. **工作要求（通用）**——表格结构、证书→字段映射、填写规范、标准流程。任何单位/填报人都适用，一般不用改。
2. **个人填写信息（配置区）**——部门/单位、使用保管人、技术领域、智能电网环节、知识产权增加方式、项目类型、必填字段清单等本单位口径，集中放在 `SKILL.md` 文末的「配置区」。

> **分享给他人或换单位使用时，先按对方情况修改配置区即可**，工作要求部分无需改动。

## 功能

- 从专利受理通知书 / 授权证书 / 软著证书 / 论文稿提取信息（支持文本 PDF 与扫描件 OCR）
- 自动映射到对应 sheet 与字段（发明人顿号分隔、日期格式化、编号保留证书原样）
- 累计表（台账：6 分类 sheet + 月度统计汇总）与分月统计表（报送件）双表流程
- 批量解析：pymupdf 提取 + 正则解析 + paddle-ocr 扫描件识别

## 安装

把 `SKILL.md` 放入 Hermes 的 skills 目录（或 external_dirs 共享目录）：

```bash
# 用户级 skills
cp SKILL.md ~/.hermes/skills/ip-monthly-statistics/SKILL.md
# 或共享目录（多 profile 可见）
cp SKILL.md ~/.hermes/shared-skills/ip-monthly-statistics/SKILL.md
```

新会话生效（skill 索引在会话启动时构建）。

## 使用

1. 按本单位情况修改 SKILL.md 文末「配置区」（部门、保管人、技术领域、项目类型等）
2. 提供证书文件（受理通知书 PDF、软著证书、论文发布稿）
3. 技能自动提取信息填入登记表对应 sheet，验证后交付

## 依赖

- openpyxl（填表）
- pymupdf（PDF 文本提取）
- paddleocr（可选，扫描件 OCR）

## License

MIT
