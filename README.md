# nb-pdf-template-zh

给 Jupyter Notebook 的 PDF 导出补上中文、特殊符号和同行选择框。

基于 [t-makaro/nb_pdf_template](https://github.com/t-makaro/nb_pdf_template) 的 5.0.1 版，保留它的代码框、语法配色和标题排版。默认 A4、11 pt，章节不自动编号。

下面以 Windows、Conda 和 MiKTeX 为例。已有 TeX Live 的话，也可以直接使用。

## 下载源码，创建 Conda 环境

```powershell
git clone https://github.com/jeoor/nb-pdf-template-zh.git
cd nb-pdf-template-zh
conda env create -f environment.yml
conda activate notebook-pdf-zh
```

也可以在 GitHub 点击 `Code → Download ZIP`，解压后进入仓库目录。

`environment.yml` 提供 Python、JupyterLab、nbconvert、nbformat、Pandoc、pip 和构建工具 Hatchling。MiKTeX 或 TeX Live 需要另外安装。

如果使用已有环境，先激活它，再安装对应依赖：

```powershell
conda install -c conda-forge "python=3.11" "jupyterlab>=4,<5" "nbconvert>=7,<8" "nbformat>=5,<6" "pandoc>=3,<4" pip "hatchling>=1,<2"
```

## 安装 MiKTeX

从 [MiKTeX 官网](https://miktex.org/download) 下载 Windows 安装程序。安装范围选择当前用户，目录使用默认值即可。官方也推荐[按用户安装](https://miktex.org/howto/install-miktex)。

安装完成后打开 `MiKTeX Console`：

1. 在 `Updates` 中点击 `Check for Updates`，再点击 `Update now`。
2. 打开 `Settings → General`，选择 `Always install missing packages on-the-fly`。

第二个设置允许编译时自动下载缺少的宏包。Jupyter 的导出过程不方便确认安装弹窗，所以这里直接启用自动安装。设置说明见 [MiKTeX Console 文档](https://miktex.org/howto/miktex-console)。

重新打开终端，激活 Conda 环境，检查命令：

```powershell
conda activate notebook-pdf-zh
where.exe xelatex
xelatex --version
pandoc --version
```

如果 `xelatex` 找不到，把 MiKTeX 安装目录中的 `miktex\bin\x64` 加入用户 `PATH`，再重开终端。如果同时安装了 MiKTeX 和 TeX Live，以 `where.exe xelatex` 的第一条结果为准。

可以提前安装主要宏包，减少第一次导出时的等待：

```powershell
miktex packages update-package-database
miktex packages install ctex fandol tcolorbox needspace newunicodechar
```

其他依赖由 MiKTeX 在编译时补齐。命令用法见[官方包管理文档](https://docs.miktex.org/manual/miktex-packages.html)。

模板默认使用 [Fandol 字体](https://miktex.org/packages/fandol)，由 TeX 提供，复现时不用额外安装 Windows 中文字体。[CTeX](https://miktex.org/packages/ctex) 负责中文排版，编译引擎使用 XeLaTeX。

已有 TeX Live 的话，确认 `xelatex` 可用，并安装对应的中文字体和宏包即可。这台机器的实际验证使用 TeX Live 2025；MiKTeX 的步骤依据官方文档整理，尚未实测。

## 安装模板，先导出一次

在仓库根目录运行：

```powershell
python -m pip install --no-build-isolation --no-deps .
jupyter nbconvert examples/chinese.ipynb --to pdf --template latex_authentic_zh --output-dir examples --output chinese_check
```

前面的 Conda 环境已经安装了构建工具和运行依赖，所以这里直接安装本地源码。以后修改模板后，也用同一条安装命令更新。

成功后会生成 `examples/chinese_check.pdf`，里面有中文、代码、公式、表格和选择框。导出使用 Notebook 已保存的输出，不重新运行代码。

也可以直接从源码导出：

```powershell
python -m nb_pdf_template examples/chinese.ipynb --hide-prompts
```

这条命令生成 `examples/chinese_authentic_zh.pdf`。

## 设置为 Jupyter 默认模板

Jupyter 网页菜单和命令行需要读到同一份配置。这里把配置放在当前 Conda 环境的 `etc/jupyter/jupyter_config.py` 中。

先查看完整路径：

```powershell
python -c "from pathlib import Path; import sys; print(Path(sys.prefix) / 'etc' / 'jupyter' / 'jupyter_config.py')"
```

新建这个文件。如果已经存在，把下面的设置加进去，保留原有内容：

```python
c = get_config()
c.LatexExporter.template_name = "latex_authentic_zh"
c.PDFExporter.template_name = "latex_authentic_zh"
c.LatexExporter.template_file = "index.tex.j2"
c.PDFExporter.template_file = "index.tex.j2"
c.LatexExporter.exclude_input_prompt = True
c.LatexExporter.exclude_output_prompt = True
c.PDFExporter.exclude_input_prompt = True
c.PDFExporter.exclude_output_prompt = True
```

这里也隐藏了 `[179]:` 这类执行编号。如果需要保留，把四个 `exclude_*_prompt` 设置改成 `False`。

保存 Notebook，重启 Jupyter，并从这个 Conda 环境启动：

```powershell
jupyter lab
```

在菜单中选择 `PDF via LaTeX`。命令行也可以省略 `--template`：

```powershell
jupyter nbconvert examples/chinese.ipynb --to pdf --output-dir examples --output chinese_default
```

如果已有配置覆盖了这些设置，用 `jupyter --paths` 查看配置搜索路径，再检查对应文件。直接指定 `--template latex_authentic_zh` 可以确认模板是否安装成功。

## 常用设置

从源码导出时可以指定输出文件、提示编号位置和字体：

```powershell
python -m nb_pdf_template report.ipynb --output report.pdf
python -m nb_pdf_template report.ipynb --to latex --output report.tex
python -m nb_pdf_template report.ipynb --layout above
python -m nb_pdf_template report.ipynb --hide-prompts
python -m nb_pdf_template report.ipynb --fontset auto
```

`--layout above` 把执行编号放在代码框上方，`--hide-prompts` 隐藏编号。`--fontset auto` 让 CTeX 选择系统字体，效果会随系统变化。希望别人复现相近的效果，保留默认 Fandol 即可。

普通 nbconvert 命令使用上方编号模板时，指定 `--template-file m`：

```powershell
jupyter nbconvert report.ipynb --to pdf --template latex_authentic_zh --template-file m
```

总标题写在第一个 Markdown 单元格中，例如 `# 报告标题`。作者信息直接写在标题下面。

正文和表格中的 `[ ]` 会导出为 ☐，`[x]`、`[X]` 会导出为 ☑，同一行可以写多个：

```markdown
[x] 可信　[ ] 存疑　[ ] 不可信
-[ ] -[x]
```

标准任务列表 `- [ ]`、`- [x]` 同样支持。代码、公式、链接和已保存的代码输出保持原样。这是 PDF/LaTeX 导出的适配，Notebook 编辑器的显示由编辑器本身决定。

常用符号如 `☐ ☑ ☒ ✓ ≠ ≈ ≤ ≥ × ± → α π σ` 也可以直接写入正文。

## 检查环境和导出结果

```powershell
python --version
python -m pip show nb-pdf-template-zh nbconvert nbformat
pandoc --version
xelatex --version
python -m unittest discover -s tests -v
```

本地验证使用 Windows、Python 3.11、nbconvert 7.17.1、nbformat 5.11.1、Pandoc 3.12 和 TeX Live 2025。测试覆盖标题、中文与符号、选择框、执行编号和代码保留，示例已实际编译为 PDF。

`environment.yml` 约束主要版本，方便创建兼容环境；它没有锁定所有依赖和 TeX 宏包版本。MiKTeX 会更新宏包，所以重建环境不保证 PDF 文件逐字节相同。

出现 `xxx.sty not found` 时，在 MiKTeX Console 的 `Packages` 中搜索并安装对应宏包，再导出。字体找不到时，检查 `fandol` 是否安装。修改 `PATH` 或默认配置后，重开终端并重启 Jupyter。

## 来源和许可证

上游基底：[t-makaro/nb_pdf_template 5.0.1](https://github.com/t-makaro/nb_pdf_template/tree/c98382fb09ee00c7d303b957459b4649bb67451e)。

中文配置参考了 [nb-tmpl-ctex](https://pypi.org/project/nb-tmpl-ctex/) 和[《关于 Jupyter Nbconvert 自定义 LaTeX 模板，中文兼容与格式设置》](https://www.cnblogs.com/BOXonline1396529/p/18256506)。Eisvogel、ElegantPaper 也作过参考，当前主体排版沿用上游模板。

保留上游 [MIT 许可证](LICENSE)。宏包声明改编自 nbconvert 的 LaTeX 模板，遵循 BSD-3-Clause，完整说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
