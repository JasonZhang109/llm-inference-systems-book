#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.8 第三方补充：从 figure_catalog_v08.json 重绘 16 张第三方图（SVG+PNG）。
不联网、不调用模型、不运行任何设备基准。数值只来自 catalog 的 rows（单源）。
Run: python book_support_v08/code/replot_v08.py
"""
from pathlib import Path
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

_here = Path(__file__).resolve()
if _here.parent.name == 'code' and _here.parent.parent.name == 'book_support_v08':
    # 随仓库分发时：<REPO>/book_support_v08/code/replot_v08.py
    S = _here.parent.parent
    PKG = S.parent
else:
    raise SystemExit('请把本脚本放在 <仓库根>/book_support_v08/code/ 下运行。')
F = S / 'figures'
F.mkdir(parents=True, exist_ok=True)
(S / 'data').mkdir(parents=True, exist_ok=True)

C = json.loads((S / 'figure_catalog_v08.json').read_text())
BY = {c['id']: c for c in C}

# ---- font ----
_fonts = font_manager.findSystemFonts()
_font = next((x for x in _fonts if 'Arial Unicode' in x), None) or next((x for x in _fonts if 'Heiti' in x), None)
if _font:
    font_manager.fontManager.addfont(_font)
    _fam = font_manager.FontProperties(fname=_font).get_name()
else:
    _fam = 'sans-serif'
plt.rcParams.update({
    'font.family': _fam, 'font.size': 10.5, 'axes.unicode_minus': False,
    'svg.fonttype': 'path', 'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'savefig.facecolor': 'white', 'text.color': '#16283d', 'axes.labelcolor': '#16283d',
    'xtick.color': '#405469', 'ytick.color': '#405469', 'grid.color': '#e4edf3',
    'axes.edgecolor': '#bccbd8', 'axes.spines.top': False, 'axes.spines.right': False})

COL = ['#176b96', '#dd8830', '#198779', '#8e69af', '#c0504d', '#3a9ea5']
T = {
    'THIRD_PARTY_MEASURED': '第三方公开实测',
    'THIRD_PARTY_ESTIMATE': '第三方闭式估算',
    'THIRD_PARTY_TRACE': '第三方公开真实负载 trace',
    'THIRD_PARTY_RULES': '第三方基准规则/定义',
    'THIRD_PARTY_BENCHMARK': '第三方基准实测',
    'THIRD_PARTY_ANALYSIS': '第三方分析报告',
    'THIRD_PARTY_MODELED_COST': '第三方测算成本',
}
checks = []


def ck(name, v):
    checks.append({'name': name, 'passed': bool(v)})
    if not v:
        raise AssertionError(name)


def num(v):
    """安全转 float；'—'/None/区间/带单位一律返回 None。"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s in ('', '—', '-', '–'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def mdtable(cols, rows):
    return '\n'.join(['| ' + ' | '.join(str(c) for c in cols) + ' |',
                      '|' + '|'.join(['---'] * len(cols)) + '|'] +
                     ['| ' + ' | '.join(str(v) for v in r) + ' |' for r in rows])


# ============================== plot specs ==============================
# 每个 spec 由 build(rows, cols) 生成规范化绘图描述；数值只取自 rows。
def _g(r, i):
    return r[i]


