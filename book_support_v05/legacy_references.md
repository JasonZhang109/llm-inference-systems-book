# 原稿来源登记归档（不作为本轮全部核验完成的证明）

以下保留原稿历史记录；其中“本次”“本轮”均指原登记轮次，不指v0.5。新核验以references.md的N系列为准。

---

# 参考资料与版本登记

R01—R33保留原稿身份，S01—S26承接技术时效性复核。日期与正文状态均为输入资料的历史登记；本次合并未重新浏览网页或做硬件实验。正式扩写须把浮动入口定位到具体版本/commit/正文段落。相同URL可有不同引用身份，用别名关联避免重复维护。

## R系列：原理与原稿资料入口

<a id="ref-r01"></a>
### R01 vLLM：Metrics

**类型：**官方设计文档。**原稿登记日：**2026-09-29。

**使用范围：**指标事件边界、统计口径和实现差异；使用时还需固定代码版本。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/en/stable/design/metrics/`

<a id="ref-r02"></a>
### R02 Kwon 等：Efficient Memory Management for Large Language Model Serving with PagedAttention（2023）

**类型：**原始论文。**原稿登记日：**2026-09-29。

**使用范围：**分页式 KV 管理的设计依据；论文测试结果不能作为本书自测结果。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://arxiv.org/abs/2309.06180`

<a id="ref-r03"></a>
### R03 Dao 等：FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness（2022）

**类型：**原始论文。**原稿登记日：**2026-09-29。

**使用范围：**注意力计算中的数据移动与 IO 感知方法。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://arxiv.org/abs/2205.14135`

<a id="ref-r04"></a>
### R04 Hugging Face Transformers：Cache strategies

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**不同状态缓存策略的实现与限制；须对应模型及运行版本。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://huggingface.co/docs/transformers/en/kv_cache`

<a id="ref-r05"></a>
### R05 DeepSeek-AI：DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model（2024）

**类型：**原始论文。**原稿登记日：**2026-09-29。

**使用范围：**MLA、MoE 结构原理的实例，不作为所有模型的结构假设。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://arxiv.org/abs/2405.04434`

<a id="ref-r06"></a>
### R06 Zheng 等：SGLang: Efficient Execution of Structured Language Model Programs

**类型：**原始论文。**原稿登记日：**2026-09-29。

**使用范围：**结构化程序执行、前缀复用与调度相关设计。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://arxiv.org/abs/2312.07104`

<a id="ref-r07"></a>
### R07 vLLM：Automatic Prefix Caching（设计文档）

**类型：**官方设计文档。**原稿登记日：**2026-09-29。

**使用范围：**缓存块身份与前缀复用机制；功能和配置按版本复核。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/en/stable/design/prefix_caching/`

<a id="ref-r08"></a>
### R08 NVIDIA NCCL：Collective Operations

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**集合通信语义；性能仍取决于拓扑、消息大小与实现。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html`

<a id="ref-r09"></a>
### R09 Zhong 等：DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving（2024）

**类型：**原始论文。**原稿登记日：**2026-09-29。

**使用范围：**P/D 分离、阶段干扰、通信约束与 Goodput 优化的研究实例。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://arxiv.org/abs/2401.09670`

<a id="ref-r10"></a>
### R10 SGLang：PD Disaggregation

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**分离式推理的实现入口；部署命令与支持范围需要实验时锁定版本。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.sglang.io/docs/advanced_features/pd_disaggregation`

<a id="ref-r11"></a>
### R11 NVIDIA：GenAI-Perf

**类型：**官方工具文档。**原稿登记日：**2026-09-29。

**使用范围：**负载控制、发压参数和输出指标的工具参考。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html`

<a id="ref-r12"></a>
### R12 NVIDIA AIPerf：Metrics Reference

**类型：**官方工具文档。**原稿登记日：**2026-09-29。

