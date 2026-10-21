#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
build_reader_v07.py -- 大模型推理系统工程 v0.7 电子书阅读版渲染器

用法:
    python build_reader_v07.py <package_dir> [--outdir DIR]

读取 v0.7 实验深化包 (18 个分章 Markdown + book_support_v05 / v06 / v07 资产),
渲染两个完全自包含、可单文件携带的 HTML 阅读版:

    <outdir>/电子书阅读版_v0.7.html      全书 18 章, 浏览器原生搜索, 侧栏 18 章 + 新增图表
    <outdir>/新增图表速览_v0.7.html       只含各章 V07 (x.10) 新增块

实现要点 (调用契约见交付说明):
  * Markdown -> HTML: python-markdown, 扩展 tables/fenced_code/footnotes/attr_list/
    def_list/abbr/md_in_html/sane_lists, 不丢原始内容。
  * 数学公式在 Markdown 之前先被"保护"成占位符 (避免 _ * \ 等被 Markdown 破坏),
    渲染后再还原为原始 TeX, 由离线 MathJax (tex-svg-full.js) 以 tex-svg 输出渲染。
  * 本地图片内嵌: 优先匹配同名的 .svg 并以内联 <svg> 嵌入 (matplotlib 路径字体, 视觉最佳);
    否则把 png/jpg 以 base64 data URI 内嵌。图注一律取自原 Markdown 的 alt 文本。
  * 新增内容块由章节内的 <!-- V06-START --> / <!-- V06-END --> (x.9)
    与 <!-- V07-START --> / <!-- V07-END --> (x.10) 包围。
  * 三态切换: 全书 -> 只看 x.10 新增 -> 只看全部新增 (x.9+x.10)。
  * 脚本只读书稿, 不修改任何输入文件。
