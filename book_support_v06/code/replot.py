#!/usr/bin/env python3
"""v0.6: reproducible evidence charts. No GPU execution, network, or inferred samples.
Run: python book_support_v06/code/replot.py
Dependencies: matplotlib, numpy. An installed Chinese font is needed; font not bundled.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
ROOT=Path(__file__).resolve().parents[2]
SUP=ROOT/'book_support_v06'; FIG=SUP/'figures'; DATA=SUP/'data'
for p in (FIG,DATA):
    if not p.exists(): p.mkdir(parents=True)
fonts=font_manager.findSystemFonts()
font=next((x for x in fonts if 'Arial Unicode' in x),None)
if font: font_manager.fontManager.addfont(font)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name() if font else 'sans-serif','font.size':11,'axes.titlesize':13,'axes.labelsize':11,'axes.unicode_minus':False,'svg.fonttype':'path','figure.facecolor':'white','axes.facecolor':'white','text.color':'#18293d','axes.labelcolor':'#18293d','xtick.color':'#405166','ytick.color':'#405166','axes.edgecolor':'#bdcbd9','grid.color':'#e6edf3','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
C=['#176b96','#de8c32','#198778','#9163af','#bf5263']
CAT=[]; TEST=[]
TYPE={'TEACHING_CALCULATION':'复算','CONFIG_DERIVED':'官方配置推导','SPEC_DERIVED':'官方规格推导','PUBLISHED_RESULT':'公开结果重绘','PUBLIC_RELATIVE_RESULT':'公开相对结果 · 基线归一化','PUBLIC_FIT_RECONSTRUCTION':'公开拟合重建','DOCUMENTED_COVERAGE':'官方覆盖声明'}
def check(name,ok):
    TEST.append({'name':name,'passed':bool(ok)})
    if not ok: raise AssertionError(name)
def table(headers,rows):
    fmt=lambda v: str(v).replace('|','/')
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(fmt(v) for v in r)+' |' for r in rows])
def canvas(title,typ,source,ncols=1,height=5.5):
    fig,ax=plt.subplots(1,ncols,figsize=(10.8,height),squeeze=False)
    fig.suptitle(title,x=.055,y=.96,ha='left',fontsize=17,fontweight='bold')
    fig.text(.055,.89,TYPE[typ]+'  |  '+source,fontsize=9.5,color='#596b7d')
    fig.subplots_adjust(left=.09,right=.96,top=.79,bottom=.19,wspace=.32)
    return fig,ax[0]
def finish(fig,slug,ch,title,typ,source,conditions,limits,records,headers,rows,formula=None):
    fig.text(.055,.047,limits if len(limits)<94 else limits[:91]+'…',fontsize=8.5,color='#596b7d',wrap=True)
    for ext in ('svg','png'): fig.savefig(FIG/(slug+'.'+ext),dpi=180)
    plt.close(fig)
    obj={'figure_id':f'图{ch}-V{1+sum(x["chapter"]==ch for x in CAT)}','slug':slug,'chapter':ch,'title':title,'evidence_type':typ,'source':source,'conditions':conditions,'limitations':limits,'formula':formula,'author_hardware_measured':False,'records':records,'display_table':table(headers,rows)}
    (DATA/(slug+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
    CAT.append({k:v for k,v in obj.items() if k!='records'})
def bars(ax,labels,values,unit,colors=None):
    b=ax.bar(labels,values,color=colors or C[:len(labels)],width=.58)
    ax.set_ylabel(unit); ax.grid(axis='y'); ax.set_axisbelow(True)
    if min(values)>=0: ax.set_ylim(0,max(values)*1.21)
    ax.bar_label(b,labels=[f'{v:g}' for v in values],padding=5,fontsize=10)
    return b

# 01: existing request example, not a fictional trace.
t='单段优化能把任务缩短多少？'; typ='TEACHING_CALCULATION'
labels=['原始任务','Decode 缩短30%','Decode 理想归零']; v=[6.70,6.70-3.10*.30,6.70-3.10]
f,(a,)=canvas(t,typ,'本书1.1、1.8'); bars(a,labels,v,'任务端到端时间 / s'); a.axhline(3,color=C[4],ls='--',label='目标 3 s'); a.legend()
finish(f,'ch01_task_limit',1,t,typ,'本书1.1、1.8','S7独立预取被覆盖；其余阶段与依赖不变；原始6.70s、Decode3.10s','3.60s是条件化乐观下界，不是设备可达性能。',list(zip(labels,v)),['方案','端到端/s','相对原值减少/%'],[[x,round(y,2),round((1-y/v[0])*100,2)] for x,y in zip(labels,v)],'T=6.70-3.10*r')
check('task_limit_3.60',math.isclose(v[2],3.60))

# 02: configuration-derived KV size.
t='真实模型配置：随上下文增长的逻辑KV状态'; typ='CONFIG_DERIVED'
kv={'Qwen2.5-7B GQA':2*28*4*(3584//28)*2,'DeepSeek-V3 压缩MLA':61*(512+64)*2}
lengths=[4096,8192,16384,32768]; rows=[]; rec=[]
f,(a,)=canvas(t,typ,'X01 / X02；BF16假设')
for i,(model,b) in enumerate(kv.items()):
    vals=[b*s/2**20 for s in lengths]; a.plot(lengths,vals,'o-',color=C[i],label=f'{model} ({b/1024:g} KiB/Token)')
    for s,m in zip(lengths,vals): rows.append([model,s,b/1024,m]);rec.append({'model':model,'length_tokens':s,'bytes_per_token':b,'logical_mib':m})
a.set_xlabel('上下文长度 / Token');a.set_ylabel('逻辑状态 / MiB');a.grid();a.legend(fontsize=9);a.set_ylim(bottom=0)
finish(f,'ch02_config_kv',2,t,typ,'X01 / X02','Qwen:28层/4KV头/头维128；DSV3:61层/(512+64)；全部按2字节存储、单序列、未分片','不是模型优劣比较；不含块对齐、复制、MTP、分配器、工作区或物理显存。',rec,['配置','Token','KiB/Token','MiB'],rows,'GQA=2*L*h_kv*d_head*b; MLA=L*(d_c+d_r)*b')
check('Qwen56KiB',kv['Qwen2.5-7B GQA']==57344);check('DSV3_68.625KiB',kv['DeepSeek-V3 压缩MLA']==70272)

# 03: peak roofline, marked theory.
t='规格给出的只是屋顶：稠密BF16 Roofline';typ='SPEC_DERIVED'
f,(a,)=canvas(t,typ,'X03 / X04；SXM版本'); x=np.logspace(-1,3.5,130); rec=[]; rows=[]
for i,(label,F,B) in enumerate([('A100 80GB SXM',312,2.039),('H100 SXM',1979/2,3.35)]):
    ridge=F/B; y=np.minimum(F,B*x); a.loglog(x,y,color=C[i],label=f'{label}；交点约{ridge:.1f}')
    a.scatter([ridge],[F],color=C[i]);rows.append([label,F,B,round(ridge,2)])
    rec.extend({'device':label,'intensity_flop_per_byte':float(xx),'roof_tflops':float(yy)} for xx,yy in zip(x,y))
a.set_xlabel('算术强度 / FLOP·byte⁻¹'); a.set_ylabel('理想上界 / TFLOP·s⁻¹');a.grid(which='both',alpha=.65);a.legend(fontsize=9)
finish(f,'ch03_spec_roofline',3,t,typ,'X03 / X04','A100 312TFLOP/s与2.039TB/s；H100约989.5TFLOP/s与3.35TB/s；十进制单位','H100官网1979为含稀疏峰值；此图不能解释实机利用率或服务吞吐。',rec,['设备','BF16稠密 TFLOP/s','TB/s','交点 FLOP/byte'],rows,'roof=min(F_peak,B_peak*I)')
check('H100_ridge_295',295<989.5/3.35<296)

# 04: same public workload, metrics on separate scales.
t='FP8 KV并不意味着吞吐翻倍：公开负载对照';typ='PUBLISHED_RESULT'
f,axs=canvas(t,typ,'X05 Table 4；Llama-3.1-8B',ncols=2)
bars(axs[0],['BF16','FP8'],[450.3,517.5],'输出 Token/s');bars(axs[1],['BF16','FP8'],[15.18,12.93],'Median ITL / ms')
rows=[['BF16',763.6,15.18,672.6,450.3],['FP8',742.8,12.93,585.2,517.5]]
finish(f,'ch04_fp8_workload',4,t,typ,'X05 Table 4','150请求、并发8、约20k输入/2k输出、±15%；H100/FA3与v0.19.1由文章上下文给出','吞吐+14.92%是本书复算；没有逐请求数据，不制造P99或误差条。',rows,['KV格式','TTFT中位数/ms','ITL中位数/ms','总时长/s','输出Token/s'],rows)
check('fp8_gain_14.9',14.9<(517.5/450.3-1)*100<15)

# 05: percentages only, preserve normalization.
t='调度策略：均值改善与尾部改善不是一回事';typ='PUBLIC_RELATIVE_RESULT'
f,(a,)=canvas(t,typ,'X08；SGLang v0.5.20 / PR #32911')
x=np.arange(2);a.bar(x-.18,[100,100],.36,color=C[0],label='FCFS基线');bb=a.bar(x+.18,[31,92],.36,color=C[1],label='HRRN');a.bar_label(bb,padding=4);a.set_xticks(x,['Mean TTFT','P99 TTFT']);a.set_ylabel('相对延迟指数（FCFS=100）');a.set_ylim(0,125);a.grid(axis='y');a.set_axisbelow(True);a.legend()
rows=[['Mean TTFT',100,31,'下降69%'],['P99 TTFT',100,92,'下降8%']]
finish(f,'ch05_hrrn_relative',5,t,typ,'X08','GLM-5.2 production trace；同发布说明的HRRN vs FCFS条目；未披露硬件及绝对时间','100是归一化基线，不是100ms；不由两个标量生成延迟分布。',rows,['指标','FCFS指数','HRRN指数','公开降幅'],rows,'normalized=100*(1-reduction)')
check('hrrn_normalized',100*(1-.69)>30.999 and 100*(1-.69)<31.001)

# 06: original rank imbalance example.
t='MoE的瓶颈是最忙rank，不是平均rank';typ='TEACHING_CALCULATION'
vals=[1536,1408,1152,1024,960,896,704,512];f,(a,)=canvas(t,typ,'本书6.5.4；8192次专家指派')
bars(a,[f'rank {i}' for i in range(8)],vals,'Token—专家指派次数',colors=[C[1]]+[C[0]]*7);a.axhline(1024,color=C[2],ls='--',label='均值1024');a.legend()
rows=[[i,n,round(n/1024,3)] for i,n in enumerate(vals)]
finish(f,'ch06_rank_skew',6,t,typ,'本书6.5','4096Token、top-2、8rank；相同单位指派计算成本、无重叠的简化假设','1.5倍偏斜不等于实际端到端慢1.5倍；通信、专家异构及重叠需另测。',rows,['rank','指派数','相对均值'],rows,'skew=max(load)/mean(load)')
check('rank_total_8192',sum(vals)==8192);check('rank_skew_1.5',max(vals)/(sum(vals)/8)==1.5)

# 07: exact set construction proving bounds, not observed frequency.
t='两个95%达标，不保证联合达标95%';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书7.8.1；100个请求的集合构造')
labels=['失败集合不重叠','失败集合完全重叠'];bars(a,labels,[90,95],'联合达标率 / %');a.set_ylim(0,110)
rows=[['不重叠',95,95,90,10],['完全重叠',95,95,95,5]]
finish(f,'ch07_joint_slo',7,t,typ,'本书7.8.1','100个请求；TTFT与TPOT分别95个达标；两种失败集合安排','这是概率界的可达构造，不是对真实服务联合达标率的预测。',rows,['失败集合关系','TTFT通过数','TPOT通过数','联合通过数','至少一项失败数'],rows,'max(0,pA+pB-1)<=P(A∩B)<=min(pA,pB)')
check('joint_bounds',abs(max(0,.95+.95-1)-.9)<1e-9)

# 08: means only; never counterfeit a distribution.
t='三类公开负载：均值已足以提醒不要混为一谈';typ='PUBLISHED_RESULT'
f,(a,)=canvas(t,typ,'X07；OSDI正式版 Figure 7 / 印刷201页')
labels=['ShareGPT','HumanEval','LongBench'];ins=[755.5,171.3,1738.3];outs=[200.3,98.2,90.7];x=np.arange(3)
for off,v,c,lab in [(-.18,ins,C[0],'输入均值'),(.18,outs,C[1],'输出均值')]:
    b=a.bar(x+off,v,.36,color=c,label=lab);a.bar_label(b,padding=4,fontsize=10)
a.set_xticks(x,labels);a.set_ylabel('平均Token数');a.set_ylim(0,2050);a.grid(axis='y');a.set_axisbelow(True);a.legend()
rows=[[l,i,o] for l,i,o in zip(labels,ins,outs)]
finish(f,'ch08_public_lengths',8,t,typ,'X07 Figure 7','OPT评测；LongBench输入被限制到2048；数值为原图图例avg标签；tokenizer未披露','只有边际均值，不是联合分布、样本直方图或现代长上下文数据集全貌。',rows,['论文工作负载','输入均值/Token','输出均值/Token'],rows)

# 09a: reconstruct rounded fit parameters with dashed lines.
t='从公开拟合识别固定开销与随长度增长的成本';typ='PUBLIC_FIT_RECONSTRUCTION'
f,(a,)=canvas(t,typ,'X05 Figure 2；H100 / FA3 / Llama-3.1-8B')
lengths=list(range(256,125001,512));rec=[]
for lab,slope,inter,c in [('BF16',4.37e-5,6.44,C[0]),('FP8',2.37e-5,6.58,C[1])]:
    ys=[inter+slope*s for s in lengths];a.plot(lengths,ys,'--',color=c,label=lab+'（拟合重建）')
    rec.extend({'kv':lab,'length_tokens':s,'predicted_itl_ms':y,'measured':False} for s,y in zip(lengths,ys))
a.axvline(7000,color=C[2],ls=':',label='舍入参数交点约7000');a.set_xlabel('输入长度 / Token');a.set_ylabel('拟合ITL / ms');a.grid();a.legend(fontsize=9)
rows=[['BF16',4.37e-5,6.44],['FP8',2.37e-5,6.58]]
finish(f,'ch09_public_fit',9,t,typ,'X05 Figure 2 / Table 3','单H100、FA3、并发1、输出128、输入256到125k；采用文中舍入斜率和截距','虚线非原始点；舍入参数给约7000Token，原表精确交点7010，两者不强行等同。',rec,['格式','斜率/ms每Token','截距/ms'],rows,'ITL=slope*input_len+intercept')
check('rounded_fit_crossover',abs((6.58-6.44)/(4.37e-5-2.37e-5)-7000)<1e-7)
# 09b: sampling.
t='只采样1%，会漏掉多少罕见异常？';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书9.2、9.8；固定30个异常请求')
p=np.linspace(0,.2,101); ys=100*(1-(1-p)**30);a.plot(p*100,ys,color=C[0]);a.scatter([1],[100*(1-.99**30)],color=C[1]);a.annotate('1%采样 → 约26.03%捕获概率',(1,26.03),xytext=(3,12),arrowprops={'arrowstyle':'->','color':C[1]},fontsize=10)
a.set_xlabel('每请求独立采样概率 / %');a.set_ylabel('至少捕获一次异常 / %');a.set_ylim(0,105);a.grid()
rows=[[r,round(100*(1-(1-r/100)**30),3)] for r in [1,2,5,10,20]]
finish(f,'ch09_sampling',9,t,typ,'本书9.2、9.8','窗口内恰有30个异常请求；每次独立伯努利采样；采样不依赖异常','真实请求/采样若相关，公式不成立；此图不是采样工具实测。',[{'sample_percent':float(x*100),'capture_percent':float(y)} for x,y in zip(p,ys)],['采样概率/%','至少捕获一次/%'],rows,'P=1-(1-p)^30')
check('sampling26',26<100*(1-.99**30)<26.1)

# 10: two by two factorial values from the book.
t='四格交叉对照：版本效应会随长度改变';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书10.8.1；不是补造的升级观测')
a.plot([1250,1650],[620,780],'o-',color=C[0],label='版本A');a.plot([1250,1650],[660,900],'o-',color=C[1],label='版本B');a.set_xticks([1250,1650]);a.set_xlabel('固定输入长度 / Token');a.set_ylabel('TTFT / ms');a.grid();a.legend()
for x,y in [(1250,620),(1650,780),(1250,660),(1650,900)]:a.annotate(str(y),(x,y),xytext=(5,6),textcoords='offset points')
rows=[['A',620,780,160],['B',660,900,240],['B−A',40,120,80]]
finish(f,'ch10_factorial',10,t,typ,'本书10.8.1','四格数据均为原稿设定；每格待以匹配负载、多次运行替换','80ms是差中之差，不是统计显著性；没有原始重复记录，不计算置信区间。',rows,['版本','1250Token/ms','1650Token/ms','长度增量/ms'],rows,'interaction=(900-660)-(780-620)=80ms')
check('interaction80',(900-660)-(780-620)==80)

# 10b: a public version effect with both endpoints disclosed.
t='版本变化会移动FP8的收益交点';typ='PUBLISHED_RESULT'
f,(a,)=canvas(t,typ,'X05 Table 3；Llama-3.1-8B / H100')
rows=[['v0.10.2',24889,63],['v0.19.1',7010,54]]
bars(a,[r[0] for r in rows],[r[1] for r in rows],'两条ITL曲线相等时的输入长度 / Token')
finish(f,'ch10_version_breakeven',10,t,typ,'X05 Table 3','Llama-3.1-8B；H100/FA3单请求上下文；before与after比较；交点由原文拟合得到','是整版本比较，不可把全部收益归因于单个开关；交点不是最大可用上下文。',rows,['版本','公开拟合交点/Token','FP8斜率为BF16的/%'],rows)
check('breakeven_shift_positive',24889>7010)

# 11a: exact EAGLE table 4, do not mix batch64.
t='推测解码的公开单请求生成速率';typ='PUBLISHED_RESULT'
f,(a,)=canvas(t,typ,'X06 Table 4；SGLang / 1×H100 / MT-Bench')
labels=['无推测','EAGLE-2','EAGLE-3'];v=[158.34,244.10,373.25];bars(a,labels,v,'单请求生成速率 / Token/s')
rows=[[l,x,round(x/v[0],4)] for l,x in zip(labels,v)]
finish(f,'ch11_eagle',11,t,typ,'X06 Table 4','LLaMA-Instruct 3.1 8B；SGLang团队实验；batch size=1；同一H100','原表标题Latency但单位Token/s；不把此单请求速率当并发服务容量，未给误差条。',rows,['方法','Token/s','相对基线/倍'],rows)
check('eagle_2.357',2.35<373.25/158.34<2.36)
# 11b: hybrid context precise table.
t='混合注意力：有选择地量化比一刀切更合理';typ='PUBLISHED_RESULT'
f,axs=canvas(t,typ,'X05 Table 5；gpt-oss-20b',ncols=2)
lab=['BF16','FP8','FP8\nskip-SW'];bars(axs[0],lab,[831.6,853,871.8],'输出Token/s');bars(axs[1],lab,[8.09,7.90,7.70],'Median ITL / ms')
rows=[['BF16',468.9,8.09,364.2,831.6],['FP8',451.7,7.90,355.1,853.0],['FP8 skip-SW',456.4,7.70,347.4,871.8]]
finish(f,'ch11_hybrid_fp8',11,t,typ,'X05 Table 5','150请求、并发8、约20k输入/2k输出±15%；H100/FA3上下文；skip-SW保留滑窗层BF16','这不是Llama的数据；不得把两个模型的柱高比较解释成优化优劣。',rows,['KV策略','TTFT中位数/ms','ITL中位数/ms','总时长/s','输出Token/s'],rows)
# 11c: negative outcome and correction, identity limits.
t='质量回归：更低精度并不自动保持正确性';typ='PUBLISHED_RESULT'
f,(a,)=canvas(t,typ,'X05 Figure 1；Hopper / 128k needle-in-a-haystack')
rows=[['BF16基线',91],['FP8修复前',13],['FP8修复后',89]];bars(a,[x[0] for x in rows],[x[1] for x in rows],'准确率 / %',colors=[C[0],C[4],C[2]]);a.set_ylim(0,105)
finish(f,'ch11_quality_failure',11,t,typ,'X05 Figure 1','Hopper、FA3 FP8长上下文路径；两级累加修复；具体模型、样本数未披露','91→13→89是不同配置的公开结果，不是时间序列；89不能证明与91统计等价。',rows,['配置','公开准确率/%'],rows)
check('quality_loss78',91-13==78)

# 12a: explicit theoretical link-only floor.
t='状态转移：带宽足够才有讨论分离的前提';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书12.5、12.6；512MiB状态')
bws=[.5,3,20];times=[512*2**20/(b*1e9)*1000 for b in bws];bars(a,[f'{b:g} GB/s' for b in bws],times,'仅payload传输时间 / ms');a.axhline(285,color=C[4],ls='--',label='重算285ms');a.legend()
rows=[[b,round(t,3),round(285/t,3)] for b,t in zip(bws,times)]
finish(f,'ch12_transfer_floor',12,t,typ,'本书12.5、12.6','S=512MiB=536870912byte；带宽0.5/3/20GB/s均为假设；重算285ms','仅payload理想时间，不含排队、序列化、注册、复制和重传；不代表真实链路。',rows,['有效带宽假设/GB每秒','理想payload/ms','285ms与传输时间之比'],rows,'T_ms=S_bytes/(B_GBs*10^9)*1000')
check('transfer20_26.84',26.84<times[-1]<26.85)
# 12b: numerical SLO contract, not outcome.
t='同一论文，不同任务采用不同服务目标';typ='PUBLISHED_RESULT'
f,axs=canvas(t,typ,'X07 Table 1；OSDI正式版服务目标',ncols=2)
labels=['对话13B','对话66B','对话175B','代码66B','摘要66B'];tt=[250,2500,4000,125,15000];tp=[100,150,200,200,150]
for a,vs,title in zip(axs,[tt,tp],['TTFT门槛 / ms','TPOT门槛 / ms']):
    a.barh(labels,vs,color=C[0] if a is axs[0] else C[1]);a.invert_yaxis();a.set_xlabel(title);a.set_xlim(0,max(vs)*1.25);a.grid(axis='x');a.set_axisbelow(True)
    for i,v in enumerate(vs):a.text(v+max(vs)*.02,i,f'{v:g}',va='center',fontsize=9)
rows=[[l,x,y] for l,x,y in zip(labels,tt,tp)]
finish(f,'ch12_slo_contract',12,t,typ,'X07 Table 1','OPT-13B/66B/175B；FP16；论文全局测试床4节点32×A100-80GB；不同实验使用相应子集','图中是门槛不是测得的延迟；不混用arXiv v2的0.2/0.4s聊天TTFT。',rows,['任务/模型','TTFT门槛/ms','TPOT门槛/ms'],rows)

# 13: preserve only declared combinations, no cross-product inference.
t='官方验证过哪些组合？空白不等于不支持';typ='DOCUMENTED_COVERAGE'
f,(a,)=canvas(t,typ,'X09 Models；v0.26.0rc1固定提交')
models=['GLM-5.2 · W8A8C8','Kimi K3 · W4A8','DeepSeek-V4-Flash · W8A8C8','DeepSeek-V4-Pro · W8A8C8'];cells=[['4节点 EP / 1P1D','未声明'],['8节点 EP / 1P1D','4节点 EP / 1P1D'],['4节点 DP / 1P1D','未声明'],['2节点 EP / 1P1D','未声明']]
a.imshow([[1,0],[1,1],[1,0],[1,0]],cmap=ListedColormap(['#eff3f7','#d8eef5']),vmin=0,vmax=1,aspect='auto');a.set_xticks([0,1],['A3','Ascend 950']);a.set_yticks(range(4),models,fontsize=9)
for i,row in enumerate(cells):
    for j,val in enumerate(row):a.text(j,i,val,ha='center',va='center',fontsize=10,color='#18293d')
f.subplots_adjust(left=.35)
rows=[[m,*r] for m,r in zip(models,cells)]
finish(f,'ch13_declared_matrix',13,t,typ,'X09 Models','仅保留报告列出的模型、精度、节点数、EP/DP和1P1D组合','未声明≠不支持；蓝格也不代表本书已验证；不得展开为任意功能笛卡尔积。',rows,['模型/量化','A3部署','Ascend950部署'],rows)

# 14: pre-existing pedagogical example.
t='约束匹配轨与平台优化轨，结论可以反向';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书14.4.1；A/B为匿名配置')
x=np.arange(2)
for off,v,c,lab in [(-.18,[5.20,5.80],C[0],'平台A'),(.18,[4.60,6.10],C[1],'平台B')]:
    b=a.bar(x+off,v,.36,color=c,label=lab);a.bar_label(b,padding=4)
a.set_xticks(x,['约束匹配轨','平台优化轨']);a.set_ylabel('合格完成速率 / req/s');a.set_ylim(0,7.3);a.grid(axis='y');a.set_axisbelow(True);a.legend()
rows=[['约束匹配轨',5.20,4.60,'A较B高13.04%'],['平台优化轨',5.80,6.10,'B较A高5.17%']]
finish(f,'ch14_two_tracks',14,t,typ,'本书14.4.1；X12只支持比较纪律','数字沿用原稿；轨道内需相同质量/SLO/负载；不混用卡、节点、资源池边界','不能映射为任何真实厂商排名；调参预算、精度、功耗和软件差异均需披露。',rows,['轨道','A req/s','B req/s','该轨道结论'],rows)

# 15: incompatible score scales separated.
t='国产推理栈公开质量数据：先保留量表，再谈结论';typ='PUBLISHED_RESULT'
f,axs=canvas(t,typ,'X09 Accuracy；v0.26.0rc1；图中DS = DeepSeek',ncols=2,height=6)
lab=['GLM-5.2','Kimi K3','DS-V4-Flash','DS-V4-Pro'];vals=[92.165,92.42,91.67,91.92]
bars(axs[0],lab,vals,'GPQA 报告Score');axs[0].tick_params(axis='x',labelrotation=24,labelsize=8);axs[0].set_ylim(0,110)
bars(axs[1],['Kimi K3'],[.88],'OCRBench 报告Score');axs[1].set_ylim(0,1.05)
rows=[['GPQA',l,v] for l,v in zip(['GLM-5.2','Kimi K3','DeepSeek-V4-Flash','DeepSeek-V4-Pro'],vals)]+[['OCRBench','Kimi K3',.88]]
finish(f,'ch15_quality_scales',15,t,typ,'X09 Accuracy','报告4模型GPQA与1模型OCRBench原值；对应部署见图13-V1；量表分开','报告未给GPQA子集/题数及逐样本数据；保留Score，不由0.88反推880个正确，也不做显著排名。',rows,['基准','模型','报告Score'],rows)

# 16: explicit fluid queue, no service trace claimed.
t='一次60秒突发，会留下180秒恢复尾巴';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书16.8.2；流体队列模型')
ts=list(range(0,301));qs=[15*t if t<=60 else max(900-5*(t-60),0) for t in ts];a.plot(ts,qs,color=C[0]);a.fill_between(ts,qs,color='#e0edf5');a.axvline(60,color=C[1],ls='--');a.axvline(240,color=C[2],ls='--');a.annotate('峰值900个积压',(60,900),xytext=(100,790),arrowprops={'arrowstyle':'->','color':C[1]});a.set_xlabel('自突发开始 / s');a.set_ylabel('积压请求数');a.set_ylim(0,1040);a.grid()
rows=[[0,0,40,25],[60,900,20,25],[120,600,20,25],[180,300,20,25],[240,0,20,25]]
finish(f,'ch16_backlog',16,t,typ,'本书16.8.2；X11仅支撑控制器语义','服务25req/s；0—60s到达40，其后20；无取消、拒绝、重试，初始积压0','与16.3.1的620/340s属于不同模型；不作为生产恢复时长保证。',[{'t_s':t,'backlog_requests':q} for t,q in zip(ts,qs)],['时点/s','积压','该时点后到达率/req每秒','服务率/req每秒'],rows,'Qpeak=(40-25)*60=900; recovery=900/(25-20)=180s')
check('backlog_peak',max(qs)==900);check('backlog_clear240',qs[240]==0 and qs[239]>0)

# 17: conditional economics, not market quotes.
t='技术收益要扣掉维护，才是回本曲线';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书17.5、17.8；非市场报价')
months=np.linspace(0,12,49);rec=[];rows=[]
for i,maint in enumerate([8000,24000]):
    ys=-36000+(122640-maint)*months/12;pb=36000/(122640-maint)*12;a.plot(months,ys/10000,color=C[i],label=f'维护{maint/10000:g}万元/年；回本{pb:.2f}月');a.scatter([pb],[0],color=C[i]);rows.append([maint,122640-maint,round(pb,3),122640-maint-36000]);rec.extend({'maintenance_cny_year':maint,'month':float(m),'cumulative_net_cny':float(y)} for m,y in zip(months,ys))
a.axhline(0,color='#687b8d',ls='--');a.set_xlabel('月份');a.set_ylabel('累计净收益 / 万元');a.grid();a.legend(fontsize=9)
finish(f,'ch17_payback',17,t,typ,'本书17.5、17.8','年毛节省122640元、一次投入36000元；维护8000/24000元；均匀发生、未折现','经济模型，不代表当前采购、电价、云价格或必能兑现的现金节省。',rec,['年维护/元','年净持续节省/元','简单回本/月','首年净收益/元'],rows,'cash=-36000+(122640-maintenance)*month/12')
check('payback3.77',3.76<36000/114640*12<3.78);check('first_year78640',122640-8000-36000==78640)

# 18: useful E0 regression-gate calculation.
t='回归指标越多，误报至少一次的概率越高';typ='TEACHING_CALCULATION'
f,(a,)=canvas(t,typ,'本书18.8；独立真零假设示例')
ks=list(range(1,61));ys=[100*(1-.95**k) for k in ks];bon=[100*(1-(1-.05/k)**k) for k in ks];a.plot(ks,ys,color=C[4],label='每项α=0.05');a.plot(ks,bon,color=C[2],label='每项α=0.05/m（独立例）');a.set_xlabel('独立检验指标数量 m');a.set_ylabel('至少一次假阳性 / %');a.set_ylim(0,105);a.grid();a.legend(fontsize=9)
rows=[[k,round(100*(1-.95**k),3),round(100*(1-(1-.05/k)**k),3)] for k in [1,5,10,20,50]]
finish(f,'ch18_multiple_tests',18,t,typ,'本书18.8；概率复算','所有零假设为真；独立检验时画精确族错误率；Bonferroni的≤5%保证不要求独立','回归指标往往相关，红线不是实测误报率；统计显著也不能替代业务阈值。',[{'m':k,'unadjusted_percent':y,'bonferroni_independent_percent':b} for k,y,b in zip(ks,ys,bon)],['指标数','未校正至少一次/%','Bonferroni独立例/%'],rows,'FWER=1-(1-alpha)^m')
check('FWER20_64.15',64.15<100*(1-.95**20)<64.16)

# Structural and numerical validation.
check('18_chapters',set(c['chapter'] for c in CAT)==set(range(1,19)))
check('23_figures',len(CAT)==23)
for c in CAT:
    check(c['slug']+'_assets',all((FIG/(c['slug']+'.'+e)).stat().st_size>1000 for e in ('svg','png')))
    check(c['slug']+'_not_hardware',c['author_hardware_measured'] is False)
(SUP/'figure_catalog_v06.json').write_text(json.dumps(CAT,ensure_ascii=False,indent=2))
(SUP/'data/calculation_checks_v06.json').write_text(json.dumps({'scope':'E0 arithmetic and artifact structure only; no hardware experiments','tests':TEST,'passed':sum(x['passed'] for x in TEST),'failed':sum(not x['passed'] for x in TEST)},ensure_ascii=False,indent=2))
print(json.dumps({'figures':len(CAT),'chapters':18,'checks_passed':sum(x['passed'] for x in TEST),'checks_failed':sum(not x['passed'] for x in TEST)},ensure_ascii=False))