**使用范围：**客户端指标定义与统计处理；不得默认与其他工具完全相同。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference`

<a id="ref-r13"></a>
### R13 NVIDIA AIPerf：Migrating from GenAI-Perf

**类型：**官方迁移文档。**原稿登记日：**2026-09-29。

**使用范围：**工具迁移与版本变化的核验入口，不表示旧工具已经停止使用。

**别名：**与 [S17](#ref-s17) 为同一迁移文档入口；具体TTFT/TTFO条件已纳入第7章和附录B。

**原始入口：**`https://docs.nvidia.com/aiperf/getting-started/migrating-from-gen-ai-perf`

<a id="ref-r14"></a>
### R14 MLCommons：MLPerf Inference Datacenter

**类型：**官方基准文档。**原稿登记日：**2026-09-29。

**使用范围：**受质量、场景与延迟要求约束的基准思路；本书自定义实验不是 MLPerf 认证结果。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://mlcommons.org/benchmarks/inference-datacenter/`

<a id="ref-r15"></a>
### R15 Prometheus：Histograms and summaries

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**直方图、分位数与聚合限制。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://prometheus.io/docs/practices/histograms/`

<a id="ref-r16"></a>
### R16 PyTorch：torch.profiler

**类型：**官方 API 文档。**原稿登记日：**2026-09-29。

**使用范围：**执行活动、时间线与剖析工具；stable 为浮动入口，实验必须另存版本。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.pytorch.org/docs/stable/profiler.html`

<a id="ref-r17"></a>
### R17 NVIDIA Nsight Systems：User Guide

**类型：**官方工具文档。**原稿登记日：**2026-09-29。

**使用范围：**系统级时间线与分析功能；使用时核对设备、权限与版本。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.nvidia.com/nsight-systems/UserGuide/index.html`

<a id="ref-r18"></a>
### R18 OpenTelemetry：Semantic Conventions for Generative AI

**类型：**官方项目仓库。**原稿登记日：**2026-09-29。

**使用范围：**GenAI 遥测语义与状态演进；字段必须带版本，不假设已稳定。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://github.com/open-telemetry/semantic-conventions-genai`

<a id="ref-r19"></a>
### R19 vLLM Ascend：Documentation

**类型：**官方项目文档。**原稿登记日：**2026-09-29。

**使用范围：**昇腾适配栈、功能与版本依赖核验入口；latest 不是实测环境身份。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/projects/ascend/en/latest/`

<a id="ref-r20"></a>
### R20 华为 MindStudio：msprof 命令行性能数据采集（26.1.0 文档入口）

**类型：**官方工具文档。**原稿登记日：**2026-09-29。

**使用范围：**原生性能采集方法；该入口版本不代表读者环境或本书已验证环境。

**修订状态：**SOURCE_ENTRY_ONLY；复核未取得支持具体命令/能力的正文。以 [S24](#ref-s24) 的缺口登记为准。

**原始入口：**`https://www.hiascend.com/document/detail/zh/mindstudio/2610/msTT_msIT/msProf/docs/zh/profiling/msprof_cmd/ai_runtime_profile_data.md`

<a id="ref-r21"></a>
### R21 AMD HIP：Performance optimization（7.14.0 文档入口）

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**GPU 性能分析思路及平台工具；不可直接映射为其他硬件的计数器语义。

