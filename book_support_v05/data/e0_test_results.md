# E0 计算测试记录

Python 3.13.5；98/98 项通过。

这里只验证列明的算术与参考实现；不表示全部书稿、硬件性能或推理服务已经验证。

| 测试 | 章节 | 状态 | 实际结果 |
|---|---|---|---|
| TTFT_server_ms | 1,7 | PASS | `613.0` |
| E2E_content_ms | 1,7 | PASS | `4189.0` |
| E2E_terminal_ms | 1,7 | PASS | `4192.0` |
| TPOT_content_ms | 7 | PASS | `11.92` |
| TPOT_terminal_ms | 7 | PASS | `11.93` |
| TPOT_one_token_null | 7 | PASS | `None` |
| TPOT_zero_token_null | 7 | PASS | `None` |
| reject_cross_domain | 1,7 | PASS | `True` |
| reject_reversed_time | 1,7 | PASS | `True` |
| event_interval_no_token_interpolation | 7 | PASS | `[10.0, 30.0]` |
| empty_stream_no_intervals | 7 | PASS | `[]` |
| reject_negative_count | 7 | PASS | `True` |
| P999_inverted_cdf | 7 | PASS | `100.0` |
| P999_linear | 7 | PASS | `104.89999999988413` |
| P9995_inverted_cdf | 7 | PASS | `5000.0` |
| quantile_min | 7 | PASS | `100.0` |
| quantile_max | 7 | PASS | `5000.0` |
| reject_empty_quantile | 7 | PASS | `True` |
| reject_nan_quantile | 7 | PASS | `True` |
| mean_local_P99_not_global | 7 | PASS | `750.0` |
| pooled_P99 | 7 | PASS | `500.0` |
| joint_lower_bound | 7 | PASS | `0.8999999999999999` |
| three_positive_sign_test_two_sided | 8 | PASS | `0.25` |
| paired_mean_difference | 8 | PASS | `0.25666666666666665` |
| toy_KV_bytes_per_token | 2,4 | PASS | `131072` |
| toy_4096_KV_MiB | 2,4 | PASS | `512.0` |
| Qwen25_config_KiB | 2 | PASS | `56.0` |
| Qwen25_4096_MiB | 2 | PASS | `224.0` |
| DSV3_compressed_MLA_KiB | 2 | PASS | `68.625` |
| KV_replication_TP8_h4 | 4 | PASS | `1073741824` |
| reject_nondivisible_heads | 4 | PASS | `True` |
| blocks_aligned_zero_waste | 4 | PASS | `0` |
| blocks_4097_waste_KiB | 4 | PASS | `1920.0` |
| empty_sequence_zero_blocks | 4 | PASS | `(0, 0)` |
| causal_pairs_128 | 2 | PASS | `8256` |
| causal_pairs_prefix4096_new128 | 2 | PASS | `532544` |
| causal_pairs_all4224 | 2 | PASS | `8923200` |
| causal_pairs_ratio_rounded_1dp | 2 | PASS | `64.5` |
| dense_linear_4096_TFLOP | 2 | PASS | `57.344` |
| full_attention_4096_TFLOP | 2 | PASS | `8.796093022208` |
| GEMM_flops | 3 | PASS | `268435456` |
| GEMM_bytes | 3 | PASS | `33685504` |
| GEMM_bandwidth_bound_us | 3 | PASS | `16.842752` |
| exact_roof_ridge_minimum_M | 3 | PASS | `662` |
| phasewise_bounds_are_stronger | 3 | PASS | `20` |
| aggregated_bound_weak | 3 | PASS | `11` |
| Amdahl_speedup | 3 | PASS | `1.0526315789473684` |
| Amdahl_latency_reduction | 3 | PASS | `0.04999999999999993` |
| TP8_capacity | 6 | PASS | `(871, 871)` |
| TP4_capacity | 6 | PASS | `(305, 610)` |
| TP2_capacity | 6 | PASS | `(22, 88)` |
| DAG_e2e_seconds | 1 | PASS | `6.7` |
| DAG_tool_end_seconds | 1 | PASS | `0.88` |
| DAG_decode30pct | 1 | PASS | `5.77` |
| DAG_decode_zero | 1 | PASS | `3.6` |
| reject_DAG_cycle | 1 | PASS | `True` |
| device_union_ms | 9 | PASS | `3775.0` |
| device_idle_ms | 9 | PASS | `414.0` |
| overlap_not_double_counted | 9 | PASS | `15.0` |
| union_clips_window | 9 | PASS | `12.0` |
| sample_30_at_1pct | 9 | PASS | `0.2602996266117198` |
| sample_30_at_5pct | 9 | PASS | `0.7853612360570628` |
| non_matrix_busy_time | 9 | PASS | `162` |
| idle_separate_time | 9 | PASS | `12` |
| spec_drafts_07_k4 | 2,11 | PASS | `1.7731` |
| spec_progress_07_k4 | 2,11 | PASS | `2.7731` |
| spec_alpha0 | 11 | PASS | `1.0` |
| spec_alpha1 | 11 | PASS | `5.0` |
| spec_k0 | 11 | PASS | `1.0` |
| reject_bad_acceptance | 11 | PASS | `True` |
| spec_exact_distribution | 11 | PASS | `[0.2, 0.3, 0.5000000000000001]` |
| spec_draft_zero_support | 11 | PASS | `[0.2, 0.3, 0.5]` |
| spec_identical_distributions | 11 | PASS | `[0.2, 0.8]` |
| request_graph_fallback_not_iteration | 11 | PASS | `0.9831296806411504` |
| AB_interaction_tokens_s | 11 | PASS | `-50` |
| NVFP4_block_effective_bits | 3,11 | PASS | `4.5` |
| MXFP4_block_effective_bits | 11 | PASS | `4.25` |
| handoff_minimum_GBs | 12 | PASS | `13.4217728` |
| DistServe_ideal_GPU_normalized_NOT_MEASURED | 12 | PASS | `3.3333333333333335` |
| MG1_CV2_0_mean_wait_s | 5 | PASS | `0.04000000000000001` |
| MG1_CV2_1_mean_wait_s | 5 | PASS | `0.08000000000000002` |
| MG1_CV2_4_mean_wait_s | 5 | PASS | `0.20000000000000004` |
| reject_unstable_queue | 5 | PASS | `True` |
| finite_window_inflight_balance | 5,16 | PASS | `23` |
| burst_backlog_requests | 16 | PASS | `900` |
| burst_recovery_seconds | 16 | PASS | `180.0` |
| scale_out_delay_range | 16 | PASS | `(145.0, 160.0)` |
| one_confirmation_delay | 16 | PASS | `(115.0, 130.0)` |
| Nplus1_baseline_replicas | 16,17 | PASS | `6` |
| Nplus1_candidate_replicas | 17 | PASS | `5` |
| board_yearly_energy_cost | 17 | PASS | `39244.8` |
| system_yearly_energy_cost | 17 | PASS | `68678.40000000001` |
| net_simple_payback_months | 17 | PASS | `3.7683182135380324` |
| first_year_net_saving | 17 | PASS | `78640` |
| maintenance_sensitivity | 17 | PASS | `0.36363636363636354` |
| throughput30_not_resource30 | 17 | PASS | `0.23076923076923084` |
| unit_effective_task_cost | 17 | PASS | `0.096` |
| multi_test_false_alarm_example | 18 | PASS | `0.6415140775914581` |
