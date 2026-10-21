#!/usr/bin/env python3
"""Rebuild all numerical figures from explicit source values or E0 formulas.
Requires matplotlib; no network calls. Output contains no measured local GPU data.
"""
from pathlib import Path
import csv, json, math, platform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from e0_reference import dag_finish, make_tp_rows, mg1_wait, progress, quantile, replicas

BASE=Path(__file__).resolve().parents[1]
FIG=BASE/'figures'; DATA=BASE/'data'
FIG.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)
# Use a locally available font; no font files are copied into the deliverable.
for name in ['Noto Sans CJK SC','Noto Sans CJK JP','Microsoft YaHei','SimHei','Arial Unicode MS']:
    if any(f.name==name for f in font_manager.fontManager.ttflist):
        plt.rcParams['font.family']=name;break
plt.rcParams['axes.unicode_minus']=False
plt.rcParams['font.size']=11
CAT=[]

def new(title, ylabel=None, xlabel=None, size=(10,6)):
    fig,ax=plt.subplots(figsize=size)
    ax.set_title(title,pad=18,fontsize=15)
    if ylabel: ax.set_ylabel(ylabel)
    if xlabel: ax.set_xlabel(xlabel)
    return fig,ax

def save(fig,ax,name,rows,note,kind,source):
    fig.subplots_adjust(bottom=.23,top=.83,left=.13,right=.96)
    fig.text(.06,.06,note,fontsize=10,va='bottom',wrap=True)
    for extension in ['png','svg']:
        fig.savefig(FIG/f'{name}.{extension}',dpi=180)
    plt.close(fig)
    if rows:
        with (DATA/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    CAT.append(dict(id=name,figure=f'figures/{name}.png',svg=f'figures/{name}.svg',data=f'data/{name}.csv',
                    provenance=kind,source=source,author_hardware_measured=False,caption=note))

def labelbars(ax,bars):
    ax.bar_label(bars,fmt='%g',padding=4)
    ax.margins(y=.18)

nodes={'S1':(.08,[]),'S2':(.35,['S1']),'S3':(.9,['S2']),'S4':(.6,['S3']),
       'S5':(1.2,['S4']),'S6':(3.1,['S5']),'S7':(.45,['S2']),
       'S8':(.12,['S6','S7']),'S9':(.35,['S8'])}
ends=dag_finish(nodes)
labels=['S1 鉴权','S2 解析','S3 检索','S4 重排','S5 Prefill','S6 Decode','S7 独立工具','S8 组装','S9 渲染']
fig,ax=new('图1-R1 依赖图决定6.70秒，而不是九段盲目相加',xlabel='任务起点后的时间（秒）',size=(11,7))
rows=[]
for idx,(name,(duration,deps)) in enumerate(nodes.items()):
    start=ends[name]-duration
    ax.barh(idx,duration,left=start,height=.6)
    ax.text(ends[name]+.07,idx,f'{duration:.2f}s',va='center',fontsize=10)
    rows.append(dict(stage=name,start_s=start,end_s=ends[name],duration_s=duration,depends_on=';'.join(deps)))
ax.set_yticks(range(9),labels);ax.invert_yaxis();ax.set_xlim(0,7.4)
ax.axvline(.88,linestyle=':',label='工具已在0.88 s完成');ax.legend(loc='lower right')
save(fig,ax,'ch01_timeline',rows,'构造数据＋依赖递推。S7不在关键路径；不能把它的0.45秒重复加入总耗时。', 'SYNTHETIC_CALCULATION','第1章任务图')

Is=[10**(-1+i*4/100) for i in range(101)]
rows=[dict(arithmetic_intensity_flop_byte=i,roof_TFLOPs=min(1000,2*i)) for i in Is]
fig,ax=new('图3-R1 Roofline给上界，不给实际吞吐',ylabel='计算吞吐上界（TFLOP/s）',xlabel='运算强度（FLOP/byte）')
ax.loglog(Is,[r['roof_TFLOPs'] for r in rows],label='min(1000, 2I)')
ax.axvline(500,linestyle='--',label='ridge point = 500')
for m in [8,128,662]:
    i=2*m*4096**2/(2*(4096**2+2*m*4096)); y=min(1000,2*i)
    ax.plot(i,y,marker='o');ax.annotate(f'M={m}',(i,y),xytext=(5,-18 if m==662 else 6),textcoords='offset points')
ax.legend(loc='lower right')
save(fig,ax,'ch03_roofline',rows,'设备：稠密峰值1000 TFLOP/s、HBM带宽2000 GB/s；矩阵4096×4096，BF16。\n曲线与点均为模型计算，不是任何产品的微基准。','SYNTHETIC_CALCULATION','第3章公式')

fig,ax=new('图5-R1 平均服务时间相同，尾部形态仍改变平均排队',ylabel='平均等待（毫秒）',xlabel='到达率（请求/秒）')
rows=[]
for cv in [0,1,4]:
    rates=list(range(5,49)); waits=[1000*mg1_wait(r,.02,cv) for r in rates]
    ax.plot(rates,waits,label=f'服务时间 CV²={cv}')
    rows += [dict(arrival_req_s=r,mean_service_ms=20,cv_squared=cv,mean_wait_ms=w) for r,w in zip(rates,waits)]
ax.legend();ax.set_ylim(0,2600)
save(fig,ax,'ch05_queue',rows,'M/G/1模型：泊松到达、独立服务、单服务台、均值20 ms；不是连续批处理的容量预测器。','SYNTHETIC_CALCULATION','第5.8节推导')

rows=make_tp_rows()
fig,ax=new('图6-R1 正确计入KV分片后的静态槽位上界',ylabel='集群可容纳的4096-Token序列数')
bars=ax.bar(['TP8 × 1副本','TP4 × 2副本','TP2 × 4副本'],[r['cluster_slots'] for r in rows]);labelbars(ax,bars)
save(fig,ax,'ch06_tp_capacity',rows,'组合：8卡，每卡80 GB；权重140 GB；每rank固定开销4 GB；逻辑KV为128 KiB/Token。\n只计算容量，不包含输出增长、工作区动态变化和SLO；不是吞吐或采购建议。','SYNTHETIC_CALCULATION','第6.1节修订公式')

xs=[100.]*999+[5000.]
vals=[quantile(xs,.999),quantile(xs,.999,'linear')]
rows=[dict(method=m,q=.999,n=1000,value_ms=v) for m,v in zip(['inverted_cdf','linear'],vals)]
fig,ax=new('图7-R1 同一千条样本，两种P99.9算法',ylabel='P99.9（毫秒）')
labelbars(ax,ax.bar(['inverted_cdf（最近秩）','linear（线性插值）'],vals))
save(fig,ax,'ch07_quantile',rows,'样本：999条100 ms、1条5000 ms。两种P99.9均不能完整展示那个5000 ms极端值。\n差异来自统计定义，不是服务变快；算法语义参见N05。','SYNTHETIC_CALCULATION','N05 + 第7章样本')

rows=[dict(configuration=x,loading_seconds=y,source='N18',run_type='PUBLISHED_RESULT') for x,y in [('原路径',505.7),('修订路径',40.4)]]
fig,ax=new('图8-R1 官方案例：主机到设备的数据路径影响模型加载',ylabel='模型加载时间（秒）')
labelbars(ax,ax.bar([r['configuration'] for r in rows],[r['loading_seconds'] for r in rows]))
save(fig,ax,'ch08_public_loading',rows,'来源N18：SGLang v0.5.20发布说明；GLM-5.2，TP4，4×MI355X。\n仅重绘公开的505.7→40.4秒；未公开重复次数和误差条，不等于端到端服务同比提速。','PUBLISHED_RESULT','N18')

fig,ax=new('图11-R1 接受率不是速度：收益还取决于整轮成本',ylabel='理论加速比（相对普通一步）',xlabel='假设的条件接受概率 α')
rows=[]
alphas=[i/100 for i in range(101)]
for cost in [1.3,1.65,1.95]:
    speed=[progress(a,4)/cost for a in alphas]
    ax.plot(alphas,speed,label=f'整轮成本 c={cost}')
    rows += [dict(alpha=a,k=4,round_cost=cost,expected_progress=progress(a,4),speedup=v) for a,v in zip(alphas,speed)]
ax.axhline(1,linestyle=':',label='不增不减');ax.legend()
save(fig,ax,'ch11_speculative',rows,'模型：k=4，各位置条件接受概率相同，忽略EOS截断；整轮包含草稿、验证、校正与同步。\n真实接受率和整轮成本必须测量，本图不代表任何草稿模型。','SYNTHETIC_CALCULATION','第11章公式')

rows=[dict(metric=m,before_s=a,after_s=b,source='N06',run_type='PUBLISHED_RESULT') for m,a,b in [('图捕获',12,2),('引擎初始化',28.9,8.2)]]
fig,ax=new('图11-R2 官方案例：图捕获与初始化是不同计量对象',ylabel='时间（秒）')
x=[0,1];w=.32
b1=ax.bar([i-w/2 for i in x],[r['before_s'] for r in rows],w,label='修改前')
b2=ax.bar([i+w/2 for i in x],[r['after_s'] for r in rows],w,label='修改后')
ax.set_xticks(x,[r['metric'] for r in rows]);labelbars(ax,b1);labelbars(ax,b2);ax.legend()
save(fig,ax,'ch11_public_initialization',rows,'来源N06：vLLM v0.30.0，H200，图捕获期间冻结GC。\n发布摘要未给完整模型／形状／重复条件；初始化可能包含图捕获，两组时间不可相加。','PUBLISHED_RESULT','N06')

rows=[dict(mode=m,max_rate_req_s=v,source='N01',scope=s) for m,v,s in [('共置',1.6,'端到端共置'),('仅Prefill',5.6,'阶段隔离，非完整服务'),('仅Decode',10.,'阶段隔离，非完整服务')]]
fig,ax=new('图12-R1 DistServe动机实验：阶段干扰与约束容量',ylabel='图中约束下的请求速率（req/s）')
labelbars(ax,ax.bar([r['mode'] for r in rows],[r['max_rate_req_s'] for r in rows]))
save(fig,ax,'ch12_distserve',rows,'来源N01：OSDI 2024论文图1及相邻正文；13B模型，单A100 80GB，输入512／输出64。\nP90 TTFT 0.4 s、TPOT 0.04 s。阶段隔离不是完整服务，不能用10÷1.6宣称端到端加速。','PUBLISHED_RESULT','N01')

rows=[dict(pooling=x,tps=v,source='N09',run_type='PUBLISHED_RESULT') for x,v in [('关闭',2443),('开启',2313)]]
fig,ax=new('图15-R1 官方负面案例：增加pooling后TPS反而下降',ylabel='报告原生TPS（未替换指标口径）')
labelbars(ax,ax.bar([r['pooling'] for r in rows],[r['tps'] for r in rows]))
save(fig,ax,'ch15_public_regression',rows,'来源N09已知问题：Qwen3-32B W8A8、A2、P/D共置pooling测试，2443→2313（约−5.32%）。\n不是当前RC对所有模型的支持承诺；报告未给完整负载和重复数据，不补造误差条。','PUBLISHED_RESULT','N09')

rows=[dict(first_sample_delay_s=d,total_delay_s=d+30+115,run_type='SYNTHETIC_CALCULATION') for d in range(16)]
fig,ax=new('图16-R1 三次采样确认，不等于固定十分钟扩容延迟',ylabel='越过阈值至实例就绪（秒）',xlabel='首次命中采样的等待（秒）')
ax.plot([r['first_sample_delay_s'] for r in rows],[r['total_delay_s'] for r in rows],marker='o');ax.set_ylim(140,165)
save(fig,ax,'ch16_control_delay',rows,'自定义策略：15秒采样、连续3次确认、启动115秒；额外等待为0。\n区间145—160秒；不是Kubernetes默认策略或真实控制器测量。','SYNTHETIC_CALCULATION','第16章自定义策略；N19仅为方向性语义依据')

fig,ax=new('图17-R1 连续能力改善，现金可执行动作却是阶梯式',ylabel='满足单副本故障余量的实例数',xlabel='需求（有效请求/秒）')
rows=[]
for capacity in [8,10]:
    demand=list(range(1,81)); ns=[replicas(d,capacity) for d in demand]
    ax.step(demand,ns,where='post',label=f'每副本 {capacity} req/s')
    rows += [dict(demand_req_s=d,capacity_per_replica=capacity,unavailable=1,required_replicas=n) for d,n in zip(demand,ns)]
ax.legend();ax.set_yticks(range(1,13))
save(fig,ax,'ch17_replica_steps',rows,'完全同质副本的模型：n=ceil(需求/每副本能力)+1；无价格输入，不能据此承诺现金节省。','SYNTHETIC_CALCULATION','第16—17章整数模型')

(BASE/'figure_catalog.json').write_text(json.dumps(CAT,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 新增图表与数据目录','','所有图由本目录代码生成；公开结果重绘不改变原始数据，不补造逐请求样本和误差条。','',
       '| 图 | 来源类别 | 数据 | 图片 |','|---|---|---|---|']
for item in CAT:
    lines.append(f'| {item["id"]} | {item["provenance"]} / {item["source"]} | [CSV]({item["data"]}) | [PNG]({item["figure"]}) / [SVG]({item["svg"]}) |')
(BASE/'figures.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(BASE/'data'/'plot_runtime.json').write_text(json.dumps(dict(python=platform.python_version(),matplotlib=matplotlib.__version__,figures=len(CAT)),indent=2),encoding='utf-8')
print(f'Built {len(CAT)} figures, each PNG + SVG + CSV')