**修订状态：**历史版本参考，不是整套ROCm或当前环境认证；参见 [S23](#ref-s23)。

**原始入口：**`https://rocm.docs.amd.com/projects/HIP/en/docs-7.14.0/understand/performance_optimization.html`

<a id="ref-r22"></a>
### R22 Lawrence Berkeley National Laboratory：Roofline Performance Model

**类型：**研究机构原始资料。**原稿登记日：**2026-09-29。

**使用范围：**Roofline 的计算与带宽约束框架。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://amcr.lbl.gov/departments/computer-science-department/ppan/roofline-performance-model/`

<a id="ref-r23"></a>
### R23 NVIDIA TensorRT-LLM：Overview

**类型：**官方项目文档。**原稿登记日：**2026-09-29。

**使用范围：**推理软件栈与执行优化的实现参考，不据此推断跨平台性能排名。

**别名：**与 [S05](#ref-s05) 为同一文档入口；实现行为仍需固定版本。

**原始入口：**`https://nvidia.github.io/TensorRT-LLM/overview.html`

<a id="ref-r24"></a>
### R24 Google SRE：Service Level Objectives

**类型：**原作者公开书籍。**原稿登记日：**2026-09-29。

**使用范围：**从用户需求定义服务指标与目标；本书成本核算模板为自拟工程方法。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://sre.google/sre-book/service-level-objectives/`

<a id="ref-r25"></a>
### R25 Google SRE：Handling Overload

**类型：**原作者公开书籍。**原稿登记日：**2026-09-29。

**使用范围：**过载、准入和退化处理的工程背景。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://sre.google/sre-book/handling-overload/`

<a id="ref-r26"></a>
### R26 vLLM：Quantization

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**量化方法与硬件、模型、后端支持限制的核验入口。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/en/stable/features/quantization/`

<a id="ref-r27"></a>
### R27 Leviathan、Kalman、Matias：Fast Inference from Transformers via Speculative Decoding（ICML 2023）

**类型：**原始论文。**原稿登记日：**2026-09-29。

**使用范围：**推测解码的算法与正确性前提；实现变体须另外核验。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://proceedings.mlr.press/v202/leviathan23a.html`

<a id="ref-r28"></a>
### R28 vLLM：Hybrid KV Cache Manager

**类型：**官方设计文档。**原稿登记日：**2026-09-29。

**使用范围：**混合层结构下的状态管理，不适用单一全注意力缓存公式的情形。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/en/stable/design/hybrid_kv_cache_manager/`

<a id="ref-r29"></a>
### R29 Hugging Face Transformers：Chat templates

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**聊天模板、特殊 Token 与输入格式。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://huggingface.co/docs/transformers/en/chat_templating`

<a id="ref-r30"></a>
### R30 vLLM：Parallelism and Scaling

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**并行部署的实现参考；可用策略需对照模型、硬件和版本。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/en/stable/serving/parallelism_scaling/`

<a id="ref-r31"></a>
### R31 vLLM：torch.compile integration

**类型：**官方设计文档。**原稿登记日：**2026-09-29。

**使用范围：**编译、图执行与运行版本相关的执行机制。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.vllm.ai/en/stable/design/torch_compile/`

<a id="ref-r32"></a>
### R32 SGLang：HiCache

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**分层缓存设计与实现入口；介质、后端和部署限制另行锁定。

**状态边界：**原稿来源入口；浮动实现需进一步固化正文和版本。

**原始入口：**`https://docs.sglang.ai/advanced_features/hicache.html`

<a id="ref-r33"></a>
### R33 华为 CANN：HCCL 用户指南（8.5.0 alpha002 文档入口）

**类型：**官方文档。**原稿登记日：**2026-09-29。

**使用范围：**昇腾集合通信的原生参考；该特定文档版本不是通用兼容性结论。

**修订状态：**SOURCE_ENTRY_ONLY；复核未取得支持具体命令/能力的正文。以 [S25](#ref-s25) 的缺口登记为准。

**原始入口：**`https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850alpha002/hccl/hcclug`

## S系列：版本化实现与复核来源

<a id="ref-s01"></a>
### S01 vLLM v0.29.0 release

**类型：**发布说明。**发布/版本日：**2026-09-09。**复核记录查阅日：**2026-09-29。

**支持范围：**Model Runner V2 默认化；保留部分回退；旧入口弃用。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://github.com/vllm-project/vllm/releases/tag/v0.29.0`

<a id="ref-s02"></a>
### S02 vLLM v0.30.0 release

**类型：**发布说明。**发布/版本日：**2026-09-22。**复核记录查阅日：**2026-09-29。

**支持范围：**Fast Start、HiSparse、具体模型缓存布局、推测解码与并行组合。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://github.com/vllm-project/vllm/releases/tag/v0.30.0`

<a id="ref-s03"></a>
### S03 SGLang releases

**类型：**滚动发布页。**发布/版本日：**2026-09-18（v0.5.20）。**复核记录查阅日：**2026-09-29。

**支持范围：**CPU-only Simulator、Responses 存储变更、Prefill CP v1 移除。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://github.com/sgl-project/sglang/releases`

<a id="ref-s04"></a>
### S04 TensorRT-LLM v1.3.0rc28

**类型：**预发布说明。**发布/版本日：**2026-09-23。**复核记录查阅日：**2026-09-29。

**支持范围：**RC 状态、遗留 TensorRT 服务入口清理、已知问题。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://github.com/NVIDIA/TensorRT-LLM/releases/tag/v1.3.0rc28`

<a id="ref-s05"></a>
### S05 TensorRT-LLM Overview

**类型：**浮动官方文档。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**当前文档体系及新执行、缓存和部署主题；不能单凭目录认定所有功能成熟。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://nvidia.github.io/TensorRT-LLM/overview.html`

<a id="ref-s06"></a>
### S06 NVIDIA Dynamo v1.5.0

**类型：**GA 发布说明。**发布/版本日：**2026-09-18。**复核记录查阅日：**2026-09-29。

**支持范围：**服务控制层、依赖固定版本、KVBM 弃用与 AISimulate 更名。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://docs.dynamo.nvidia.com/dynamo/reference/releases/v1-5-0`

<a id="ref-s07"></a>
### S07 llm-d v0.9: Hardened for Scale

**类型：**维护者发布说明。**发布/版本日：**2026-08-28。**复核记录查阅日：**2026-09-29。

**支持范围：**路由高可用、受限流控、插件生命周期、版本路由及 KEDA 演进。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://llm-d.ai/blog/llm-d-v0.9-hardened-for-scale`

<a id="ref-s08"></a>
### S08 FlashAttention official repository

**类型：**浮动官方仓库。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**FlashAttention-4 的 CuTeDSL 实现与 Hopper/Blackwell 目标。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://github.com/Dao-AILab/flash-attention`

<a id="ref-s09"></a>
### S09 FlashInfer official repository

**类型：**浮动官方仓库。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**Attention、GEMM、MoE 内核及多后端执行。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://github.com/flashinfer-ai/flashinfer`

<a id="ref-s10"></a>
### S10 Introducing NVFP4

**类型：**厂商技术说明。**发布/版本日：**2025-06-24。**复核记录查阅日：**2026-09-29。

**支持范围：**NVFP4 数据及缩放表示；不采用宣传性性能倍数作为本书结果。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/`

<a id="ref-s11"></a>
### S11 DeepSeek-V4.1-Flash model card

**类型：**作者模型卡。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**CED、CSA2、跨层状态与模型侧 FP4 主 KV 描述。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash`

<a id="ref-s12"></a>
### S12 Qwen3.8-Flash-Next model card

**类型：**作者模型卡／实验预览。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**Gated DeltaNet 与 QSA 混合结构；官方明确实验预览。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://huggingface.co/Qwen/Qwen3.8-Flash-Next`

<a id="ref-s13"></a>
### S13 LMCache documentation

**类型：**浮动官方文档。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**独立多进程缓存、分层持久化、非前缀复用及兼容性入口。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://docs.lmcache.ai/`

<a id="ref-s14"></a>
### S14 Mooncake official repository

**类型：**浮动官方仓库。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**Transfer Engine 与 Store 是不同组件；拓扑、存储及状态传输。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://github.com/kvcache-ai/Mooncake`

<a id="ref-s15"></a>
### S15 NIXL official repository

**类型：**浮动官方仓库。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**点到点推理状态传输及内存、存储后端抽象。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://github.com/ai-dynamo/nixl`

<a id="ref-s16"></a>
### S16 DeepEP official repository

**类型：**浮动官方仓库。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**V2 ElasticBuffer、dispatch/combine 与通信计算依赖。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://github.com/deepseek-ai/DeepEP`

<a id="ref-s17"></a>
### S17 AIPerf: Migrating from GenAI-Perf

**类型：**浮动官方文档。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**推理 Token 导致 TTFT/TTFO 与长度字段的迁移差异。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://docs.nvidia.com/aiperf/getting-started/migrating-from-gen-ai-perf`

<a id="ref-s18"></a>
### S18 AIPerf: Conversation DAG Benchmarks

**类型：**浮动官方文档。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**分支会话、FORK/SPAWN 以及当前树形拓扑等限制。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://docs.nvidia.com/aiperf/benchmark-modes/conversation-dag-benchmarks`

<a id="ref-s19"></a>
### S19 vLLM Ascend v0.23.0.post1

**类型：**正式维护版。**发布/版本日：**2026-09-22（GitHub 显示；正文署 09-21）。**复核记录查阅日：**2026-09-29。

**支持范围：**与 RC 路线分开记录，不按最大版本号推断正式状态。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://github.com/vllm-project/vllm-ascend/releases/tag/v0.23.0.post1`

<a id="ref-s20"></a>
### S20 vLLM Ascend v0.26.0rc1

**类型：**模型受限预发布。**发布/版本日：**2026-09-03。**复核记录查阅日：**2026-09-29。

**支持范围：**限定模型验证范围、CANN 9.1.0 依赖及 FlashComm2 等移除。

**前次复核登记：**正文核验 `true`；本地运行 `false`。

**原始入口：**`https://github.com/vllm-project/vllm-ascend/releases/tag/v0.26.0rc1`

<a id="ref-s21"></a>
### S21 NVIDIA GB300 NVL72 product page

**类型：**官方产品页。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**机柜级 GPU/CPU 与 NVLink 域；不把营销预测倍数作为实测。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://www.nvidia.com/en-us/data-center/gb300-nvl72/`

<a id="ref-s22"></a>
### S22 AMD Instinct MI350 series product page

**类型：**官方产品页。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**MI350X/MI355X 与低精度规格示例；不声称是 AMD 最新全部产品。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://www.amd.com/en/products/accelerators/instinct/mi350.html`

<a id="ref-s23"></a>
### S23 HIP performance optimization 7.14.0 path

**类型：**版本化官方文档。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**页面有效且有非最新版本提示；URL 的组件版本不等于整套栈认证。

**前次复核登记：**正文核验 `true`；本地运行 `false`。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://rocm.docs.amd.com/projects/HIP/en/docs-7.14.0/understand/performance_optimization.html`

<a id="ref-s24"></a>
### S24 MindStudio msprof 26.1.0 entry

**类型：**官方入口／正文未取得。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**本轮工具仅返回站点框架，不能据此核验具体命令。

**前次复核登记：**正文核验 `false`；本地运行 `false`。仅保留入口，不用其推断具体命令、最新版本或兼容能力。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://www.hiascend.com/document/detail/zh/mindstudio/2610/msTT_msIT/msProf/docs/zh/profiling/msprof_cmd/ai_runtime_profile_data.md`

<a id="ref-s25"></a>
### S25 CANN 8.5.0 alpha002 HCCL entry

**类型：**官方入口／正文未取得。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**本轮未取得实质正文；历史 alpha 入口不能证明当前兼容性。

**前次复核登记：**正文核验 `false`；本地运行 `false`。仅保留入口，不用其推断具体命令、最新版本或兼容能力。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850alpha002/hccl/hcclug`

<a id="ref-s26"></a>
### S26 Huawei MindIE product entry

**类型：**官方入口／正文未取得。**发布/版本日：**未单独固定，不能用查阅日代替。**复核记录查阅日：**2026-09-29。

**支持范围：**跳转至 /cn/developer/software/mindie；本轮未取得正文，不给出最新版本或能力结论。

**前次复核登记：**正文核验 `false`；本地运行 `false`。仅保留入口，不用其推断具体命令、最新版本或兼容能力。浮动来源在正式扩写前仍需固定commit或存档。

**原始入口：**`https://www.hiascend.com/software/mindie`