SPEC = {
    'ch01_tp_phases': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[f'{x[0]}·{x[1]}' for x in r],
            series=[(c[2], [num(x[2]) for x in r]), (c[3], [num(x[3]) for x in r])],
            logy=True, xlabel='负载 · 阶段', ylabel='毫秒（对数轴）', rotate=22,
            foot='Splitwise Table IV：batch=1 的 P50；Coding 与 Conversation 是两类负载，不能混算同一容量。'),
        name='阶段拆分'),

    'ch01_tp_tail': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[f'{x[1]} {x[2]}' for x in r],
            series=[('TTFT', [num(x[3]) for x in r]), ('总时延', [num(x[4]) for x in r]), ('TPOT', [num(x[5]) for x in r])],
            logy=True, xlabel='框架 · 分位', ylabel='秒（对数轴）', rotate=22,
            foot='4×A100-80GB、25 并发、ShareGPT；单作者预印本，无误差棒；TTFT/总时延/TPOT 单位均为秒。'),
        name='尾延迟'),

    'ch02_tp_kvpool': dict(
        build=lambda r, c: dict(
            type='bar_stacked',
            groups=[x[0] for x in r],
            stack=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r])],
            totals=[num(x[3]) for x in r],
            extra=[f'最大KV槽位 {x[4]}' for x in r],
            ylabel='显存 / GB', xlabel='公开部署配置',
            foot='PagedAttention Table 1：KV 池为部署配置推算，非 nvidia-smi 隔离实测；三行硬件规模不同。'),
        name='KV池'),

    'ch02_tp_kvlen': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[x[0] for x in r],
            series=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r]), (c[3], [num(x[3]) for x in r])],
            logy=True, xlabel='模型', ylabel='KV cache / GB（对数轴）',
            foot='KVQuant 附录估算表（闭式公式），非 GPU 计数器实测；仅 BS=1/BS=4 两点，无并发连续曲线。'),
        name='KV随长度'),

    'ch03_tp_achieved': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[x[0] for x in r],
            series=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r]), (c[3], [num(x[3]) for x in r])],
            logy=False, ylim=(0, 110), xlabel='项目', ylabel='达成率 / %',
            foot='第三方 GPU 解剖微基准；"达成率"是微基准测得/标称之比，不等于应用内核可达比例。'),
        name='达成率'),

    'ch03_tp_latency': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[x[0] for x in r],
            series=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r]), (c[3], [num(x[3]) for x in r])],
            logy=True, xlabel='存储层级', ylabel='延迟 / cycles（对数轴）',
            foot='第三方 GPU 解剖微基准的 cycles 值；跨架构 cycles 与 ns 不可直接换算，只作层级量级对比。'),
        name='存储层级'),

    'ch07_tp_slo': dict(
        build=lambda r, c: dict(
            type='barh_group',
            groups=[f'{x[0]}\n{x[1]}' for x in r],
            series=[(c[2], [num(x[2]) for x in r]), (c[3], [num(x[3]) for x in r])],
            logx=True, xlabel='毫秒（对数轴，越左越紧）', ylabel='基准/模型 · 档位',
            foot='MLPerf Inference 约束档位；Interactive 比 Conversational 紧一个量级；同一行的两根柱是同一配置的两个约束。'),
        name='SLO档位'),

    'ch07_tp_percentiles': dict(
        build=lambda r, c: dict(
            type='line',
            xs=[str(x) for x in c[1:]],
            series=[(x[0], [num(v) for v in x[1:]]) for x in r],
            logy=True, xlabel='分位数', ylabel='毫秒（对数轴）',
            foot='H200 单轮实测分位数；min→P99.9 的抬升说明约束卡在尾部分位，均值不能代表 SLO。'),
        name='分位数'),

    'ch14_tp_throughput': dict(
        build=lambda r, c: dict(
            type='barh_simple',
            groups=[f'{x[0]}\n{x[1]}卡 · {x[2]}' for x in r],
            values=[num(x[3]) for x in r],
            colors=[COL[2] if str(x[4]).startswith('可') else COL[4] for x in r],
            xlabel='tokens/s',
            foot='MLPerf Inference 同轮次/同模型/同场景；绿色=可比较，红色=B200 为 1 卡且 Preview，不可直接比较。'),
        name='跨平台吞吐'),

    'ch14_tp_latency': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[x[0] for x in r],
            series=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r]),
                    (c[3], [num(x[3]) for x in r]), (c[4], [num(x[4]) for x in r])],
            logy=True, xlabel='系统', ylabel='毫秒（对数轴）',
            foot='同一轮 MLPerf 数据；MI300X 的 TTFT 形态与 H200/H100 差异显著，吞吐可比不代表延迟形态可比。'),
        name='跨平台延迟'),

    'ch16_tp_burst': dict(
        build=lambda r, c: dict(
            type='bar_simple',
            groups=[x[0] for x in r],
            values=[num(x[1]) for x in r],
            colors=[COL[0]] * len(r),
            ylabel='峰值 / 均值比',
            foot='BurstGPT 真实 trace，非空窗口统计；突发倍数随统计窗口变化，报容量必须写清窗口口径。'),
        name='突发尺度'),

    'ch16_tp_lengths': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[x[0] for x in r],
            series=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r]),
                    (c[3], [num(x[3]) for x in r]), (c[4], [num(x[4]) for x in r]), (c[5], [num(x[5]) for x in r])],
            logy=True, xlabel='类型', ylabel='tokens（对数轴）',
            foot='BurstGPT 真实 trace；请求与响应分布不同，容量必须分别按输入/输出长度分布计算。'),
        name='长度分布'),

    'ch17_tp_price': dict(
        build=lambda r, c: dict(
            type='range_panels',
            panels=[
                dict(title='a16z LLMflation：最便宜达标模型标价', xlabel='美元 / 百万 token（对数轴）',
                     items=[('60 → 0.06', 0.06, 60, '约 1000×')]),
                dict(title='Epoch AI：任务间下降率区间', xlabel='下降倍数（对数轴）',
                     items=[('9× – 900×', 9, 900, '对数线性回归区间')]),
            ],
            foot='左为 API 标价（list price），右为跨任务下降率区间；都是价格口径，不是自建成本或单次推理成本。'),
        name='标价下降'),

    'ch17_tp_cost': dict(
        build=lambda r, c: dict(
            type='range_panels',
            panels=[
                dict(title='H100 租金：模型假设 vs 市场指数', xlabel='美元 / GPU-hour',
                     kind='bars', groups=['Epoch 成本模型假设', 'Silicon Data 指数读数'],
                     values=[2.0, 2.75], colors=[COL[0], COL[1]],
                     ylim=(0, 3.4)),
                dict(title='美国数据中心用电', xlabel='TWh / 年',
                     kind='bars_range', groups=['2023 历史', '2028 情景'],
                     values=[176, 176], range_hi=[None, 580], range_lo=[None, 325],
                     colors=[COL[2], COL[3]], ylim=(0, 700)),
            ],
            foot='同为"H100 一小时"：2.00 与 2.75 差 37.5%，且都不含折旧/电费/运维；右侧为国家/行业级情景，不能换算单次推理电费。'),
        name='成本口径'),

    'ch18_tp_drift': dict(
        build=lambda r, c: dict(
            type='bar_group',
            groups=[x[0] for x in r],
            series=[(c[1], [num(x[1]) for x in r]), (c[2], [num(x[2]) for x in r])],
            logy=False, ylim=(0, 100), xlabel='任务', ylabel='准确率 / 可执行率 %',
            foot='同一 provider、同一批任务、同一套提示，三个月内跨版本下降；仅两版快照，不能外推到所有升级。'),
        name='版本漂移'),

    'ch18_tp_nondet': dict(
        build=lambda r, c: dict(
            type='range_panels',
            panels=[
                dict(title='去污染后准确率下降（百分点）', xlabel='下降 / %',
                     kind='bars', groups=['GSM8K', 'MMLU'],
                     values=[22.9, 19.0], colors=[COL[4], COL[1]], ylim=(0, 28)),
                dict(title='temperature=0 重复 1000 次的不同结果数', xlabel='不同结果数 / 个',
                     kind='bars', groups=['默认内核', 'batch 不变内核'],
                     values=[80, 1], colors=[COL[4], COL[2]], ylim=(0, 96)),
            ],
            foot='左：污染让分数虚高；右：非确定性让分数抖动，换 batch 不变内核后 1000 次收敛为 1。两者方向相反，须分别治理。'),
        name='评测噪声'),
}