"""

import argparse
import base64
import html as html_mod
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------------
# 常量
# ----------------------------------------------------------------------------

# 与 markdown.extensions.extra + sane_lists 等价的显式扩展集合
MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "footnotes",
    "attr_list",
    "def_list",
    "abbr",
    "md_in_html",
    "sane_lists",
]

V06_BLOCK_RE = re.compile(
    r"<!--\s*V06-START\s*-->(.*?)<!--\s*V06-END\s*-->", re.DOTALL | re.IGNORECASE)
V07_BLOCK_RE = re.compile(
    r"<!--\s*V07-START\s*-->(.*?)<!--\s*V07-END\s*-->", re.DOTALL | re.IGNORECASE)

CHAPTER_FILE_RE = re.compile(r"^第\s*(\d{1,2})\s*章")

# 占位符定界符: 私用区字符, Markdown 原样透传, 不会与正文冲突
PH_L = "\ue000"
PH_R = "\ue001"
PH_RE = re.compile(PH_L + r"([DIC])(\d+)" + PH_R)

# 附录候选 (存在则嵌入末尾; 相对 package_dir)
APPENDIX_DOCS = [
    ("实验深化说明_v0.7.md", "实验深化说明（v0.7）"),
    ("book_support_v07/来源与核验_v07.md", "来源与核验（v0.7）"),
    ("book_support_v07/来源可信度全文核查_v0.7.md", "来源可信度全文核查（v0.7）"),
    ("book_support_v07/独立核验报告_v07.md", "独立核验报告（v0.7）"),
    ("实验图表补充说明_v0.6.md", "实验图表补充说明（v0.6）"),
    ("book_support_v06/来源与核验.md", "来源与核验（v0.6）"),
    ("book_support_v05/figures.md", "原 v0.5 新增图表与数据目录（只读）"),
    ("book_support_v05/references.md", "原 v0.5 参考资料（只读）"),
]

IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


# ----------------------------------------------------------------------------
# 依赖加载
# ----------------------------------------------------------------------------

def load_deps():
    """导入 Markdown 与 bs4 (在隔离 venv 中安装)。缺失时给出明确指引。"""
    try:
        import markdown  # noqa: F401
    except ImportError:
        sys.exit(
            "缺少依赖 Markdown。请在本任务的隔离 venv 中安装后重试:\n"
            "    <venv>/bin/pip install Markdown beautifulsoup4\n"
            "然后用该 venv 的 python 运行本脚本。"
        )
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        sys.exit(
            "缺少依赖 beautifulsoup4。请安装后重试:\n"
            "    <venv>/bin/pip install beautifulsoup4"
        )
    import markdown
    return markdown


# ----------------------------------------------------------------------------
# 数学 / 行内代码保护
# ----------------------------------------------------------------------------

def _iter_code_regions(text):
    """把文本切成 (is_code, chunk) 序列, 围栏代码块原样保留、不参与数学保护。"""
    lines = text.split("\n")
    i = 0
    buf = []
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^(\s*)(`{3,}|~{3,})(.*)$", line)
        if m:
            if buf:
                yield (False, "\n".join(buf))
                buf = []
            fence_char = m.group(2)[0]
            fence_len = len(m.group(2))
            block = [line]
            i += 1
            close_re = re.compile(r"^\s*" + re.escape(fence_char) + r"{" + str(fence_len) + r",}\s*$")
            while i < n:
                block.append(lines[i])
                if close_re.match(lines[i]):
                    i += 1
                    break
                i += 1
            yield (True, "\n".join(block))
            continue
        buf.append(line)
        i += 1
    if buf:
        yield (False, "\n".join(buf))


INLINE_CODE_RE = re.compile(r"(`+)([^`\n]*?)\1")
DISPLAY_MATH_RE = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
# 行内 $...$: 起始 $ 后不得是空白/$, 允许内容尾部有空格 (原稿存在 "$Prefill $" 这类写法)
INLINE_MATH_RE = re.compile(r"\$(?![\s$])([^$\n]*?)\$(?!\$)")


def protect_text(chunk, items):
    """保护行内代码 -> 显示数学 -> 行内数学, 返回替换后的文本。"""
    def add(kind, tex, raw):
        idx = len(items)
        items.append({"kind": kind, "tex": tex, "raw": raw})
        return PH_L + kind + str(idx) + PH_R

    # 1) 行内代码 (最优先, 其中可能含 $)
    chunk = INLINE_CODE_RE.sub(lambda m: add("C", m.group(2), m.group(0)), chunk)
    # 2) 显示数学 $$...$$
    chunk = DISPLAY_MATH_RE.sub(lambda m: add("D", m.group(1), m.group(0)), chunk)
    # 3) 行内数学 $...$
    chunk = INLINE_MATH_RE.sub(lambda m: add("I", m.group(1), m.group(0)), chunk)
    return chunk


def protect_math(text):
    """保护整段 Markdown 中的代码与数学, 返回 (受保护文本, items)。"""
    items = []
    out = []
    for is_code, chunk in _iter_code_regions(text):
        out.append(chunk if is_code else protect_text(chunk, items))
    return "\n".join(out), items


def restore_math(html, items, mathjax_available):
    """把占位符还原为原始 TeX (MathJax 可用时用 \\(..\\)/\\[..\\], 否则保留源码)。"""
    def esc(s):
        return html_mod.escape(s, quote=False)

    def repl(m):
        kind, idx = m.group(1), int(m.group(2))
        it = items[idx]
        if kind == "C":
            return "<code>%s</code>" % esc(it["tex"])
        if mathjax_available:
            if kind == "D":
                return '<span class="math-block">\\[%s\\]</span>' % esc(it["tex"])
            return '<span class="math-inline">\\(%s\\)</span>' % esc(it["tex"])
        # 资源缺失: 保持原始 TeX 源码, 便于直接阅读
        cls = "math-block math-src" if kind == "D" else "math-inline math-src"
        return '<span class="%s">%s</span>' % (cls, esc(it["raw"]))

    html = PH_RE.sub(repl, html)
    # 单独成段的显示公式去掉外层 <p>
    html = re.sub(
        r"<p>\s*(<span class=\"math-block(?: math-src)?\">.*?</span>)\s*</p>",
        r"\1",
        html,
        flags=re.DOTALL,
    )
    return html


# ----------------------------------------------------------------------------
# Markdown 渲染
# ----------------------------------------------------------------------------

def make_markdown(markdown):
    return markdown.Markdown(extensions=MD_EXTENSIONS, output_format="html5")


def render_markdown(text, markdown):
    """渲染一段 Markdown (已保护数学)。返回 HTML 字符串。"""
    md = make_markdown(markdown)
    return md.convert(text)


# ----------------------------------------------------------------------------
# SVG / 图片内嵌
# ----------------------------------------------------------------------------

def _strip_svg_root_size(svg):
    m = re.search(r"<svg\b[^>]*>", svg)
    if not m:
        return svg
    tag = m.group(0)
    tag = re.sub(r"\s(?:width|height)=\"[^\"]*\"", "", tag)
    if "class=" not in tag:
        tag = re.sub(r"^<svg", '<svg class="fig-svg"', tag)
    return svg[: m.start()] + tag + svg[m.end():]


def _namespace_svg_ids(svg, prefix):
    ids = set(re.findall(r'(?<![\w-])id="([^"]+)"', svg))
    if not ids:
        return svg
    svg = re.sub(r'(?<![\w-])id="([^"]+)"',
                 lambda m: 'id="%s%s"' % (prefix, m.group(1)), svg)
    for i in sorted(ids, key=len, reverse=True):
        svg = svg.replace("xlink:href=\"#%s\"" % i, "xlink:href=\"#%s%s\"" % (prefix, i))
        svg = svg.replace("href=\"#%s\"" % i, "href=\"#%s%s\"" % (prefix, i))
        svg = svg.replace("url(#%s)" % i, "url(#%s%s)" % (prefix, i))
    return svg


def inline_svg(path, prefix, caption):
    """读取 SVG 文件并返回可直接内嵌的 <svg> 片段。"""
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw)
    raw = re.sub(r"<!DOCTYPE[^>]*>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"<metadata>.*?</metadata>", "", raw, flags=re.DOTALL)
    raw = raw.strip()
    raw = _strip_svg_root_size(raw)
    raw = _namespace_svg_ids(raw, prefix)
    # 无障碍属性
    label = html_mod.escape(caption or path.name, quote=True)
    raw = re.sub(r"<svg\b", '<svg role="img" aria-label="%s"' % label, raw, count=1)
    return raw


def data_uri(path):
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }.get(path.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def resolve_image(src, base_dir, pkg_dir):
    """解析图片相对路径, 优先返回匹配的 .svg。返回 Path 或 None。"""
    src = src.split("#")[0].split("?")[0]
    for root in (base_dir, pkg_dir):
        p = (root / src)
        if p.suffix.lower() == ".png":
            svg = p.with_suffix(".svg")
            if svg.is_file():
                return svg
        if p.is_file():
            return p
    # 兜底: 若只给了 .png 但只有 .svg 存在
    p = base_dir / src
    alt = p.with_suffix(".svg")
    if alt.is_file():
        return alt
    return None


_IMG_TAG_RE = re.compile(r"<img\b[^>]*>")
_ATTR_RE = re.compile(r'(\w[\w:-]*)\s*=\s*"([^"]*)"')


def embed_images(html, base_dir, pkg_dir, registry):
    """把渲染出的 <img> 换成内嵌 figure (SVG 内联 / 位图 base64), 图注保留 alt。"""
    counter = {"n": len(registry)}

    def repl(m):
        tag = m.group(0)
        attrs = dict(_ATTR_RE.findall(tag))
        src = attrs.get("src", "")
        caption = attrs.get("alt", "") or attrs.get("title", "")
        if not src or src.startswith(("data:", "http://", "https://", "//")):
            return tag
        path = resolve_image(src, base_dir, pkg_dir)
        if path is None:
            return tag  # 找不到: 保持原样
        counter["n"] += 1
        prefix = "f%d-" % counter["n"]
        cap_html = html_mod.escape(caption, quote=False)
        if path.suffix.lower() == ".svg":
            try:
                inner = inline_svg(path, prefix, caption)
            except Exception as exc:  # noqa: BLE001
                print("[warn] SVG 内嵌失败 %s: %s" % (path, exc), file=sys.stderr)
                return tag
        else:
            try:
                uri = data_uri(path)
            except Exception as exc:  # noqa: BLE001
                print("[warn] 位图内嵌失败 %s: %s" % (path, exc), file=sys.stderr)
                return tag
            alt = html_mod.escape(caption, quote=True)
            inner = '<img class="fig-img" alt="%s" src="%s">' % (alt, uri)
        registry.append({"src": src, "path": str(path), "caption": caption})
        fig = '<figure class="fig">%s<figcaption>%s</figcaption></figure>' % (inner, cap_html)
        return fig

    html = _IMG_TAG_RE.sub(repl, html)
    # 去掉包裹图片的孤立 <p>
    html = re.sub(r"<p>\s*(<figure class=\"fig\">.*?</figure>)\s*</p>", r"\1", html, flags=re.DOTALL)
    return html


# ----------------------------------------------------------------------------
# HTML 后处理
# ----------------------------------------------------------------------------

def wrap_tables(html):
    return re.sub(
        r"(<table\b.*?</table>)",
        r'<div class="table-wrap">\1</div>',
        html,
        flags=re.DOTALL,
    )


def scope_footnote_ids(html, ch_key):
    """给脚注 id 加章节前缀, 保证跨章唯一且章内引用仍然正确。"""
    html = re.sub(r'id="((?:fnref|fn):[^"]+)"',
                  lambda m: 'id="%s-%s"' % (ch_key, m.group(1)), html)
    html = re.sub(r'href="#((?:fnref|fn):[^"]+)"',
                  lambda m: 'href="#%s-%s"' % (ch_key, m.group(1)), html)
    return html


def dedupe_ids(html):
    """安全网: 让 id 全局唯一 (重复项加后缀)。构造上不应触发。"""
    seen = set()
    dup = {}

    def repl(m):
        i = m.group(1)
        if i in seen:
            dup[i] = dup.get(i, 1) + 1
            return 'id="%s__%d"' % (i, dup[i])
        seen.add(i)
        return m.group(0)

    return re.sub(r'(?<![\w-])id="([^"]+)"', repl, html)


def extract_v06_blocks(html):
    """抽取章节 HTML 中的 V06 (x.9) 新增块内容。"""
    return [m.group(1) for m in V06_BLOCK_RE.finditer(html)]


def extract_v07_blocks(html):
    """抽取章节 HTML 中的 V07 (x.10) 新增块内容。"""
    return [m.group(1) for m in V07_BLOCK_RE.finditer(html)]


def wrap_v06_blocks(html):
    """把 V06/V07 注释标记替换为可切换的容器 (兼容被 <p> 包裹的情况)。"""
    html = re.sub(r"(?:<p>\s*)?<!--\s*V06-START\s*-->(?:\s*</p>)?",
                  '<div class="v06-block">', html, flags=re.IGNORECASE)
    html = re.sub(r"(?:<p>\s*)?<!--\s*V06-END\s*-->(?:\s*</p>)?",
                  "</div>", html, flags=re.IGNORECASE)
    html = re.sub(r"(?:<p>\s*)?<!--\s*V07-START\s*-->(?:\s*</p>)?",
                  '<div class="v07-block">', html, flags=re.IGNORECASE)
    html = re.sub(r"(?:<p>\s*)?<!--\s*V07-END\s*-->(?:\s*</p>)?",
                  "</div>", html, flags=re.IGNORECASE)
    return html


# ----------------------------------------------------------------------------
# 链接重写
# ----------------------------------------------------------------------------

def rewrite_links(html, base_dir, pkg_dir, appendix_map):
    """本地 .md 目标映射到附录 section; 其它本地文件标注为原始文件; 外部链接保持。"""
    def repl(m):
        whole, href = m.group(0), m.group(1)
        if not href or href.startswith(("#", "http://", "https://", "mailto:", "data:", "//")):
            return whole
        target = href.split("#")[0].split("?")[0]
        if not target:
            return whole
        p = (base_dir / target)
        key = str(p.resolve()) if p.exists() else None
        if key and key in appendix_map:
            # Explicit source anchors remain globally unique after embedding.
            # Do not concatenate two fragment delimiters (#apx-2#x05).
            new_href = ("#" + href.split("#", 1)[1]) if "#" in href else appendix_map[key]
            return whole.replace('href="%s"' % href, 'href="%s"' % new_href)
        # Rebase non-embedded files to the output/package root. An appendix's
        # data/foo.json must not be resolved relative to the top-level HTML.
        if re.search(r"\.(md|csv|json|py|sh|png|svg|txt|ya?ml)$", target, re.IGNORECASE):
            suffix = href[len(target):]
            try:
                rebased = p.resolve().relative_to(pkg_dir.resolve()).as_posix() + suffix
            except ValueError:
                rebased = href
            esc_t = html_mod.escape(rebased, quote=True)
            whole = whole.replace('href="%s"' % href, 'href="%s"' % esc_t)
            return whole.replace(
                "<a ",
                '<a class="orig-file" data-orig="%s" title="原始文件：%s" ' % (esc_t, esc_t),
                1,
            )
        return whole

    return re.sub(r"<a\b[^>]*href=\"([^\"]*)\"[^>]*>", repl, html)


# ----------------------------------------------------------------------------
# 页面外壳
# ----------------------------------------------------------------------------

BASE_CSS = """
:root{
  --bg:#ffffff; --fg:#1f2328; --muted:#57606a; --line:#e5e7eb; --soft:#f6f8fa;
  --accent:#1f6feb; --accent-soft:#eaf2ff; --nav-w:264px; --content-w:1000px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB",
  "Microsoft YaHei",Roboto,"Helvetica Neue",Arial,sans-serif;
  font-size:17px;line-height:1.85;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
a.orig-file{color:var(--muted);border-bottom:1px dotted var(--muted)}
a.orig-file::after{content:" ⧉";font-size:.85em;color:var(--muted)}

/* ---- 侧栏 ---- */
#sidebar{position:fixed;top:0;left:0;bottom:0;width:var(--nav-w);overflow-y:auto;
  background:#fbfcfd;border-right:1px solid var(--line);padding:20px 14px 40px;z-index:30}
#sidebar h1{font-size:15px;line-height:1.5;margin:0 0 4px;font-weight:700}
#sidebar .sub{font-size:12px;color:var(--muted);margin-bottom:14px}
#sidebar .grp{font-size:12px;color:var(--muted);margin:16px 0 6px;letter-spacing:.04em}
#sidebar a.nav{display:block;padding:6px 10px;border-radius:7px;color:var(--fg);
  font-size:14px;line-height:1.5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#sidebar a.nav:hover{background:var(--accent-soft);text-decoration:none;color:var(--accent)}

/* ---- 主区 ---- */
#main{margin-left:var(--nav-w)}
.wrap{max-width:var(--content-w);margin:0 auto;padding:28px 30px 96px}
header.book{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:26px}
header.book h1{font-size:26px;line-height:1.4;margin:0 0 8px}
header.book .meta{font-size:13.5px;color:var(--muted)}
header.book .meta b{color:var(--fg)}

.toolbar{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);
  backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
  padding:10px 0;margin:-28px -30px 22px;padding-left:30px;padding-right:30px}
