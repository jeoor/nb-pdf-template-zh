import copy
import json
from pathlib import Path
import unittest

import nbformat
from nbconvert import LatexExporter
from nbconvert.filters.pandoc import convert_pandoc

from nb_pdf_template.checkboxes import render_checkboxes


class TemplateTests(unittest.TestCase):
    def export(self, nb, layout='index.tex.j2', **options):
        templates = str(Path(__file__).resolve().parents[1] / 'share' / 'templates')
        exporter = LatexExporter(template_name='latex_authentic_zh', template_file=layout,
                                 extra_template_basedirs=[templates], extra_template_paths=[templates],
                                 **options)
        return exporter.from_notebook_node(nb)[0]

    def notebook(self):
        return nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell('# 中文标题\n\n示例作者\n\n## 正文\n\n符号：≈ ≥ ☐ ☑ α。'),
            nbformat.v4.new_code_cell('print("机器人.测试")', execution_count=2,
                                     outputs=[nbformat.v4.new_output('stream', name='stdout', text='机器人.测试\n'),
                                              nbformat.v4.new_output('execute_result', execution_count=2,
                                                                    data={'text/latex': '$x^2$'})])])

    def test_headings_and_saved_outputs_are_preserved(self):
        nb = self.notebook()
        before = copy.deepcopy(nb)
        latex = self.export(nb)
        self.assertEqual(nb, before)
        self.assertIn('中文标题', latex)
        self.assertIn('机器人.测试', latex)
        self.assertIn('\\documentclass[11pt,a4paper]{article}', latex)
        self.assertIn('\\setcounter{secnumdepth}{0}', latex)
        self.assertNotIn('\\maketitle', latex)
        self.assertIn('scheme=plain,fontset=fandol', latex)
        self.assertIn('boxrule=1pt', latex)
        self.assertNotIn('SimSun', latex)

    def test_xecjk_character_classes_are_not_changed(self):
        latex = self.export(self.notebook())
        self.assertNotIn('XeTeXcharclass', latex)
        self.assertNotIn('XeTeXinterchartoks', latex)
        self.assertIn('008800', latex)
        self.assertIn('AA22FF', latex)
        self.assertIn('\\newunicodechar{☑}', latex)
        self.assertIn('\\@ifundefined{c@none}', latex)

    def test_above_prompts_use_current_interface_and_a4(self):
        latex = self.export(self.notebook(), 'm.tex.j2')
        self.assertIn('\\newcommand{\\prompt}[4]', latex)
        self.assertIn('\\prompt{In}{incolor}{2}', latex)
        self.assertIn('\\documentclass[11pt,a4paper]{article}', latex)

    def test_native_prompt_filter_and_system_font_option(self):
        nb = self.notebook()
        nb.metadata['latex_authentic_zh'] = {'fontset': 'auto'}
        latex = self.export(nb, exclude_input_prompt=True, exclude_output_prompt=True)
        self.assertNotIn('\\prompt{In}', latex)
        self.assertNotIn('\\prompt{Out}', latex)
        self.assertIn('\\usepackage[UTF8,scheme=plain]{ctex}', latex)

    def test_inline_table_and_task_checkboxes(self):
        nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(
            '[x] 可信　[ ] 存疑　[X] 不可信\n\n'
            '-[ ] -[x]\n\n'
            '- [ ] 空项 - [x] 同行勾选\n'
            '- [x] 已完成\n\n'
            '| 判断 |\n| --- |\n| [x]是 [ ]否 |\n\n'
            '原有符号：☒')])
        before = copy.deepcopy(nb)
        latex = self.export(nb).split('\\begin{document}', 1)[1]
        self.assertEqual(nb, before)
        self.assertIn('☑ 可信', latex)
        self.assertIn('☐ 存疑', latex)
        self.assertIn('☑ 不可信', latex)
        self.assertIn('☐ ☑', latex)
        self.assertIn(r'\item[$\square$]', latex)
        self.assertIn('空项 ☑ 同行勾选', latex)
        self.assertIn(r'\item[☑]', latex)
        self.assertIn('已完成', latex)
        self.assertIn('☑是 ☐否', latex)
        self.assertIn('原有符号：☒', latex)

    def test_code_math_links_and_saved_results_keep_their_brackets(self):
        source = ('正文 [x]，`[x] [ ]`，$a[x]$，data[x]，'
                  '[链接[x]](https://example.com/a[x])，![图[x]](image.png)\n\n'
                  '```python\nvalue = "[x] [ ]"\n```\n\n'
                  '$$b[x]$$')
        original = json.loads(convert_pandoc(source, 'markdown-task_lists', 'json'))
        converted = json.loads(render_checkboxes(json.dumps(original)))

        def protected(node):
            if isinstance(node, dict):
                if node.get('t') in {'Code', 'CodeBlock', 'Math', 'Link', 'Image'}:
                    return [node]
                return protected(node.get('c', []))
            if isinstance(node, list):
                return [item for child in node for item in protected(child)]
            return []

        self.assertEqual(protected(original['blocks']), protected(converted['blocks']))
        self.assertIn('data[x]', json.dumps(converted, ensure_ascii=False))
        self.assertIn('☑', json.dumps(converted, ensure_ascii=False))
        nb = nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell('[x] prose\n\n```\n\\item[$\\boxtimes$]\n```'),
            nbformat.v4.new_code_cell('value = "[x] [ ]"', execution_count=179,
                                     outputs=[nbformat.v4.new_output('stream', name='stdout',
                                                                   text='[x] [ ]\n')])])
        before = copy.deepcopy(nb)
        latex = self.export(nb)
        self.assertEqual(nb, before)
        self.assertIn('[x] [ ]', latex)
        self.assertIn('☑ prose', latex)
        self.assertIn('\\begin{verbatim}\n\\item[$\\boxtimes$]\n\\end{verbatim}', latex)


if __name__ == '__main__':
    unittest.main()
