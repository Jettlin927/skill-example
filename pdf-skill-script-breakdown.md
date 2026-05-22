# PDF skill 中 scripts 的流程职责拆解

## 总体观察

当前仓库里的 `pdf/` skill 不是一个“只有提示词的 skill”。它的 `SKILL.md` 负责给出 PDF 处理的总入口和常见能力说明；当任务进入“填写 PDF 表单”这个复杂分支时，`SKILL.md` 明确要求读取 `forms.md`，而 `forms.md` 再把流程拆成一系列脚本化步骤。

这说明这个 skill 的设计思路是：

> AI 负责判断、理解和决策；脚本负责检查、抽取、转换、校验和写入。

PDF 表单填写特别适合这样拆，因为它同时涉及：

- PDF 是否有 AcroForm 可填字段。
- 字段 ID、页码、选项值、checkbox/radio 状态。
- PDF 坐标系和图片坐标系转换。
- 视觉定位、结构定位、混合定位。
- 写入后是否重叠、是否偏位、是否超出文本框。

这些细节如果每次都让 AI 临时写代码，效率低，而且非常容易在坐标、页码、字段值、字体尺寸上出错。

## 原流程中的脚本职责地图

PDF 表单填写流程大致可以拆成五段：

```text
识别表单类型
  -> 抽取可操作结构
  -> 人/AI 决定字段含义和填写内容
  -> 写入前校验
  -> 执行填充并验证输出
```

对应到脚本：

| 流程阶段 | 脚本 | 承担职责 |
| --- | --- | --- |
| 识别表单类型 | `check_fillable_fields.py` | 判断 PDF 是否有可填表单字段，决定走 fillable 还是 non-fillable 分支 |
| 抽取 fillable 字段结构 | `extract_form_field_info.py` | 提取字段 ID、页码、坐标、字段类型、checkbox/radio/choice 可用值 |
| 视觉理解辅助 | `convert_pdf_to_images.py` | 把 PDF 渲染成 PNG，供 AI/人判断字段在页面上的真实含义 |
| 抽取 non-fillable 页面结构 | `extract_form_structure.py` | 从不可填 PDF 中提取文字标签、横线、checkbox、小矩形和行边界 |
| 写入前校验 | `check_bounding_boxes.py` | 检查 label/entry 框是否相交、输入框高度是否小于字体大小 |
| 视觉校验辅助 | `create_validation_image.py` | 在页面图上画出 label 和 entry 框，帮助检查坐标准不准 |
| 填充 fillable 表单 | `fill_fillable_fields.py` | 根据字段 ID 写入真实 PDF 表单字段，并校验字段 ID、页码和值是否合法 |
| 填充 non-fillable 表单 | `fill_pdf_form_with_annotations.py` | 用 FreeText annotation 把文本写到指定坐标，自动处理 PDF/图片坐标转换 |

## 逐个脚本拆解

### 1. check_fillable_fields.py：流程分流器

在 `forms.md` 的第一步，AI 不能直接开始填表，而是必须先运行：

```bash
python scripts/check_fillable_fields.py <file.pdf>
```

这个脚本只做一件事：用 `pypdf.PdfReader(...).get_fields()` 判断 PDF 是否存在可填字段。

它承担的是“流程分流”职责：

- 如果有可填字段，走 AcroForm 字段填充流程。
- 如果没有可填字段，走视觉定位 + annotation 填写流程。

为什么适合做成脚本：

- 判断标准明确，不需要语言模型推理。
- 如果 AI 直接凭页面外观判断，可能把可填字段当成普通文本框。
- 这个判断决定后续整条路线，分错支会导致后续全部返工。

### 2. extract_form_field_info.py：把隐藏 PDF 字段变成结构化 JSON

fillable PDF 的难点是：用户看到的是页面上的“姓名、地址、勾选框”，但程序真正要写入的是 PDF 内部字段 ID 和合法值。

这个脚本提取：

- `field_id`
- `page`
- `rect`
- `type`
- checkbox 的 checked/unchecked value
- radio group 的选项值和坐标
- choice 字段的可选项

它承担的是“结构抽取”职责，把 PDF 内部对象转换成 AI 可读、可编辑的 JSON。

为什么适合做成脚本：

- PDF 表单字段常常有父子层级，字段 ID 需要沿 `/Parent` 拼接。
- checkbox、radio、choice 的合法值不是肉眼能稳定判断的。
- 如果让 AI 临时写这段逻辑，每次都可能漏掉 radio group、choice options 或页码坐标。
- JSON 输出形成了后续 `field_values.json` 的契约，降低了自由发挥空间。

### 3. convert_pdf_to_images.py：给 AI 一个视觉判断面

无论是 fillable 还是 non-fillable 流程，都需要把 PDF 转成图片。

在 fillable 流程里，它帮助 AI 看懂字段含义：字段 ID 可能叫 `Text1`、`Checkbox12`，但图片能告诉 AI 这个字段实际是“Last Name”还是“Over 18”。

在 non-fillable 流程里，它是视觉估算坐标的基础。

为什么适合做成脚本：

- PDF 渲染参数需要稳定，例如 dpi、输出命名、最大尺寸。
- 后续坐标判断依赖图片尺寸，渲染方式不稳定会导致坐标不稳定。
- 统一输出 `page_1.png` 这类格式，后续流程和验证更容易复用。

### 4. extract_form_structure.py：不可填 PDF 的结构雷达

对于没有可填字段的 PDF，不能直接写入字段，只能在页面上添加文本 annotation。这时最难的是确定坐标。

这个脚本用 `pdfplumber` 提取：

- 页面尺寸。
- 文字 label 的坐标。
- 横线位置。
- 小方框 checkbox。
- 根据横线推导出的行边界。