.mode-toggle{border:1px solid var(--line);background:#fff;color:var(--fg);
  border-radius:8px;padding:7px 14px;font-size:14px;cursor:pointer}
.mode-toggle:hover{background:var(--soft)}
body.only-new .mode-toggle,body.only-v07 .mode-toggle{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}

/* ---- 正文排版 ---- */
.chapter{scroll-margin-top:64px}
.chapter > h2{font-size:23px;line-height:1.45;margin:44px 0 6px;padding-top:14px;border-top:2px solid var(--line)}
.chapter:first-of-type > h2{border-top:none;margin-top:0;padding-top:0}
h3{font-size:19.5px;margin:30px 0 8px}
h4{font-size:17.5px;margin:22px 0 6px;color:#30363d}
p{margin:12px 0}
p,li,a,code{overflow-wrap:anywhere}
pre code{overflow-wrap:normal}
.chapter-body,.v06-block,.v07-block,.table-wrap{min-width:0;max-width:100%}
ul,ol{margin:12px 0;padding-left:1.7em}
li{margin:5px 0}
blockquote{margin:16px 0;padding:6px 16px;border-left:4px solid var(--line);
  background:var(--soft);color:#3a4249;border-radius:0 6px 6px 0}
code{background:var(--soft);padding:.15em .38em;border-radius:5px;font-size:.9em;
  font-family:"SF Mono",SFMono-Regular,Consolas,"Liberation Mono",Menlo,monospace}
pre{background:var(--soft);border:1px solid var(--line);border-radius:8px;
  padding:14px 16px;overflow-x:auto;line-height:1.6}
pre code{background:none;padding:0;font-size:13.5px}
hr{border:none;border-top:1px solid var(--line);margin:30px 0}

/* ---- 表格横向滚动 ---- */
.table-wrap{overflow-x:auto;margin:16px 0;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.6}
th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
thead th{background:var(--soft);font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:#fcfdfe}

/* ---- 图 ---- */
figure.fig{margin:22px 0;text-align:center}
figure.fig svg.fig-svg{max-width:100%;height:auto;display:block;margin:0 auto;
  background:#fff;border:1px solid var(--line);border-radius:8px}
figure.fig img.fig-img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px}
figure.fig figcaption{font-size:14px;color:var(--muted);margin-top:8px;line-height:1.7;text-align:left}

/* ---- 数学 ---- */
.math-block{display:block;overflow-x:auto;margin:14px 0;text-align:center}
.math-inline{display:inline-block;max-width:100%;overflow-x:auto;vertical-align:middle;white-space:nowrap}
.math-src{font-family:"SF Mono",Consolas,Menlo,monospace;background:var(--soft);
  padding:.1em .35em;border-radius:5px;font-size:.9em;white-space:pre-wrap}

/* ---- 新增块 / 新增图表 ---- */
.v06-block{border-left:3px solid var(--line);background:#f7f8fa;
  padding:2px 18px 6px;border-radius:0 8px 8px 0;margin:22px 0}
.v06-block::before{content:"v0.6 新增（x.9）";display:inline-block;font-size:12px;
  color:var(--muted);background:var(--soft);border-radius:5px;
  padding:1px 8px;margin:12px 0 2px}
.v07-block{border-left:3px solid var(--accent);background:#f7faff;
  padding:2px 18px 6px;border-radius:0 8px 8px 0;margin:22px 0}
.v07-block::before{content:"v0.7 新增（x.10）";display:inline-block;font-size:12px;
  color:var(--accent);background:var(--accent-soft);border-radius:5px;
  padding:1px 8px;margin:12px 0 2px}
.gallery{display:grid;grid-template-columns:1fr;gap:26px}
.gallery-group{margin:26px 0 8px;font-size:15px;color:var(--muted);font-weight:600}
.appendix{border-top:2px solid var(--line);margin-top:52px;padding-top:10px}

@media (max-width:900px){
  #sidebar{transform:translateX(-100%);transition:transform .2s ease;width:80%;max-width:300px}
  body.nav-open #sidebar{transform:none;box-shadow:0 0 40px rgba(0,0,0,.18)}
  #main{margin-left:0}
  .wrap{padding:64px 16px 80px}
  .toolbar{margin:-64px -16px 18px;padding-left:16px;padding-right:16px;padding-top:12px}
  #navToggle{display:block;position:fixed;top:12px;left:12px;z-index:50;
    box-shadow:0 1px 6px rgba(0,0,0,.12)}
}
#navToggle{display:none;border:1px solid var(--line);background:#fff;border-radius:8px;
  padding:7px 12px;font-size:14px;cursor:pointer;margin-right:8px}
@media(max-width:900px){#navToggle{display:block}}
"""

BASE_JS = """
(function(){
  var btn=document.getElementById('modeToggle');
  var nav=document.getElementById('navToggle');
  // 0 = 全书, 1 = 只看 x.10 新增, 2 = 只看全部新增 (x.9+x.10)
  var mode=0;
  function clsFor(mode,cls){
    if(mode===0)return true;
    if(mode===1)return cls.indexOf('v07-block')>=0;
    return cls.indexOf('v06-block')>=0 || cls.indexOf('v07-block')>=0;
  }
  function applyMode(){
    document.body.classList.toggle('only-new', mode===2);
    document.body.classList.toggle('only-v07', mode===1);
    if(btn){btn.textContent = mode===0 ? '只看 x.10 新增内容'
                             : mode===1 ? '只看全部新增（x.9+x.10）'
                                        : '返回全书';}
    document.querySelectorAll('section.chapter').forEach(function(sec){
      var hasV7=sec.querySelector('.v07-block');
      var hasAny=sec.querySelector('.v06-block,.v07-block');
      var show = mode===0 ? true : (mode===1 ? !!hasV7 : !!hasAny);
      sec.style.display = show ? '' : 'none';
    });
    document.querySelectorAll('.chapter-body').forEach(function(b){
      Array.prototype.forEach.call(b.children,function(el){
        var cls=el.className||'';
        var keep = (el.tagName === 'H2' || (el.tagName === 'A' && !!el.id));
        if(!keep){
          if(mode===0)keep=true;
          else keep = clsFor(mode,cls);
        }
        el.style.display = keep ? '' : 'none';
      });
    });
    document.querySelectorAll('[data-onlynew-hide]').forEach(function(el){
      el.style.display = mode===0 ? '' : 'none';
    });
    document.querySelectorAll('[data-v07-only-hide]').forEach(function(el){
      el.style.display = mode===1 ? 'none' : '';
    });
  }
  if(btn){btn.addEventListener('click',function(){mode=(mode+1)%3;applyMode();});}
  if(nav){nav.addEventListener('click',function(){document.body.classList.toggle('nav-open');});}
  document.addEventListener('click',function(ev){
    var link=ev.target.closest('a[href^="#"]');
    if(!link)return;
    var target=document.getElementById(decodeURIComponent(link.getAttribute('href').slice(1)));
    if(target && mode!==0 && target.closest('.appendix')){mode=0;applyMode();}
    if(target)document.body.classList.remove('nav-open');
  });
})();
"""


def mathjax_block(pkg_dir):
    """返回 (html, available)。存在 tex-svg-full.js 则离线内联, 否则注释说明。"""
    candidates = [
        pkg_dir / "book_support_v07" / "assets" / "tex-svg-full.js",
        pkg_dir / "book_support_v06" / "assets" / "tex-svg-full.js",
    ]
    asset = next((c for c in candidates if c.is_file()), candidates[-1])
    config = (
        "<script>window.MathJax={"
        "tex:{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']],processEscapes:true},"
        "svg:{fontCache:'global'},"
        "options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}"
        "};</script>"
    )
    if asset.is_file():
        try:
            js = asset.read_text(encoding="utf-8", errors="replace")
            return config + "\n<script>" + js + "</script>", True
        except Exception as exc:  # noqa: BLE001
            print("[warn] 读取 MathJax 失败 %s: %s" % (asset, exc), file=sys.stderr)
    note = (
        "<!-- MathJax 资源缺失: 未找到 book_support_v07/assets/tex-svg-full.js, "
        "公式保持原始 TeX 源码显示。放入该文件后重新运行即可离线渲染。 -->"
    )
    return note, False


def render_shell(title, header_html, sidebar_html, body_html, mj_html, extra_head=""):
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n" % html_mod.escape(title) +
        "<style>%s</style>\n" % BASE_CSS +
        extra_head +
        "</head>\n<body>\n"
        '<button id="navToggle">目录</button>\n'
        '<nav id="sidebar">%s</nav>\n' % sidebar_html +
        '<div id="main"><div class="wrap">\n'
        "%s\n" % header_html +
        '<div class="toolbar"><button id="modeToggle" class="mode-toggle">只看 x.10 新增内容</button></div>\n'
        "%s\n" % body_html +
        "</div></div>\n"
        "<script>%s</script>\n" % BASE_JS +
        "%s\n" % mj_html +
        "</body>\n</html>\n"
    )


# ----------------------------------------------------------------------------
# 章节 / 附录 读取
# ----------------------------------------------------------------------------

def find_chapters(pkg_dir):
    """返回 [(num, path, title), ...] 按章号排序。"""
    found = {}
    for p in sorted(pkg_dir.glob("第*.md")):
        m = CHAPTER_FILE_RE.match(p.name)
        if not m:
            continue
        num = int(m.group(1))
        if num not in found:
            found[num] = p
    chapters = []
    for num in sorted(found):
        p = found[num]
        title = ""
        try:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("## "):
                    title = line[3:].strip()
                    break
        except Exception:  # noqa: BLE001
            pass
        chapters.append((num, p, title or ("第%d章" % num)))
    return chapters


def build_appendix_map(pkg_dir):
    """返回 {resolved_path_str: anchor_id} 与附录元数据列表。"""
    mapping = {}
    meta = []
    for i, (rel, label) in enumerate(APPENDIX_DOCS, 1):
        p = pkg_dir / rel
        if p.is_file():
            anchor = "apx-%d" % i
            mapping[str(p.resolve())] = "#" + anchor
            meta.append({"anchor": anchor, "label": label, "path": p, "base": p.parent})
    return mapping, meta


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------

def build(pkg_dir, out_dir, markdown):
    chapters = find_chapters(pkg_dir)
    if not chapters:
        sys.exit("在 %s 下未找到分章 Markdown（第XX章*.md）。" % pkg_dir)

    mj_html, mj_available = mathjax_block(pkg_dir)
    appendix_map, appendix_meta = build_appendix_map(pkg_dir)

    fig_registry = []
    figure_caption = {}  # stem -> caption (来自原 md alt)

    # 预扫描: 收集图注 (原 md 图注必须保留)
    for num, path, _title in chapters:
        txt = path.read_text(encoding="utf-8", errors="replace")
        for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", txt):
            stem = Path(src.split("#")[0]).stem
            if stem and alt:
                figure_caption[stem] = alt

    # ---- 渲染每一章 ----
    chapter_pages = []
    overview_sections = []
    for num, path, title in chapters:
        ch_key = "ch%02d" % num
        anchor = "ch-%02d" % num
        raw = path.read_text(encoding="utf-8", errors="replace")
        protected, items = protect_math(raw)
        body = render_markdown(protected, markdown)
        body = restore_math(body, items, mj_available)

        # 先把图 / 表 / 链接 / 脚注全部处理完, 再抽取新增块,
        # 保证速览页里的新增块同样是自包含的 (图已内嵌、链接已重写)。
        body = embed_images(body, path.parent, pkg_dir, fig_registry)
        body = wrap_tables(body)
        body = rewrite_links(body, path.parent, pkg_dir, appendix_map)
        body = scope_footnote_ids(body, ch_key)

        if 'id="%s"' % anchor not in body:
            body = '<a id="%s"></a>\n' % anchor + body

        v06_blocks = extract_v06_blocks(body)
        v07_blocks = extract_v07_blocks(body)
        body = wrap_v06_blocks(body)

        chapter_pages.append(
            '<section class="chapter" data-ch="%02d">\n<div class="chapter-body">\n%s\n</div>\n</section>\n'
            % (num, body)
        )
        if v06_blocks or v07_blocks:
            overview_sections.append((num, title, v06_blocks, v07_blocks))

    # ---- 新增图表画廊 (v0.7 与 v0.6 分组) ----
    def collect_figures(subdir):
        d = pkg_dir / subdir
        by = {}
        if d.is_dir():
            for p in sorted(d.iterdir()):
                if p.suffix.lower() not in (IMG_EXTS | {".svg"}):
                    continue
                cur = by.get(p.stem)
                if cur is None or p.suffix.lower() == ".svg":
                    by[p.stem] = p
        return [by[k] for k in sorted(by)]

    def build_gallery(figs, prefix):
        items = []
        for idx, f in enumerate(figs, 1):
            cap = figure_caption.get(f.stem, "")
            if f.suffix.lower() == ".svg":
                try:
                    inner = inline_svg(f, "%s%d-" % (prefix, idx), cap)
                except Exception as exc:  # noqa: BLE001
                    print("[warn] 画廊 SVG 失败 %s: %s" % (f, exc), file=sys.stderr)
                    continue
            else:
                inner = '<img class="fig-img" alt="%s" src="%s">' % (
                    html_mod.escape(cap, quote=True), data_uri(f))
            items.append(
                '<figure class="fig">%s<figcaption>%s</figcaption></figure>'
                % (inner, html_mod.escape(cap, quote=False))
            )
        return items

    figs_v07 = collect_figures("book_support_v07/figures")
    figs_v06 = collect_figures("book_support_v06/figures")
    gal_v07 = build_gallery(figs_v07, "gal7-")
    gal_v06 = build_gallery(figs_v06, "gal6-")
    new_fig_count = sum(1 for p in (figs_v07 + figs_v06) if p.suffix.lower() == ".svg")
    total_new = len(gal_v07) + len(gal_v06)

    gallery_html = (
        '<section class="chapter appendix" id="sec-newfigures" data-onlynew-hide="1">'
        '<h2>新增图表（v0.7 与 v0.6）</h2>'
        '<p class="meta">共 <b>%d</b> 张新增图（本轮 v0.7 <b>%d</b> 张，v0.6 <b>%d</b> 张）；'
        '图注取自各章原 Markdown，公开结果与计算分列，无新增 GPU/NPU 实测。</p>'
        '<div class="gallery-group">v0.7 新增（x.10，第二轮深化）</div>'
        '<div class="gallery">%s</div>'
        '<div class="gallery-group" data-v07-only-hide="1">v0.6 新增（x.9）</div>'
        '<div class="gallery" data-v07-only-hide="1">%s</div></section>'
        % (total_new, len(gal_v07), len(gal_v06), "\n".join(gal_v07), "\n".join(gal_v06))
    )

    # ---- 附录 ----
    appendix_html_parts = []
    for meta in appendix_meta:
        raw = meta["path"].read_text(encoding="utf-8", errors="replace")
        protected, items = protect_math(raw)
        body = render_markdown(protected, markdown)
        body = restore_math(body, items, mj_available)
        body = embed_images(body, meta["base"], pkg_dir, fig_registry)
        body = wrap_tables(body)
        body = rewrite_links(body, meta["base"], pkg_dir, appendix_map)
        appendix_html_parts.append(
            '<section class="chapter appendix" id="%s" data-onlynew-hide="1">\n'
            '<div class="chapter-body">\n%s\n</div>\n</section>\n' % (meta["anchor"], body)
        )

    # ---- 页头 ----
    header_html = (
        "<header class=\"book\">"
        "<h1>大模型推理系统工程：性能、诊断与优化</h1>"
        "<div class=\"meta\">v0.7 实验深化稿 · 电子书阅读版　|　"
        "共 <b>18</b> 章　|　新增图表 <b>%d</b> 张（v0.7 <b>%d</b> + v0.6 <b>%d</b>）　|　"
        "<b>公开结果</b>与<b>计算</b>分列　|　<b>无新增 GPU/NPU 实测</b></div>"
        "</header>" % (total_new, len(gal_v07), len(gal_v06))
    )

    # ---- 侧栏 ----
    nav_items = ['<div class="grp">章节目录</div>']
    for num, _path, title in chapters:
        nav_items.append(
            '<a class="nav" href="#ch-%02d">%s</a>' % (num, html_mod.escape(title, quote=False)))
    nav_items.append('<div class="grp">图表与附录</div>')
    nav_items.append('<a class="nav" href="#sec-newfigures">新增图表（%d）</a>' % total_new)
    for meta in appendix_meta:
        nav_items.append('<a class="nav" href="#%s">%s</a>' % (meta["anchor"], html_mod.escape(meta["label"])))
    sidebar_html = (
        "<h1>大模型推理系统工程</h1>"
        "<div class=\"sub\">v0.7 阅读版 · 18 章</div>"
        + "".join(nav_items)
    )

    # ---- 电子书阅读版 ----
    full_body = "".join(chapter_pages) + gallery_html + "".join(appendix_html_parts)
    full_html = render_shell(
        "大模型推理系统工程 v0.7 电子书阅读版",
        header_html, sidebar_html, dedupe_ids(full_body), mj_html,
    )

    # ---- 新增图表速览 (只含各章 V07/x.10 新增块) ----
    ov_meta = (
        "<header class=\"book\"><h1>新增图表速览（v0.7）</h1>"
        "<div class=\"meta\">只收录 6 章中各章 <b>x.10</b> 新增块　|　本轮新增图表 <b>%d</b> 张　|　"
        "公开结果、真实/模拟、实测/折算分列　|　无新增 GPU/NPU 实测</div></header>" % len(gal_v07)
    )
    ov_parts = []
    for num, title, _b6, b7 in overview_sections:
        if not b7:
            continue
        ov_parts.append(
            '<section class="chapter" data-ch="%02d">'
            '<h2><a id="ov-%02d"></a>%s</h2>'
            '<div class="chapter-body"><div class="v07-block">%s</div></div></section>'
            % (num, num, html_mod.escape(title, quote=False), "\n".join(b7))
        )
    ov_parts.append(
        '<section class="chapter appendix"><h2><a id="ov-newfigures"></a>新增图表（v0.7）</h2>'
        '<div class="gallery">%s</div></section>' % "\n".join(gal_v07)
    )
    ov_nav = ['<div class="grp">本轮有新增块的章节</div>']
    for num, title, _b6, b7 in overview_sections:
        if not b7:
            continue
        ov_nav.append('<a class="nav" href="#ov-%02d">%s</a>' % (num, html_mod.escape(title, quote=False)))
    ov_nav.append('<a class="nav" href="#ov-newfigures">新增图表（%d）</a>' % len(gal_v07))
    ov_sidebar = (
        "<h1>新增图表速览</h1><div class=\"sub\">v0.7 · 只含 x.10 新增块</div>"
        + "".join(ov_nav)
    )
    # Include source appendices so this standalone overview has valid citations.
    ov_body = "".join(ov_parts) + "".join(appendix_html_parts)
    ov_html = render_shell(
        "大模型推理系统工程 v0.7 新增图表速览",
        ov_meta, ov_sidebar, dedupe_ids(ov_body), mj_html,
    )

    # ---- 写出 ----
    out_full = out_dir / "电子书阅读版_v0.7.html"
    out_ov = out_dir / "新增图表速览_v0.7.html"
    out_full.write_text(full_html, encoding="utf-8")
    out_ov.write_text(ov_html, encoding="utf-8")

    print("章节数: %d" % len(chapters))
    print("内嵌图 (去重后引用): %d" % len(fig_registry))
    print("新增图表: %d (v0.7=%d, v0.6=%d; svg=%d)" % (total_new, len(gal_v07), len(gal_v06), new_fig_count))
    print("MathJax: %s" % ("已离线内联" if mj_available else "缺失，公式保留源码"))
    print("附录: %s" % (", ".join(m["label"] for m in appendix_meta) or "无"))
    print("写出: %s" % out_full)
    print("写出: %s" % out_ov)
    return out_full, out_ov


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="渲染 大模型推理系统工程 v0.7 电子书阅读版 (只读书稿)")
    ap.add_argument("package_dir", help="v0.7 深化包目录 (含 18 个第XX章*.md 与 book_support_v0*)")
    ap.add_argument("--outdir", default=None, help="输出目录, 默认与 package_dir 相同")
    args = ap.parse_args(argv)

    markdown = load_deps()
    pkg_dir = Path(args.package_dir).expanduser().resolve()
    if not pkg_dir.is_dir():
        sys.exit("package_dir 不存在或不是目录: %s" % pkg_dir)
    out_dir = Path(args.outdir).expanduser().resolve() if args.outdir else pkg_dir
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
    build(pkg_dir, out_dir, markdown)


if __name__ == "__main__":
    main()
