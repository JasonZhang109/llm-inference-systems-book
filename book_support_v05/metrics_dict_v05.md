# 指标字典与E0最小测量契约 v0.5

2026-09-30。本文件从本次第1、7—9章的定义整理并校正，不冒称为原项目未附带的metrics_dict.md原文件。它是本书计量约定，不是任何工具的默认实现标准。

## 1. 对象与身份

`task_id`标识业务交付；`request_id`标识逻辑请求；`attempt_id`标识物理尝试；`model_call_id`标识逻辑模型调用，实际执行次数另记；`session_id`是上下文容器，不假设为其它对象的严格父级。跨组件事件还应有`run_id`、`trace_id`和适用的`transfer_id`。

每条记录保留事件名、时间值、单位、`clock_domain`、事件产生组件、观测方式和缺失原因。不同主机的单调时钟不直接相减；本机跨进程是否同域也必须核验。未知的校准偏差不能写为0。

## 2. 时间指标

| 本书字段 | 起点 | 终点／算式 | 边界 |
|---|---|---|---|
| TTFT_server | engine.queued | engine.first_token_generated | 排队至首生成Token；不等于所有引擎原生arrival_time口径 |
| TTFO_server | engine.queued | 首个可见内容写出 | 排除仅推理／工具控制输出，适用范围须声明 |
| TTFT_client | client.send | 客户端首个合格内容事件 | 无逐Token时刻时标注事件代理，不声称精确Token生成时间 |
| TTFO_client | client.send | 客户端首个可见答案事件 | 客户端接收与渲染可分别设终点 |
| E2E_content | 选定起点 | 最后内容事件 | 不包含其后的协议终端事件 |
| E2E_terminal | 选定起点 | 终端事件 | 包含终端尾部；不同于E2E_content |
| TPOT_req_content | 首生成Token | (最后内容事件−首生成Token)/(N_out−1) | 本书样例的分摊指标；不是精确逐Token间隔 |
| TPOT_req_terminal | 首生成Token | (终端事件−首生成Token)/(N_out−1) | 终端尾部也被摊入；必须带后缀 |
| ITL_event | 相邻内容事件 | 相邻事件之差 | M个事件有M−1个间隔，不对多Token块均分造时刻 |
| ITL_token | 相邻生成Token | 相邻Token之差 | 只有得到逐Token生成时间和数量时才可报告 |

`N_out≤1`时TPOT为null/不适用。缺少首可见输出时TTFO为null/未观测；null不能填0。是否在SLO中合格，另按任务类型处理，单Token分类任务可以完全有效。

## 3. Sample-B0时间端点

以下均为时间线。server域：入队21 ms，首Token634 ms，首内容写出641 ms，首可见写出1180 ms，最后内容4210 ms，终端4213 ms。客户端独立测量：send=0 ms，首内容668 ms，首可见1207 ms，terminal=4250 ms。客户端和服务端值不默认共享一个绝对时钟。

`N_out=301`、内容事件`M=20`。由此可得：TTFT_server=613 ms；TTFO_server=1159 ms；E2E_content=4189 ms；E2E_terminal=4192 ms；TPOT_content=11.92 ms；TPOT_terminal=11.93 ms。若20个服务端内容事件首末为641和4210，则平均ITL_event=3569/19≈187.84 ms。

客户端TTFT=668 ms、TTFO=1207 ms可直接在client域得到。两个域的持续时间差可以比较，但不能未经对时把634→668解释成一次精确单向网络延迟。生成→写出的7 ms在server域可测，写出→接收的27 ms需要跨域映射或明确的假设。

E0程序只测试列明的时间差与算式，没有复现真实SSE、gRPC或引擎前端，也没有自动确认任何工具使用这些定义。

## 4. 产出与窗口

输入至少分为逻辑输入、实际执行输入和抢占重放输入；缓存复用的逻辑输入可以计入已服务工作量，避免的计算不应伪装成新执行量。输出区分最终接受Token、推理Token、可见答案Token和被拒候选。客户端重分词不等于模型生成计数。

固定事件窗口吞吐计入窗口内的完成事件，包括窗口前到达但窗口内完成的请求；排空法则以固定cohort的首发至末终结为时间分母。二者保留独立名称。未终结、超时、拒绝和取消计数不能消失。

有效完成速率=`窗口内成功且质量及SLO合格的完成单位数/窗口时长`。联合达标率=`合格单位数/契约观察集合总数`。SLO约束容量是满足全部门槛的负载边界，不是上述两个数字的另一种叫法。

## 5. 聚合

报告必须记录样本量、分位算法、权重单位和缺失处理。默认E0最近秩对应`inverted_cdf`；对照实现`linear`对应线性插值。实例分位数不取平均冒充总体分位数。直方图合并还需相容的桶语义。

请求级TPOT均值、所有事件间隔混合均值以及Token加权均值回答不同问题。不能因名称中都带“每Token”就直接作差。

## 6. 运行与证据

运行`python book_support_v05/code/e0_reference.py`会输出逐项测试报告。`hardware_experiments_executed=false`保持明确；所有异常输入应报错或按契约返回null，不静默填0。

配套来源：[N05 NumPy](references.md#n05)、[N16工具迁移](references.md#n16)、[N24直方图](references.md#n24)、[N28取消](references.md#n28)、[N29时钟](references.md#n29)。