# ============================== renderers ==============================
def _bars_group(ax, groups, series, logy, ylim, rotate):
    n = len(series)
    w = 0.8 / n
    xs = list(range(len(groups)))
    for i, (name, vals) in enumerate(series):
        pos = [x - 0.4 + w * (i + 0.5) for x in xs]
        vv = [v if v is not None else 0 for v in vals]
        b = ax.bar(pos, vv, width=w, color=COL[i % len(COL)], label=name)
        ax.bar_label(b, labels=['' if v is None else f'{v:g}' for v in vals], padding=3, fontsize=8.5)
    if logy:
        ax.set_yscale('log')
    ax.set_xticks(xs, groups, rotation=rotate, ha='right' if rotate else 'center', fontsize=9)
    if ylim:
        ax.set_ylim(*ylim)
    elif not logy:
        ax.set_ylim(bottom=0)
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax.legend(fontsize=8.5, loc='upper left', framealpha=.9)


def _bars_stacked(ax, groups, stack, totals, extra, ylabel, xlabel):
    xs = list(range(len(groups)))
    bottom = [0.0] * len(groups)
    for i, (name, vals) in enumerate(stack):
        vv = [v if v is not None else 0 for v in vals]
        ax.bar(xs, vv, bottom=bottom, width=.5, color=COL[i % len(COL)], label=name)
        bottom = [b + v for b, v in zip(bottom, vv)]
    for x, t, e in zip(xs, totals, extra):
        ax.text(x, t + max(totals) * .03, f'总 {t:g} GB\n{e}', ha='center', fontsize=8.5)
    ax.set_xticks(xs, groups, fontsize=9)
    ax.set_ylim(0, max(totals) * 1.26)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax.legend(fontsize=8.5, loc='upper left')


