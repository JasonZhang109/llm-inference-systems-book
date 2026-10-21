# 参考资料：本轮核验与原稿归档分开

查阅日：2026-09-30。N系列是本轮具体命题记录；R/S系列保留原稿来源身份，不宣称每条都重新核验。所有本地硬件运行状态均为false。

公开资料只支持其明确条件；网页存在、正文可读与组合官方支持是不同状态。未知日期保持未记录，短commit不是全文归档。

## 本轮N系列

<a id="n01"></a>
### N01 DistServe — OSDI 2024正式论文
来源：[原始页面](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf)。版本：OSDI 2024；发布日期：2024-07；查阅：2026-09-30。
定位：PDF第2页图1及相邻正文。短commit：未固定。
支持命题：13B、A100 80GB、输入512/输出64；共置约1.6，P-only约5.6，D-only约10 req/s；阶段隔离不可冒充完整服务。
正文条目核验：True；作者硬件运行：false。边界：已查看相关PDF页图；只重绘公开标量，未取得逐请求数据，也未重跑论文。

<a id="n02"></a>
### N02 PagedAttention原始论文
来源：[原始页面](https://arxiv.org/abs/2309.06180)。版本：2023论文；发布日期：2023-09；查阅：2026-09-30。
定位：摘要及分页设计。短commit：未固定。
支持命题：分页与共享管理缓解KV分配浪费；收益属于论文条件，不能作固定倍率。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n03"></a>
### N03 Fast Inference from Transformers via Speculative Decoding
来源：[原始页面](https://proceedings.mlr.press/v202/leviathan23a.html)。版本：ICML 2023 / PMLR 202；发布日期：2023；查阅：2026-09-30。
定位：论文入口、摘要及算法依据。短commit：未固定。
支持命题：精确推测采样的分布保持条件；本书给出单步接受／残差校正推导。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n04"></a>
### N04 Introducing NVFP4
来源：[原始页面](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)。版本：2025技术说明；发布日期：2025-06-24；查阅：2026-09-30。
定位：NVFP4/MXFP4对照表与缩放说明。短commit：未固定。
支持命题：NVFP4每16元素FP8缩放并有张量级缩放；MXFP4块长32，不可混用两种元数据开销。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n05"></a>
### N05 NumPy quantile
来源：[原始页面](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html)。版本：stable，查阅时页面文档线2.5；发布日期：未固定；查阅：2026-09-30。
定位：method参数与算法说明。短commit：未固定。
支持命题：linear与inverted_cdf不是同一算法；本书100/104.9ms例为独立复算。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n06"></a>
### N06 vLLM v0.30.0发布说明
来源：[原始页面](https://github.com/vllm-project/vllm/releases/tag/v0.30.0)。版本：v0.30.0；发布日期：2026-09-22；查阅：2026-09-30。
定位：Highlights: Fast Start、Model Runner V2。短commit：ced6857。
支持命题：CUDA IPC权重映射；H200图捕获12→2s、初始化28.9→8.2s。
正文条目核验：True。边界：发布摘要未提供该性能例完整模型、形状和重复条件。

<a id="n07"></a>
### N07 vLLM Ascend RC发布说明
来源：[原始页面](https://github.com/vllm-project/vllm-ascend/releases/tag/v0.26.0rc1)。版本：v0.26.0rc1；发布日期：2026-09-03；查阅：2026-09-30。
定位：依赖、模型支持和移除清单。短commit：f2f74a1。
支持命题：模型限定RC；vLLM0.26、CANN9.1、PyTorch2.10、torch_npu2.10.0.post4等依赖；不能升级为通用GA组合。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n08"></a>
### N08 CANN离线推理性能剖析指南
来源：[原始页面](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/850/devaids/profiling/atlasprofiling_16_0005.html)。版本：CANN社区版8.5.0；发布日期：未固定；查阅：2026-09-30。
定位：Getting Started…；命令形式；Table 2。短commit：未固定。
支持命题：msprof --output形式及timeline/op_summary/op_statistic/task_time产物语义。
正文条目核验：True；作者硬件运行：false。边界：只核验8.5.0正文；不能用于证明msprof26.1或CANN9.1集成兼容。包装脚本仅作shell语法检查。

<a id="n09"></a>
### N09 vLLM Ascend RC测试总结
来源：[原始页面](https://github.com/vllm-project/vllm-ascend/blob/releases/v0.26.0rc/tests/vllm_ascend_v0.26.0rc1_test_conclusion.md)。版本：releases/v0.26.0rc分支上的RC1总结；发布日期：未固定；查阅：2026-09-30。
定位：Models / Accuracy / Known Issues。短commit：未固定。
支持命题：官方覆盖、GPQA/OCRBench原值；DSpark长输入收益不足；Qwen3-32B pooling TPS 2443→2313负面案例。
正文条目核验：True；作者硬件运行：false。边界：发布分支可更新，未固定全文commit；完整吞吐矩阵、逐请求样本和重复条件不足。已知问题中的模型不等于该RC当前全部受支持模型。

<a id="n10"></a>
### N10 Dynamo v1.5.0发布说明
来源：[原始页面](https://github.com/ai-dynamo/dynamo/releases/tag/v1.5.0)。版本：v1.5.0；发布日期：2026-09-21；查阅：2026-09-30。
定位：Backend versions / Deprecations。短commit：b83b1d9。
支持命题：后端及NIXL依赖分别固定；KVBM弃用与计划移除不可合并。
正文条目核验：True；作者硬件运行：false。边界：GitHub显示发布日期与原稿登记09-18不同，保留来源差异；本书未重建。

<a id="n11"></a>
### N11 Qwen2.5-7B-Instruct配置
来源：[原始页面](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/config.json)。版本：main配置；发布日期：未固定；查阅：2026-09-30。
定位：hidden_size / num_hidden_layers / num_key_value_heads。短commit：未固定。
支持命题：hidden3584、28层、4个KV头；常规BF16 KV的56KiB/Token是本书计算，不是显存实测。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n12"></a>
### N12 DeepSeek-V3配置
来源：[原始页面](https://huggingface.co/deepseek-ai/DeepSeek-V3/blob/main/config.json)。版本：main配置；发布日期：未固定；查阅：2026-09-30。
定位：kv_lora_rank / qk_rope_head_dim / num_hidden_layers。短commit：未固定。
支持命题：MLA配置512、64、61层；压缩缓存BF16假设下68.625KiB/Token，不含额外状态与工作区。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n13"></a>
### N13 FlashAttention原始论文
来源：[原始页面](https://arxiv.org/abs/2205.14135)。版本：2022论文；发布日期：2022-05；查阅：2026-09-30。
定位：摘要与IO-aware设计。短commit：未固定。
支持命题：减少HBM中间读写不等于把全部注意力计算变成线性；在线softmax递推在本书展开。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n14"></a>
### N14 vLLM Automatic Prefix Caching
来源：[原始页面](https://docs.vllm.ai/en/stable/design/prefix_caching/)。版本：stable浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：Cache salt / Block hash。短commit：未固定。
支持命题：缓存键与授权信任组隔离；身份一致不等于自动逐bit复现。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n15"></a>
### N15 vLLM Optimization
来源：[原始页面](https://docs.vllm.ai/en/stable/configuration/optimization/)。版本：stable浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：Chunked Prefill / Preemption。短commit：未固定。
支持命题：分块预算、decode优先与重算抢占属于具体引擎机制，不是所有后端的统一定义。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n16"></a>
### N16 AIPerf迁移说明
来源：[原始页面](https://docs.nvidia.com/aiperf/getting-started/migrating-from-gen-ai-perf)。版本：浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：推理模型TTFT/TTFO迁移。短commit：未固定。
支持命题：迁移需按首任意Token／首非推理输出映射，不只对齐字段名。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n17"></a>
### N17 NVIDIA System Management Interface
来源：[原始页面](https://docs.nvidia.com/deploy/nvidia-smi/index.html)。版本：浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：Utilization定义。短commit：未固定。
支持命题：GPU和Memory利用率分别有采样窗口时间语义，不等于实际FLOP/s或字节/s占峰值。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n18"></a>
### N18 SGLang v0.5.20发布说明
来源：[原始页面](https://github.com/sgl-project/sglang/releases/tag/v0.5.20)。版本：v0.5.20；发布日期：2026-09-18；查阅：2026-09-30。
定位：Faster model loading on ROCm；Simulator；Prefill CP。短commit：未固定。
支持命题：GLM-5.2 TP4在4×MI355X加载505.7→40.4s；CPU模拟与旧Prefill CP路径的版本边界。
正文条目核验：True；作者硬件运行：false。边界：没有该加载例的重复数据和完整配置；只重绘公开标量。

<a id="n19"></a>
### N19 Kubernetes Horizontal Pod Autoscaling
来源：[原始页面](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)。版本：查阅时浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：Stabilization window / Default behavior。短commit：未固定。
支持命题：scaleUp与scaleDown的稳定窗口分开，不能把缩容300s固定加到每次扩容。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n20"></a>
### N20 DeepSeek-V4.1-Flash模型卡
来源：[原始页面](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)。版本：main模型卡；发布日期：未固定；查阅：2026-09-30。
定位：Architecture / KV表示。短commit：未固定。
支持命题：CED与跨层状态改变阶段成本；模型卡缓存格式和所选引擎实际布局需分列。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n21"></a>
### N21 Qwen3.8-Flash-Next模型卡
来源：[原始页面](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)。版本：实验预览模型卡；发布日期：未固定；查阅：2026-09-30。
定位：混合结构与预览说明。短commit：未固定。
支持命题：Gated DeltaNet与QSA混合，状态须逐类求和，不使用单一全注意力公式。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n22"></a>
### N22 TensorRT-LLM RC发布页
来源：[原始页面](https://github.com/NVIDIA/TensorRT-LLM/releases/tag/v1.3.0rc28)。版本：v1.3.0rc28；发布日期：2026-09-23；查阅：2026-09-30。
定位：发布页身份。短commit：未固定。
支持命题：确认有该发布页；具体遗留入口清理条目本轮不作新核验结论。
正文条目核验：False；作者硬件运行：false。边界：条目级正文核验不足；原稿S04保留归档身份，不能据此编写迁移命令。

<a id="n23"></a>
### N23 vLLM v0.29.0发布说明
来源：[原始页面](https://github.com/vllm-project/vllm/releases/tag/v0.29.0)。版本：v0.29.0；发布日期：2026-09-09；查阅：2026-09-30。
定位：Model Runner V2与回退说明。短commit：98dff2a。
支持命题：MRV2默认与部分MRV1回退需按版本记录；弃用不等于立即移除。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n24"></a>
### N24 Prometheus Histograms and summaries
来源：[原始页面](https://prometheus.io/docs/practices/histograms/)。版本：浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：Quantile aggregation / Errors。短commit：未固定。
支持命题：预计算分位数不能通过取平均获得总体分位数；histogram聚合需要正确表示和桶配置。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n25"></a>
### N25 vLLM Reproducibility
来源：[原始页面](https://docs.vllm.ai/en/stable/usage/reproducibility/)。版本：stable浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：在线／离线与硬件版本限制。短commit：未固定。
支持命题：默认不保证复现；在线批不变性与离线确定性调度分别处理。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n26"></a>
### N26 vLLM Batch Invariance
来源：[原始页面](https://docs.vllm.ai/en/stable/features/batch_invariance/)。版本：stable浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：硬件范围、启用与tested models。短commit：未固定。
支持命题：功能有模型、设备及实现条件，不能外推跨硬件逐bit一致。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n27"></a>
### N27 vLLM CUDA Graphs设计
来源：[原始页面](https://docs.vllm.ai/en/stable/design/cuda_graphs/)。版本：stable浮动文档；发布日期：未固定；查阅：2026-09-30。
定位：BatchDescriptor / dispatcher。短commit：未固定。
支持命题：图模式、批描述、后端能力共同决定运行路径，不只是命中／eager二选一。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n28"></a>
### N28 gRPC Deadlines
来源：[原始页面](https://grpc.io/docs/guides/deadlines/)。版本：浮动指南；发布日期：未固定；查阅：2026-09-30。
定位：Deadlines on the Server。短commit：未固定。
支持命题：RPC取消后，应用仍负责停止已经派生的活动。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

<a id="n29"></a>
### N29 Python time
来源：[原始页面](https://docs.python.org/3/library/time.html)。版本：查阅时3.14.7文档；发布日期：未固定；查阅：2026-09-30。
定位：monotonic_ns / perf_counter_ns。短commit：未固定。
支持命题：用单调时钟差值测时；本机共享时钟不能外推到不同主机。
正文条目核验：True；作者硬件运行：false。边界：未在本书环境运行；浮动页仍需在正式实验时固定完整revision。

## 原稿R/S系列导航

完整历史记录见[归档](legacy_references.md)。以下导航只解决引用落点，不提升证据等级。

<a id="r01"></a>
### R01 vLLM：Metrics
[原始入口](https://docs.vllm.ai/en/stable/design/metrics/)；[历史登记](legacy_references.md#ref-r01)。原稿记录，非本轮逐条重新核验。

<a id="r02"></a>
### R02 Kwon 等：Efficient Memory Management for Large Language Model Serving with PagedAttention（2023）
[原始入口](https://arxiv.org/abs/2309.06180)；[历史登记](legacy_references.md#ref-r02)。原稿记录，非本轮逐条重新核验。

<a id="r03"></a>
### R03 Dao 等：FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness（2022）
[原始入口](https://arxiv.org/abs/2205.14135)；[历史登记](legacy_references.md#ref-r03)。原稿记录，非本轮逐条重新核验。

<a id="r04"></a>
### R04 Hugging Face Transformers：Cache strategies
[原始入口](https://huggingface.co/docs/transformers/en/kv_cache)；[历史登记](legacy_references.md#ref-r04)。原稿记录，非本轮逐条重新核验。

<a id="r05"></a>
### R05 DeepSeek-AI：DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model（2024）
[原始入口](https://arxiv.org/abs/2405.04434)；[历史登记](legacy_references.md#ref-r05)。原稿记录，非本轮逐条重新核验。

<a id="r06"></a>
### R06 Zheng 等：SGLang: Efficient Execution of Structured Language Model Programs
[原始入口](https://arxiv.org/abs/2312.07104)；[历史登记](legacy_references.md#ref-r06)。原稿记录，非本轮逐条重新核验。

<a id="r07"></a>
### R07 vLLM：Automatic Prefix Caching（设计文档）
[原始入口](https://docs.vllm.ai/en/stable/design/prefix_caching/)；[历史登记](legacy_references.md#ref-r07)。原稿记录，非本轮逐条重新核验。

<a id="r08"></a>
### R08 NVIDIA NCCL：Collective Operations
[原始入口](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html)；[历史登记](legacy_references.md#ref-r08)。原稿记录，非本轮逐条重新核验。

<a id="r09"></a>
### R09 Zhong 等：DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving（2024）
[原始入口](https://arxiv.org/abs/2401.09670)；[历史登记](legacy_references.md#ref-r09)。原稿记录，非本轮逐条重新核验。

<a id="r10"></a>
### R10 SGLang：PD Disaggregation
[原始入口](https://docs.sglang.io/docs/advanced_features/pd_disaggregation)；[历史登记](legacy_references.md#ref-r10)。原稿记录，非本轮逐条重新核验。

<a id="r11"></a>
### R11 NVIDIA：GenAI-Perf
[原始入口](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)；[历史登记](legacy_references.md#ref-r11)。原稿记录，非本轮逐条重新核验。

<a id="r12"></a>
### R12 NVIDIA AIPerf：Metrics Reference
[原始入口](https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference)；[历史登记](legacy_references.md#ref-r12)。原稿记录，非本轮逐条重新核验。

<a id="r13"></a>
### R13 NVIDIA AIPerf：Migrating from GenAI-Perf
[原始入口](https://docs.nvidia.com/aiperf/getting-started/migrating-from-gen-ai-perf)；[历史登记](legacy_references.md#ref-r13)。原稿记录，非本轮逐条重新核验。

<a id="r14"></a>
### R14 MLCommons：MLPerf Inference Datacenter
[原始入口](https://mlcommons.org/benchmarks/inference-datacenter/)；[历史登记](legacy_references.md#ref-r14)。原稿记录，非本轮逐条重新核验。

<a id="r15"></a>
### R15 Prometheus：Histograms and summaries
[原始入口](https://prometheus.io/docs/practices/histograms/)；[历史登记](legacy_references.md#ref-r15)。原稿记录，非本轮逐条重新核验。

<a id="r16"></a>
### R16 PyTorch：torch.profiler
[原始入口](https://docs.pytorch.org/docs/stable/profiler.html)；[历史登记](legacy_references.md#ref-r16)。原稿记录，非本轮逐条重新核验。

<a id="r17"></a>
### R17 NVIDIA Nsight Systems：User Guide
[原始入口](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)；[历史登记](legacy_references.md#ref-r17)。原稿记录，非本轮逐条重新核验。

<a id="r18"></a>
### R18 OpenTelemetry：Semantic Conventions for Generative AI
[原始入口](https://github.com/open-telemetry/semantic-conventions-genai)；[历史登记](legacy_references.md#ref-r18)。原稿记录，非本轮逐条重新核验。

<a id="r19"></a>
### R19 vLLM Ascend：Documentation
[原始入口](https://docs.vllm.ai/projects/ascend/en/latest/)；[历史登记](legacy_references.md#ref-r19)。原稿记录，非本轮逐条重新核验。

<a id="r20"></a>
### R20 华为 MindStudio：msprof 命令行性能数据采集（26.1.0 文档入口）
[原始入口](https://www.hiascend.com/document/detail/zh/mindstudio/2610/msTT_msIT/msProf/docs/zh/profiling/msprof_cmd/ai_runtime_profile_data.md)；[历史登记](legacy_references.md#ref-r20)。原稿记录，非本轮逐条重新核验。

<a id="r21"></a>
### R21 AMD HIP：Performance optimization（7.14.0 文档入口）
[原始入口](https://rocm.docs.amd.com/projects/HIP/en/docs-7.14.0/understand/performance_optimization.html)；[历史登记](legacy_references.md#ref-r21)。原稿记录，非本轮逐条重新核验。

<a id="r22"></a>
### R22 Lawrence Berkeley National Laboratory：Roofline Performance Model
[原始入口](https://amcr.lbl.gov/departments/computer-science-department/ppan/roofline-performance-model/)；[历史登记](legacy_references.md#ref-r22)。原稿记录，非本轮逐条重新核验。

<a id="r23"></a>
### R23 NVIDIA TensorRT-LLM：Overview
[原始入口](https://nvidia.github.io/TensorRT-LLM/overview.html)；[历史登记](legacy_references.md#ref-r23)。原稿记录，非本轮逐条重新核验。

<a id="r24"></a>
### R24 Google SRE：Service Level Objectives
[原始入口](https://sre.google/sre-book/service-level-objectives/)；[历史登记](legacy_references.md#ref-r24)。原稿记录，非本轮逐条重新核验。

<a id="r25"></a>
### R25 Google SRE：Handling Overload
[原始入口](https://sre.google/sre-book/handling-overload/)；[历史登记](legacy_references.md#ref-r25)。原稿记录，非本轮逐条重新核验。

<a id="r26"></a>
### R26 vLLM：Quantization
[原始入口](https://docs.vllm.ai/en/stable/features/quantization/)；[历史登记](legacy_references.md#ref-r26)。原稿记录，非本轮逐条重新核验。

<a id="r27"></a>
### R27 Leviathan、Kalman、Matias：Fast Inference from Transformers via Speculative Decoding（ICML 2023）
[原始入口](https://proceedings.mlr.press/v202/leviathan23a.html)；[历史登记](legacy_references.md#ref-r27)。原稿记录，非本轮逐条重新核验。

<a id="r28"></a>
### R28 vLLM：Hybrid KV Cache Manager
[原始入口](https://docs.vllm.ai/en/stable/design/hybrid_kv_cache_manager/)；[历史登记](legacy_references.md#ref-r28)。原稿记录，非本轮逐条重新核验。

<a id="r29"></a>
### R29 Hugging Face Transformers：Chat templates
[原始入口](https://huggingface.co/docs/transformers/en/chat_templating)；[历史登记](legacy_references.md#ref-r29)。原稿记录，非本轮逐条重新核验。

<a id="r30"></a>
### R30 vLLM：Parallelism and Scaling
[原始入口](https://docs.vllm.ai/en/stable/serving/parallelism_scaling/)；[历史登记](legacy_references.md#ref-r30)。原稿记录，非本轮逐条重新核验。

<a id="r31"></a>
### R31 vLLM：torch.compile integration
[原始入口](https://docs.vllm.ai/en/stable/design/torch_compile/)；[历史登记](legacy_references.md#ref-r31)。原稿记录，非本轮逐条重新核验。

<a id="r32"></a>
### R32 SGLang：HiCache
[原始入口](https://docs.sglang.ai/advanced_features/hicache.html)；[历史登记](legacy_references.md#ref-r32)。原稿记录，非本轮逐条重新核验。

<a id="r33"></a>
### R33 华为 CANN：HCCL 用户指南（8.5.0 alpha002 文档入口）
[原始入口](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850alpha002/hccl/hcclug)；[历史登记](legacy_references.md#ref-r33)。原稿记录，非本轮逐条重新核验。

<a id="s01"></a>
### S01 vLLM v0.29.0 release
[原始入口](https://github.com/vllm-project/vllm/releases/tag/v0.29.0)；[历史登记](legacy_references.md#ref-s01)。原稿记录，非本轮逐条重新核验。

<a id="s02"></a>
### S02 vLLM v0.30.0 release
[原始入口](https://github.com/vllm-project/vllm/releases/tag/v0.30.0)；[历史登记](legacy_references.md#ref-s02)。原稿记录，非本轮逐条重新核验。

<a id="s03"></a>
### S03 SGLang releases
[原始入口](https://github.com/sgl-project/sglang/releases)；[历史登记](legacy_references.md#ref-s03)。原稿记录，非本轮逐条重新核验。

<a id="s04"></a>
### S04 TensorRT-LLM v1.3.0rc28
[原始入口](https://github.com/NVIDIA/TensorRT-LLM/releases/tag/v1.3.0rc28)；[历史登记](legacy_references.md#ref-s04)。原稿记录，非本轮逐条重新核验。

<a id="s05"></a>
### S05 TensorRT-LLM Overview
[原始入口](https://nvidia.github.io/TensorRT-LLM/overview.html)；[历史登记](legacy_references.md#ref-s05)。原稿记录，非本轮逐条重新核验。

<a id="s06"></a>
### S06 NVIDIA Dynamo v1.5.0
[原始入口](https://docs.dynamo.nvidia.com/dynamo/reference/releases/v1-5-0)；[历史登记](legacy_references.md#ref-s06)。原稿记录，非本轮逐条重新核验。

<a id="s07"></a>
### S07 llm-d v0.9: Hardened for Scale
[原始入口](https://llm-d.ai/blog/llm-d-v0.9-hardened-for-scale)；[历史登记](legacy_references.md#ref-s07)。原稿记录，非本轮逐条重新核验。

<a id="s08"></a>
### S08 FlashAttention official repository
[原始入口](https://github.com/Dao-AILab/flash-attention)；[历史登记](legacy_references.md#ref-s08)。原稿记录，非本轮逐条重新核验。

<a id="s09"></a>
### S09 FlashInfer official repository
[原始入口](https://github.com/flashinfer-ai/flashinfer)；[历史登记](legacy_references.md#ref-s09)。原稿记录，非本轮逐条重新核验。

<a id="s10"></a>
### S10 Introducing NVFP4
[原始入口](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)；[历史登记](legacy_references.md#ref-s10)。原稿记录，非本轮逐条重新核验。

<a id="s11"></a>
### S11 DeepSeek-V4.1-Flash model card
[原始入口](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)；[历史登记](legacy_references.md#ref-s11)。原稿记录，非本轮逐条重新核验。

<a id="s12"></a>
### S12 Qwen3.8-Flash-Next model card
[原始入口](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)；[历史登记](legacy_references.md#ref-s12)。原稿记录，非本轮逐条重新核验。

<a id="s13"></a>
### S13 LMCache documentation
[原始入口](https://docs.lmcache.ai/)；[历史登记](legacy_references.md#ref-s13)。原稿记录，非本轮逐条重新核验。

<a id="s14"></a>
### S14 Mooncake official repository
[原始入口](https://github.com/kvcache-ai/Mooncake)；[历史登记](legacy_references.md#ref-s14)。原稿记录，非本轮逐条重新核验。

<a id="s15"></a>
### S15 NIXL official repository
[原始入口](https://github.com/ai-dynamo/nixl)；[历史登记](legacy_references.md#ref-s15)。原稿记录，非本轮逐条重新核验。

<a id="s16"></a>
### S16 DeepEP official repository
[原始入口](https://github.com/deepseek-ai/DeepEP)；[历史登记](legacy_references.md#ref-s16)。原稿记录，非本轮逐条重新核验。

<a id="s17"></a>
### S17 AIPerf: Migrating from GenAI-Perf
[原始入口](https://docs.nvidia.com/aiperf/getting-started/migrating-from-gen-ai-perf)；[历史登记](legacy_references.md#ref-s17)。原稿记录，非本轮逐条重新核验。

<a id="s18"></a>
### S18 AIPerf: Conversation DAG Benchmarks
[原始入口](https://docs.nvidia.com/aiperf/benchmark-modes/conversation-dag-benchmarks)；[历史登记](legacy_references.md#ref-s18)。原稿记录，非本轮逐条重新核验。

<a id="s19"></a>
### S19 vLLM Ascend v0.23.0.post1
[原始入口](https://github.com/vllm-project/vllm-ascend/releases/tag/v0.23.0.post1)；[历史登记](legacy_references.md#ref-s19)。原稿记录，非本轮逐条重新核验。

<a id="s20"></a>
### S20 vLLM Ascend v0.26.0rc1
[原始入口](https://github.com/vllm-project/vllm-ascend/releases/tag/v0.26.0rc1)；[历史登记](legacy_references.md#ref-s20)。原稿记录，非本轮逐条重新核验。

<a id="s21"></a>
### S21 NVIDIA GB300 NVL72 product page
[原始入口](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)；[历史登记](legacy_references.md#ref-s21)。原稿记录，非本轮逐条重新核验。

<a id="s22"></a>
### S22 AMD Instinct MI350 series product page
[原始入口](https://www.amd.com/en/products/accelerators/instinct/mi350.html)；[历史登记](legacy_references.md#ref-s22)。原稿记录，非本轮逐条重新核验。

<a id="s23"></a>
### S23 HIP performance optimization 7.14.0 path
[原始入口](https://rocm.docs.amd.com/projects/HIP/en/docs-7.14.0/understand/performance_optimization.html)；[历史登记](legacy_references.md#ref-s23)。原稿记录，非本轮逐条重新核验。

<a id="s24"></a>
### S24 MindStudio msprof 26.1.0 entry
[原始入口](https://www.hiascend.com/document/detail/zh/mindstudio/2610/msTT_msIT/msProf/docs/zh/profiling/msprof_cmd/ai_runtime_profile_data.md)；[历史登记](legacy_references.md#ref-s24)。原稿记录，非本轮逐条重新核验。

<a id="s25"></a>
### S25 CANN 8.5.0 alpha002 HCCL entry
[原始入口](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850alpha002/hccl/hcclug)；[历史登记](legacy_references.md#ref-s25)。原稿记录，非本轮逐条重新核验。

<a id="s26"></a>
### S26 Huawei MindIE product entry
[原始入口](https://www.hiascend.com/software/mindie)；[历史登记](legacy_references.md#ref-s26)。原稿记录，非本轮逐条重新核验。

## DOC别名与来源映射

原稿W来源编号与W01—W08负载重号，本版仅把方括号内文献编号改为DOC-W。缺少精确原始映射时不猜写URL。

<a id="doc-w01"></a>
### DOC-W01 vLLM可复现性
对应 [N25](#n25)。

<a id="doc-w02"></a>
### DOC-W02 vLLM批不变性
对应 [N26](#n26)。

<a id="doc-w03"></a>
### DOC-W03 分块Prefill与优化
对应 [N15](#n15)。

<a id="doc-w04"></a>
### DOC-W04 原稿W04引用：尚缺准确映射
原稿引用身份保留；精确版本、URL或正文定位未随本轮18章完整提供，本版登记为引用缺口。相关实现命题须再次锁定后用于正式实验。

<a id="doc-w05"></a>
### DOC-W05 CUDA Graph设计
对应 [N27](#n27)。

<a id="doc-w06"></a>
### DOC-W06 工具调用文档（原稿仅入口）
原稿引用身份保留；精确版本、URL或正文定位未随本轮18章完整提供，本版登记为引用缺口。相关实现命题须再次锁定后用于正式实验。

<a id="doc-w07"></a>
### DOC-W07 vLLM指标设计
对应 [R01](#r01)。

<a id="doc-w08"></a>
### DOC-W08 gRPC Deadline
对应 [N28](#n28)。

<a id="doc-w09"></a>
### DOC-W09 AIPerf迁移
对应 [N16](#n16)。

<a id="doc-w10"></a>
### DOC-W10 Python时钟文档
对应 [N29](#n29)。

<a id="doc-e01"></a>
### DOC-E01 DistServe Goodput定义
对应 [N01](#n01)。

<a id="doc-e04"></a>
### DOC-E04 NumPy分位算法
对应 [N05](#n05)。

<a id="doc-e05"></a>
### DOC-E05 nvidia-smi原生字段
对应 [N17](#n17)。

<a id="doc-e06"></a>
### DOC-E06 Nsight开销分类（原稿入口待固定）
原稿引用身份保留；精确版本、URL或正文定位未随本轮18章完整提供，本版登记为引用缺口。相关实现命题须再次锁定后用于正式实验。
