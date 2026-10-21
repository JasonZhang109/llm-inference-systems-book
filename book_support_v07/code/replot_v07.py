#!/usr/bin/env python3
"""Offline redraw from curated public records. Does not execute model benchmarks.
Run from any directory: python book_support_v07/code/replot_v07.py
Requires matplotlib, numpy, and an installed Chinese font (not distributed).
"""
from pathlib import Path
import json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
P=Path(__file__).resolve().parents[2]; S=P/'book_support_v07'; F=S/'figures'
D=json.loads((S/'data/curated_datasets_v07.json').read_text())
fonts=font_manager.findSystemFonts(); font=next((x for x in fonts if 'Arial Unicode' in x),None)
if font:font_manager.fontManager.addfont(font)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name() if font else 'sans-serif','font.size':10.5,'axes.unicode_minus':False,'svg.fonttype':'path','figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','text.color':'#16283d','axes.labelcolor':'#16283d','xtick.color':'#405469','ytick.color':'#405469','grid.color':'#e4edf3','axes.edgecolor':'#bccbd8','axes.spines.top':False,'axes.spines.right':False})
COL=['#176b96','#dd8830','#198779','#8e69af']
T={'PUBLISHED_EXPERIMENT':'公开实验数值','PUBLISHED_MICROBENCHMARK':'公开微基准 · 非完整服务','PUBLISHED_REAL_AND_SIMULATED':'公开真实系统与模拟器对照','PUBLISHED_STAGE_EXPERIMENT':'公开阶段实验 · 非端到端','PUBLISHED_ACCEPTANCE_ADJUSTED':'官方接受率折算'}
checks=[]
def ck(name,v):
    checks.append({'name':name,'passed':bool(v)})
    if not v:raise AssertionError(name)