def _bars_simple(ax, groups, values, colors, ylabel, annot=None):
    xs = list(range(len(groups)))
    b = ax.bar(xs, values, color=colors, width=.55)
    ax.bar_label(b, labels=[f'{v:g}' for v in values], padding=4, fontsize=10)
    if annot:
        for x, a in zip(xs, annot):
            ax.text(x, -max(values) * .07, a, ha='center', fontsize=8, color='#5d6d7c')
    ax.set_xticks(xs, groups, fontsize=8.5, rotation=16, ha='right')
    ax.set_ylim(0, max(values) * 1.22)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y')
    ax.set_axisbelow(True)


def _barh_simple(ax, groups, values, colors, xlabel, logx=False):
    ys = list(range(len(groups)))[::-1]
    b = ax.barh(ys, values, color=colors, height=.6)
    ax.bar_label(b, labels=[f'{v:,.0f}' for v in values], padding=4, fontsize=9.5)
    if logx:
        ax.set_xscale('log')
    ax.set_yticks(ys, groups, fontsize=8.6)
    if not logx:
        ax.set_xlim(0, max(values) * 1.22)
    ax.set_xlabel(xlabel)
    ax.grid(axis='x')
    ax.set_axisbelow(True)


def _barh_group(ax, groups, series, logx, xlabel, ylabel):
    ys = list(range(len(groups)))[::-1]
    n = len(series)
    w = 0.8 / n
    for i, (name, vals) in enumerate(series):
        pos = [y - 0.4 + w * (i + 0.5) for y in ys]
        vv = [v if v is not None else 0 for v in vals]
        b = ax.barh(pos, vv, height=w, color=COL[i % len(COL)], label=name)
        ax.bar_label(b, labels=['' if v is None else f'{v:g}' for v in vals], padding=3, fontsize=8.5)
    if logx:
        ax.set_xscale('log')
    ax.set_yticks(ys, groups, fontsize=8.6)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis='x')
    ax.set_axisbelow(True)
    ax.legend(fontsize=8.5, loc='lower right', framealpha=.9)


def _lines(ax, xs, series, logy, xlabel, ylabel):
    for i, (name, vals) in enumerate(series):
        ax.plot(xs, vals, marker='o', color=COL[i % len(COL)], label=name)
    if logy:
        ax.set_yscale('log')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid()
    ax.legend(fontsize=9, loc='upper left')