它承担的是“结构定位”职责，优先让 AI 使用 PDF 内部可抽取结构，而不是完全靠肉眼估。

为什么适合做成脚本：

- 坐标提取是机械任务，程序比模型稳定。
- 结构坐标比视觉估算更准确。
- 横线、label、checkbox 的提取规则可以复用。
- 它给 AI 留下的是“解释这些结构属于什么字段”，而不是“从零开始猜坐标”。

### 5. check_bounding_boxes.py：写入前的安全检查

在 non-fillable 流程里，AI 需要创建 `fields.json`，里面包含 `label_bounding_box` 和 `entry_bounding_box`。

这个脚本检查：

- label 框和 entry 框是否相交。
- 不同字段的框是否互相重叠。
- entry 框高度是否小于字体大小。

它承担的是“写入前验证”职责。

为什么适合做成脚本：

- 框相交、字体高度不够这类问题是确定性几何问题。
- AI 自己看 JSON 很容易漏掉坐标重叠。
- 提前失败比生成一个错位 PDF 后再返工更便宜。
- 错误信息能直接指向哪个字段需要修。

### 6. create_validation_image.py：把抽象坐标变成可视检查图

这个脚本把 `fields.json` 中的框画到页面图片上：

- entry 框用红色。
- label 框用蓝色。

它承担的是“人工/视觉验证辅助”职责。

为什么适合做成脚本：

- 坐标 JSON 本身不可直观看出对不对。
- 一张 validation image 能快速发现整体偏移、框选错行、框太窄等问题。
- 这是典型的调试辅助，不应该每次让 AI 临时写 PIL 绘图代码。

### 7. fill_fillable_fields.py：fillable 表单的受控写入器

这个脚本负责真正写入可填字段，但它不是简单写入。写入前会再次调用字段信息抽取逻辑，并校验：

- `field_id` 是否存在。
- `page` 是否正确。
- checkbox 的值是否是合法 checked/unchecked value。
- radio group 的值是否在可选项中。
- choice 字段的值是否在可选项中。

它承担的是“受控执行”职责。

为什么适合做成脚本：

- PDF 字段写入有很多隐藏约束。
- checkbox/radio 的值不是简单的 `true/false`。
- 写错字段 ID 可能静默失败，脚本可以提前报错。
- 这一步直接产出最终 PDF，必须减少模型自由度。

### 8. fill_pdf_form_with_annotations.py：non-fillable 表单的坐标写入器

当 PDF 没有可填字段时，这个脚本用 FreeText annotation 写入文本。

它处理两种坐标输入：

- `pdf_width` / `pdf_height`：说明 `fields.json` 使用 PDF 坐标。
- `image_width` / `image_height`：说明 `fields.json` 使用图片坐标，需要转换到 PDF 坐标。

它承担的是“坐标转换 + annotation 写入”职责。

为什么适合做成脚本：

- PDF 坐标和图片坐标方向不同，尤其 y 轴转换非常容易错。
- 坐标转换公式固定，应该程序化。
- annotation 的字体、字号、颜色、矩形框格式都需要稳定。
- 这一步如果由 AI 临时写，最常见问题就是文字上下颠倒、偏移或落到错误页面。

## 这个 skill 的脚本设计模式

这个 PDF skill 里的脚本不是随机工具集合，而是围绕一条流程组织的：

### inspect

先检查输入是什么。

- `check_fillable_fields.py`
- `extract_form_field_info.py`
- `extract_form_structure.py`

### transform

把输入变成后续可操作的中间表示。

- `convert_pdf_to_images.py`
- `extract_form_field_info.py`
- `extract_form_structure.py`

### validate

在真正写入前发现错误。

- `check_bounding_boxes.py`
- `fill_fillable_fields.py` 内部的字段和值校验
- `create_validation_image.py`

### execute

真正修改 PDF。

- `fill_fillable_fields.py`
- `fill_pdf_form_with_annotations.py`

这就是一个成熟 skill 很重要的设计：不是只有“怎么做”的说明，而是把关键节点工具化。

## 为什么这些不应该只写在 SKILL.md 里

如果只写在 `SKILL.md`，大概会变成：

> 先判断 PDF 是否有可填字段；如果有，提取字段；如果没有，提取坐标；然后根据坐标填写；最后验证。

这个说法听起来完整，但实际执行时会出现几个问题：

- AI 每次都要重新写 PDF 字段提取代码。
- 坐标转换可能每次写法不同。
- checkbox/radio/choice 的合法值可能被猜错。
- 错误无法程序化提前发现。
- 输出文件是否可靠，取决于模型这次有没有注意到所有细节。

把这些步骤变成脚本后，skill 的稳定性来自三件事：

- 输入输出契约稳定：JSON schema、命令参数、文件路径明确。
- 复杂细节封装稳定：PDF 内部字段、坐标转换、annotation 写入不反复重写。
- 失败信息稳定：字段不存在、值非法、坐标相交都会明确报错。

## 对同事写 skill 的启发

可以把这个 PDF skill 当作样板：

1. `SKILL.md` 不负责承载所有细节，只负责入口、主流程和资源导航。
2. 复杂分支放到 reference，例如这里的 `forms.md`。
3. 每个关键流程节点都问一句：这里是让 AI 判断更合适，还是让脚本执行更合适？
4. 只要是检查、抽取、转换、校验、写入，就优先考虑脚本。
5. 脚本之间最好形成中间产物契约，例如 `field_info.json`、`fields.json`、`field_values.json`。

所以这个 PDF skill 的价值不只是“有 scripts 文件夹”，而是它把 AI 的工作限制在最擅长的地方：理解页面含义、选择流程分支、根据用户意图填值；同时把不适合自由发挥的机械细节交给脚本。