def mdtable(cols,rows):
    return '\n'.join(['| '+' | '.join(cols)+' |','|'+'|'.join(['---']*len(cols))+'|']+['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
cat=[]
for d in D:
    pl=d['plot']; rows=d['rows'];typ=pl['type'];multi=typ in ['panels','simulation_panels'];n=2 if multi else 1
    fig,axes=plt.subplots(1,n,figsize=(11,6.1),squeeze=False);axes=axes[0]
    fig.suptitle(d['title'],x=.055,y=.965,ha='left',fontsize=17)
    fig.text(.055,.90,T[d['evidence_type']]+'  |  '+d['source_id']+'',fontsize=10,color='#5d6d7c')
    fig.subplots_adjust(left=.09,right=.96,top=.78,bottom=.23,wspace=.31)
    x=[r[pl['x']] for r in rows]
    if typ=='lines':
        ax=axes[0]
        for i,ycol in enumerate(pl['ys']):
            y=[r[ycol] for r in rows];lab=d['columns'][ycol].replace('、卡均',' / ').replace('/输出Token每秒','')
            if 'ch06' in d['id']:lab=lab.split('/')[0]
            ax.plot(x,y,marker='o',linestyle='--' if pl.get('derived') else '-',color=COL[i],label=lab)
        if pl.get('logx'):ax.set_xscale('log',base=2);ax.set_xticks(x,[str(v) for v in x])
        else:ax.set_xticks(x)
        if pl.get('ylim'):ax.set_ylim(pl['ylim'])
        else:ax.set_ylim(bottom=0)
        ax.set_xlabel(pl['xlabel']);ax.set_ylabel(pl['ylabel']);ax.grid();ax.legend(fontsize=9,loc='upper left')
    elif typ=='bars':
        ax=axes[0];y=[r[pl['y']] for r in rows];b=ax.bar(x,y,color=COL[:len(x)],width=.54);ax.bar_label(b,padding=5,fontsize=11);ax.set_ylabel(pl['ylabel']);ax.set_ylim(0,max(y)*1.2);ax.grid(axis='y');ax.set_axisbelow(True)
    elif typ=='panels':
        for i,(ax,yc) in enumerate(zip(axes,pl['ys'])):
            y=[r[yc] for r in rows];b=ax.bar(x,y,color=COL[i],width=.62);ax.bar_label(b,padding=5,fontsize=10);ax.set_ylim(0,max(y)*1.23);ax.grid(axis='y');ax.set_axisbelow(True);ax.set_ylabel(pl.get('panel_ylabels',[pl.get('ylabel','')]*2)[i]);ax.tick_params(axis='x',labelrotation=20 if len(x)>3 else 0,labelsize=9)
            if d['id']=='ch05_pa_batching':ax.set_title(['ShareGPT · 2 req/s','Alpaca · 30 req/s'][i],fontsize=12)
    elif typ=='simulation_panels':
        for i,(ax,pair) in enumerate(zip(axes,pl['pairs'])):
            ax.plot(x,[r[pair[0]] for r in rows],'o-',color=COL[i],label='真实系统')
            ax.plot(x,[r[pair[1]] for r in rows],'s--',color='#737d89',label='论文模拟器',markersize=4)
            ax.set_title(['vLLM','DistServe-Low'][i],fontsize=12);ax.axhline(90,color='#b1bcc7',ls=':',lw=1);ax.set_ylim(0,110);ax.set_xticks(x);ax.grid();ax.set_xlabel(pl['xlabel']);ax.set_ylabel(pl['ylabel']);ax.legend(fontsize=9,loc='lower left')
    # concise chart-contained boundary, full condition remains in JSON and book caption
    foot={'ch04_pa_sharing':'同一生成方式内比较；KV共享节省不是整卡总显存节省。',
    'ch04_lmcache_load':'400 Gbps = 50 GB/s；加载阶段倍率不等于端到端推理倍率。',
    'ch05_pa_batching':'纵轴是平均组批请求数，不是吞吐；两种负载到达率不同。',
    'ch06_deepep_latency':'每rank128Token；固定历史提交3b1045db43ed；各EP点专家总数未披露。',
    'ch06_nvlink_batch':'GB200 NVL72 / EP8 / BF16 / perfect router；折线只连接已有表值。',
    'ch06_nvlink_ep':'每rank2048Token；EP增大全局Token总量也增大，不是固定任务强扩展。',
    'ch11_dispatch_precision':'仅dispatch；量化质量与完整迭代未验；EP/硬件为章节上下文，详见正文边界。',
    'ch12_distserve_calibration':'表2未单列模型、负载、每行用卡数；只验证公开校准结果，不推卡均容量。',
    'ch15_ascend_prefill':'16卡Prefill阶段；输入吞吐不等于输出吞吐，也不能直接算PD端到端容量。',
    'ch15_ascend_mtp':'虚线为报告接受率折算值；不是六次独立实测，不与Prefill吞吐相加。'}[d['id']]
    fig.text(.055,.075,foot,fontsize=9,color='#5d6d7c')
    for ext in ['svg','png']:fig.savefig(F/(d['id']+'.'+ext),dpi=180)
    plt.close(fig)
    obj=dict(d);obj.update(figure_id=f'图{d["chapter"]}-E{1+sum(c["chapter"]==d["chapter"] for c in cat)}',display_table=mdtable(d['columns'],rows))
    (S/'data'/(d['id']+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
    cat.append(obj)
    ck(d['id']+'_not_author_measurement',obj['author_hardware_measured'] is False)
    ck(d['id']+'_assets',all((F/(d['id']+'.'+e)).stat().st_size>1000 for e in ['svg','png']))
ck('ten_new_charts',len(cat)==10)
ck('six_target_chapters',set(d['chapter'] for d in D)=={4,5,6,11,12,15})
ck('Gbps_to_GBs',400/8==50 and 88/8==11)
ck('load_ratio',4.54<400/88<4.55)
ck('pa_sharegpt_batch_ratio',2.23<30.42/13.62<2.24)
ck('pa_alpaca_batch_ratio',1.82<132.44/72.75<1.83)
ck('nvfp4_payload',4032/14336==.28125)
ck('dispatch_speedup',3.06<311.8/101.7<3.07)
ck('phase_prefill_not_decode',next(d for d in D if d['id']=='ch15_ascend_prefill')['evidence_type']=='PUBLISHED_STAGE_EXPERIMENT')
ck('mtp_folded_not_measured',next(d for d in D if d['id']=='ch15_ascend_mtp')['evidence_type']=='PUBLISHED_ACCEPTANCE_ADJUSTED')
r=next(d for d in D if d['id']=='ch12_distserve_calibration')['rows'];e1=max(abs(r[1]-r[2]) for r in r);e2=max(abs(r[3]-r[4]) for r in r)
ck('simulation_max_error_pp',abs(e1-1.8)<1e-9 and abs(e2-1.1)<1e-9)
(S/'figure_catalog_v07.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2))
(S/'data/checks_v07.json').write_text(json.dumps({'scope':'numeric and artifact validation only; no hardware experiment','passed':len(checks),'failed':0,'tests':checks},ensure_ascii=False,indent=2))
print({'new_figures':len(cat),'checks_passed':len(checks)})