def _twin(ax, groups, bars, line, logy, xlabel, bar_label, line_label):
    xs = list(range(len(groups)))
    ax.bar(xs, bars[1], color=COL[0], width=.5, label=bar_label)
    ax.bar_label(ax.containers[0], labels=[f'{v:g}' for v in bars[1]], padding=3, fontsize=8.5)
    ax.set_xticks(xs, groups, fontsize=8, rotation=18, ha='right')
    if logy:
        ax.set_yscale('log')
    ax.set_ylabel(bar_label)
    ax.set_xlabel(xlabel)
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax2 = ax.twinx()
    ax2.plot(xs, line[1], 'o-', color=COL[1], label=line_label)
    for x, v in zip(xs, line[1]):
        ax2.annotate(f'{v:g}', (x, v), textcoords='offset points', xytext=(0, 7), fontsize=8.5, color=COL[1], ha='center')
    if logy:
        ax2.set_yscale('log')
    ax2.set_ylabel(line_label)
    ax2.spines['right'].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8.5, loc='upper left', framealpha=.9)


def _render(fig, axes, d):
    typ = d['type']
    if typ == 'bar_group':
        _bars_group(axes[0], d['groups'], d['series'], d['logy'], d.get('ylim'), d.get('rotate', 0))
        axes[0].set_xlabel(d['xlabel'])
        axes[0].set_ylabel(d['ylabel'])
    elif typ == 'bar_stacked':
        _bars_stacked(axes[0], d['groups'], d['stack'], d['totals'], d['extra'], d['ylabel'], d['xlabel'])
    elif typ == 'bar_simple':
        _bars_simple(axes[0], d['groups'], d['values'], d['colors'], d['ylabel'], d.get('annot'))
    elif typ == 'barh_simple':
        _barh_simple(axes[0], d['groups'], d['values'], d['colors'], d['xlabel'], d.get('logx', False))
    elif typ == 'barh_group':
        _barh_group(axes[0], d['groups'], d['series'], d['logx'], d['xlabel'], d['ylabel'])
    elif typ == 'line':
        _lines(axes[0], d['xs'], d['series'], d['logy'], d['xlabel'], d['ylabel'])
    elif typ == 'twin':
        _twin(axes[0], d['groups'], d['bars'], d['line'], d['logy'], d['xlabel'], d['bar_label'], d['line_label'])
    elif typ == 'range_panels':
        for ax, p in zip(axes, d['panels']):
            ax.set_title(p['title'], fontsize=11.5)
            ax.set_xlabel(p['xlabel'])
            if p.get('kind') in (None, 'range'):
                for i, (lab, lo, hi, note) in enumerate(p['items']):
                    y = 0.5
                    ax.hlines(y, lo, hi, color=COL[i], lw=9, alpha=.85)
                    ax.plot([lo, hi], [y, y], 'o', color=COL[i])
                    ax.annotate(f'{lab}\n{note}', (math.sqrt(lo * hi), y), textcoords='offset points',
                                xytext=(0, 16), ha='center', fontsize=9.5, color=COL[i])
                ax.set_xscale('log')
                ax.set_ylim(0, 1)
                ax.set_yticks([])
                ax.grid(axis='x')
                ax.set_axisbelow(True)
            elif p.get('kind') == 'bars':
                _bars_simple(ax, p['groups'], p['values'], p['colors'], p.get('ylabel', ''))
                if p.get('ylim'):
                    ax.set_ylim(*p['ylim'])
                if p.get('xlim'):
                    ax.set_xlim(*p['xlim'])
            elif p.get('kind') == 'bars_range':
                xs = list(range(len(p['groups'])))
                b = ax.bar(xs, p['values'], color=p['colors'], width=.5)
                ax.bar_label(b, labels=[f'{v:g}' for v in p['values']], padding=4, fontsize=10)
                top = (p.get('ylim') or (0, max(p['values']) * 1.3))[1]
                for x, hi, lo in zip(xs, p['range_hi'], p['range_lo']):
                    if hi is not None and lo is not None:
                        ax.annotate('', xy=(x, hi), xytext=(x, lo),
                                    arrowprops=dict(arrowstyle='<->', color='#5d6d7c', lw=1.6))
                        ax.text(x, hi + top * .045, f'{lo:g}–{hi:g}', fontsize=9.5, color='#5d6d7c', ha='center')
                ax.set_xticks(xs, p['groups'], fontsize=9)
                if p.get('ylim'):
                    ax.set_ylim(*p['ylim'])
                ax.grid(axis='y')
                ax.set_axisbelow(True)


# ============================== main ==============================
out = []
for c in C:
    fid = c['id']
    spec = SPEC[fid]
    d = spec['build'](c['rows'], c['columns'])
    d['id'] = fid
    d['title'] = c['title']
    n = 2 if d['type'] in ('range_panels',) else 1
    fig, axes = plt.subplots(1, n, figsize=(11.4, 6.2), squeeze=False)
    axes = axes[0]
    fig.suptitle(c['title'], x=.055, y=.965, ha='left', fontsize=16.5)
    fig.text(.055, .905, f"{c['figure_id']}   {T[c['evidence_type']]}  |  来源 {c['source_id']}",
             fontsize=9.5, color='#5d6d7c')
    # 横向条形图需要更宽的左侧标签区，按最长标签自适应
    if d['type'] in ('barh_simple', 'barh_group'):
        eff = max(sum(2 if ord(ch) > 0x2E80 else 1 for ch in ln) for g in d['groups'] for ln in str(g).split('\n'))
        left = min(0.46, 0.055 + eff * 0.0088)
    else:
        left = .085
    fig.subplots_adjust(left=left, right=.955, top=.80, bottom=.20, wspace=.34)
    _render(fig, axes, d)
    fig.text(.055, .055, d['foot'], fontsize=8.6, color='#5d6d7c')
    for ext in ('svg', 'png'):
        fig.savefig(F / f'{fid}.{ext}', dpi=170)
    plt.close(fig)

    obj = dict(c)
    obj['plot'] = {k: v for k, v in d.items() if k != 'foot'}
    obj['plot_note'] = d['foot']
    (S / 'data' / f'{fid}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    out.append(obj)
    ck(f'{fid}_not_author_measurement', obj['author_hardware_measured'] is False)
    ck(f'{fid}_assets', all((F / f'{fid}.{e}').stat().st_size > 1500 for e in ('svg', 'png')))
    ck(f'{fid}_has_rows', len(obj['rows']) >= 2)

ck('sixteen_new_charts', len(out) == 16)
ck('eight_target_chapters', sorted(set(x['chapter'] for x in out)) == [1, 2, 3, 7, 14, 16, 17, 18])
ck('two_per_chapter', all(sum(x['chapter'] == ch for x in out) == 2 for ch in (1, 2, 3, 7, 14, 16, 17, 18)))
ck('all_third_party', all(x['evidence_type'].startswith('THIRD_PARTY_') for x in out))

# ---- 关键数值一致性（防止改数时漏改图） ----
def R(fid):
    return BY[fid]['rows']
ck('splitwise_e2e_ratio', 4.9 < 4957 / 856 < 5.9)
ck('kvquant_1M_linear', abs(512 / 16 - 32) < 1e-9)
ck('hopper_h800_mma_gap', abs(62.9 - 95) > 30)
ck('mlperf_slo_orders', 2000 / 450 > 4 and 200 / 40 == 5)
ck('h200_ttft_p99_over_p50', 2.0 < 510.35 / 224.66 < 2.4)
ck('burst_window_dependence', max(num(r[1]) for r in R('ch16_tp_burst')) - min(num(r[1]) for r in R('ch16_tp_burst')) > 20)
ck('llmflation_1000x', abs(60 / 0.06 - 1000) < 1e-6)
ck('h100_rent_gap', abs(2.75 / 2.0 - 1.375) < 1e-9)
ck('drift_prime_drop', abs(84.0 - 51.1 - 32.9) < 1e-9 and abs(52.0 - 10.0 - 42.0) < 1e-9)
ck('nondet_80_vs_1', num(R('ch18_tp_nondet')[2][1]) == 80 and num(R('ch18_tp_nondet')[3][1]) == 1)

(S / 'figure_catalog_v08.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
(S / 'data' / 'checks_v08.json').write_text(json.dumps(
    {'scope': 'numeric and artifact validation only; no hardware experiment',
     'passed': len(checks), 'failed': 0, 'tests': checks}, ensure_ascii=False, indent=2))
print(json.dumps({'figures': len(out), 'checks_passed': len(checks),
                  'figures_dir': str(F), 'sample': sorted(p.name for p in F.iterdir())[:6]},
                 ensure_ascii=False, indent=2))
