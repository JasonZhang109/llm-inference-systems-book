#!/usr/bin/env python3
"""E0 reference calculations. Standard library only; no inference or hardware calls.

Run: python book_support_v05/code/e0_reference.py --output book_support_v05/data
Each JSON result identifies a deterministic calculation, NOT a GPU experiment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import platform
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


def finite(x: float, name: str = 'value') -> float:
    if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x):
        raise ValueError(f'{name} must be a finite number')
    return float(x)


def integer(x: int, name: str, minimum: int = 0) -> int:
    if type(x) is not int or x < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return x


@dataclass(frozen=True)
class Event:
    time_ms: float
    clock_domain: str


def elapsed(start: Event, end: Event) -> float:
    """Local-domain difference. No implicit cross-host clock alignment."""
    if not start.clock_domain or start.clock_domain != end.clock_domain:
        raise ValueError('clock domains differ or are unspecified')
    duration = finite(end.time_ms) - finite(start.time_ms)
    if duration < 0:
        raise ValueError('time runs backwards')
    return duration


def tpot(first: Event, last: Event, output_tokens: int) -> float | None:
    integer(output_tokens, 'output_tokens')
    if output_tokens <= 1:
        return None
    return elapsed(first, last) / (output_tokens - 1)


def event_intervals(events: Sequence[Event]) -> list[float]:
    return [elapsed(a, b) for a, b in zip(events, events[1:])]


def quantile(values: Sequence[float], q: float, method: str = 'inverted_cdf') -> float:
    """Nearest-rank/inverted CDF or NumPy-style linear (Hyndman-Fan type 7)."""
    q = finite(q, 'q')
    if not 0 <= q <= 1 or not values:
        raise ValueError('require 0 <= q <= 1 and a nonempty sample')
    xs = sorted(finite(x) for x in values)
    if method == 'inverted_cdf':
        return xs[max(0, math.ceil(q * len(xs)) - 1)]
    if method == 'linear':
        position = (len(xs) - 1) * q
        lo = math.floor(position)
        hi = min(lo + 1, len(xs) - 1)
        return xs[lo] + (position - lo) * (xs[hi] - xs[lo])
    raise ValueError('unknown quantile method')


def kv_token_bytes(layers: int, kv_heads: int, head_dim: int, element_bytes: int = 2) -> int:
    for k, v in [('layers', layers), ('kv_heads', kv_heads), ('head_dim', head_dim), ('element_bytes', element_bytes)]:
        integer(v, k, 1)
    return 2 * layers * kv_heads * head_dim * element_bytes


def rank_kv_bytes(logical_bytes: int, kv_heads: int, tp: int) -> int:
    """Head sharding with head replication if TP>heads; only divisible layouts.
    Does not model context parallelism, alternative backends, padding or metadata.
    """
    integer(logical_bytes, 'logical_bytes'); integer(kv_heads, 'kv_heads', 1); integer(tp, 'tp', 1)
    shards = min(kv_heads, tp)
    if max(kv_heads, tp) % shards or logical_bytes % shards:
        raise ValueError('this reference model requires divisible head sharding')
    return logical_bytes // shards


def block_allocation(tokens: int, block_tokens: int, bytes_per_token: int) -> tuple[int, int]:
    integer(tokens, 'tokens'); integer(block_tokens, 'block_tokens', 1); integer(bytes_per_token, 'bytes_per_token', 1)
    blocks = (tokens + block_tokens - 1) // block_tokens
    return blocks * block_tokens * bytes_per_token, (blocks * block_tokens - tokens) * bytes_per_token


def causal_pairs(history: int, new: int) -> int:
    integer(history, 'history'); integer(new, 'new')
    return new * history + new * (new + 1) // 2


def progress(alpha: float, candidates: int) -> float:
    alpha = finite(alpha, 'alpha'); integer(candidates, 'candidates')
    if not 0 <= alpha <= 1:
        raise ValueError('alpha must be in [0,1]')
    return sum(alpha ** i for i in range(candidates + 1))


def exact_spec_distribution(target: Sequence[float], draft: Sequence[float]) -> list[float]:
    """Enumerate one exact speculative step, including residual correction.
    Result is a distribution, NOT Monte Carlo output or a speed measurement.
    """
    if len(target) != len(draft) or not target:
        raise ValueError('distribution dimensions differ')
    p = [finite(x) for x in target]; q = [finite(x) for x in draft]
    if min(p + q) < 0 or not math.isclose(sum(p), 1) or not math.isclose(sum(q), 1):
        raise ValueError('invalid probability distribution')
    accepted = [min(x, y) for x, y in zip(p, q)]
    residual = [max(x-y, 0) for x, y in zip(p, q)]
    mass = sum(residual)
    if mass <= 1e-15:
        return accepted
    rejection = 1 - sum(accepted)
    return [a + rejection * r / mass for a, r in zip(accepted, residual)]


def dag_finish(nodes: dict[str, tuple[float, Sequence[str]]]) -> dict[str, float]:
    pending = dict(nodes); done: dict[str, float] = {}
    for name, (duration, deps) in pending.items():
        if finite(duration) < 0 or any(d not in nodes for d in deps):
            raise ValueError(f'invalid node {name}')
    while pending:
        ready = [n for n, (_, deps) in pending.items() if all(d in done for d in deps)]
        if not ready:
            raise ValueError('dependency cycle')
        for name in ready:
            duration, deps = pending.pop(name)
            done[name] = duration + max((done[d] for d in deps), default=0)
    return done


def interval_union(intervals: Iterable[tuple[float, float]], start: float, end: float) -> float:
    start, end = finite(start), finite(end)
    if end < start:
        raise ValueError('invalid window')
    clipped = []
    for a, b in intervals:
        a, b = finite(a), finite(b)
        if b < a:
            raise ValueError('negative interval')
        a, b = max(a, start), min(b, end)
        if b > a:
            clipped.append((a, b))
    total = 0.; right = start
    for a, b in sorted(clipped):
        total += max(0., b - max(a, right)); right = max(right, b)
    return total


def mg1_wait(arrival_rate: float, mean_service: float, cv_squared: float) -> float:
    lam, s, cv = finite(arrival_rate), finite(mean_service), finite(cv_squared)
    rho = lam * s
    if min(lam, cv) < 0 or s <= 0 or rho >= 1:
        raise ValueError('require nonnegative inputs and stable rho<1')
    return lam * s * s * (1 + cv) / (2 * (1-rho))


def control_delay(period: float, confirmations: int, startup: float) -> tuple[float, float]:
    period, startup = finite(period), finite(startup); integer(confirmations, 'confirmations', 1)
    if period <= 0 or startup < 0:
        raise ValueError('invalid timing parameters')
    lo = (confirmations-1) * period + startup
    return lo, lo + period


def replicas(demand: float, per_replica: float, unavailable: int = 1) -> int:
    demand, per_replica = finite(demand), finite(per_replica); integer(unavailable, 'unavailable')
    if demand < 0 or per_replica <= 0:
        raise ValueError('invalid capacity')
    return math.ceil(demand / per_replica) + unavailable


def make_tp_rows() -> list[dict]:
    rows = []
    for tp in [8, 4, 2]:
        pool = int(80e9 - 140e9 / tp - 4e9)
        seq = rank_kv_bytes(512 * 2**20, 8, tp)
        slots = pool // seq
        rows.append(dict(tp=tp, replicas=8//tp, pool_bytes_per_rank=pool, kv_bytes_per_rank=seq,
                         slots_per_replica=slots, cluster_slots=slots*(8//tp), run_type='SYNTHETIC_CALCULATION'))
    return rows


def run_tests() -> list[dict]:
    results: list[dict] = []
    def check(name: str, chapter: str, fn: Callable, expected, tol: float = 1e-8):
        try:
            actual = fn()
            def matches(a, b):
                if isinstance(b, float): return isinstance(a,(int,float)) and math.isclose(a,b,rel_tol=tol,abs_tol=tol)
                if isinstance(b, (list, tuple)): return len(a)==len(b) and all(matches(x,y) for x,y in zip(a,b))
                return a == b
            ok = matches(actual, expected)
            results.append(dict(test=name, chapters=chapter, status='PASS' if ok else 'FAIL', expected=expected, actual=actual))
        except Exception as exc:
            results.append(dict(test=name, chapters=chapter, status='FAIL', error=str(exc), expected=expected))
    def raises(fn):
        try: fn()
        except ValueError: return True
        return False
    s=lambda t: Event(t,'server')
    check('TTFT_server_ms','1,7',lambda: elapsed(s(21),s(634)),613.)
    check('E2E_content_ms','1,7',lambda: elapsed(s(21),s(4210)),4189.)
    check('E2E_terminal_ms','1,7',lambda: elapsed(s(21),s(4213)),4192.)
    check('TPOT_content_ms','7',lambda: tpot(s(634),s(4210),301),11.92)
    check('TPOT_terminal_ms','7',lambda: tpot(s(634),s(4213),301),11.93)
    check('TPOT_one_token_null','7',lambda: tpot(s(1),s(2),1),None)
    check('TPOT_zero_token_null','7',lambda: tpot(s(1),s(2),0),None)
    check('reject_cross_domain','1,7',lambda: raises(lambda: elapsed(s(1),Event(2,'client'))),True)
    check('reject_reversed_time','1,7',lambda: raises(lambda: elapsed(s(2),s(1))),True)
    check('event_interval_no_token_interpolation','7',lambda:event_intervals([s(1),s(11),s(41)]),[10.,30.])
    check('empty_stream_no_intervals','7',lambda:event_intervals([]),[])
    check('reject_negative_count','7',lambda:raises(lambda:tpot(s(1),s(2),-1)),True)
    xs=[100.]*999+[5000.]
    check('P999_inverted_cdf','7',lambda:quantile(xs,.999),100.)
    check('P999_linear','7',lambda:quantile(xs,.999,'linear'),104.9,tol=1e-7)
    check('P9995_inverted_cdf','7',lambda:quantile(xs,.9995),5000.)
    check('quantile_min','7',lambda:quantile(xs,0),100.)
    check('quantile_max','7',lambda:quantile(xs,1),5000.)
    check('reject_empty_quantile','7',lambda:raises(lambda:quantile([], .5)),True)
    check('reject_nan_quantile','7',lambda:raises(lambda:quantile([float('nan')],.5)),True)
    a=[100.]*98+[1000.]*2; b=[500.]*100
    check('mean_local_P99_not_global','7',lambda:(quantile(a,.99)+quantile(b,.99))/2,750.)
    check('pooled_P99','7',lambda:quantile(a+b,.99),500.)
    check('joint_lower_bound','7',lambda:max(0,.95+.95-1),.90)
    check('three_positive_sign_test_two_sided','8',lambda:2*(.5**3),.25)
    check('paired_mean_difference','8',lambda:statistics.mean([.29,.04,.44]),.77/3)
    check('toy_KV_bytes_per_token','2,4',lambda:kv_token_bytes(32,8,128),131072)
    check('toy_4096_KV_MiB','2,4',lambda:kv_token_bytes(32,8,128)*4096/2**20,512.)
    check('Qwen25_config_KiB','2',lambda:kv_token_bytes(28,4,128)/1024,56.)
    check('Qwen25_4096_MiB','2',lambda:kv_token_bytes(28,4,128)*4096/2**20,224.)
    check('DSV3_compressed_MLA_KiB','2',lambda:61*(512+64)*2/1024,68.625)
    check('KV_replication_TP8_h4','4',lambda:rank_kv_bytes(4*2**30,4,8),2**30)
    check('reject_nondivisible_heads','4',lambda:raises(lambda:rank_kv_bytes(100,3,8)),True)
    check('blocks_aligned_zero_waste','4',lambda:block_allocation(4096,16,131072)[1],0)
    check('blocks_4097_waste_KiB','4',lambda:block_allocation(4097,16,131072)[1]/1024,1920.)
    check('empty_sequence_zero_blocks','4',lambda:block_allocation(0,16,131072),(0,0))
    check('causal_pairs_128','2',lambda:causal_pairs(0,128),8256)
    check('causal_pairs_prefix4096_new128','2',lambda:causal_pairs(4096,128),532544)
    check('causal_pairs_all4224','2',lambda:causal_pairs(0,4224),8923200)
    check('causal_pairs_ratio_rounded_1dp','2',lambda:round(causal_pairs(4096,128)/causal_pairs(0,128),1),64.5)
    check('dense_linear_4096_TFLOP','2',lambda:2*7e9*4096/1e12,57.344)
    check('full_attention_4096_TFLOP','2',lambda:4*32*4096**2*4096/1e12,8.796093022208)
    check('GEMM_flops','3',lambda:2*8*4096**2,268435456)
    check('GEMM_bytes','3',lambda:2*(4096**2+2*8*4096),33685504)
    check('GEMM_bandwidth_bound_us','3',lambda:33685504/2e12*1e6,16.842752)
    check('exact_roof_ridge_minimum_M','3',lambda:math.ceil(500*4096/(4096-1000)),662)
    check('phasewise_bounds_are_stronger','3',lambda:max(10,1)+max(1,10),20)
    check('aggregated_bound_weak','3',lambda:max(10+1,1+10),11)
    check('Amdahl_speedup','3',lambda:1/(.9+.1/2),1/.95)
    check('Amdahl_latency_reduction','3',lambda:1-(.9+.1/2),.05)
    for row in make_tp_rows():
        expected={8:(871,871),4:(305,610),2:(22,88)}[row['tp']]
        check(f'TP{row["tp"]}_capacity','6',lambda r=row:(r['slots_per_replica'],r['cluster_slots']),expected)
    nodes={'S1':(.08,[]),'S2':(.35,['S1']),'S3':(.9,['S2']),'S4':(.6,['S3']),
           'S5':(1.2,['S4']),'S6':(3.1,['S5']),'S7':(.45,['S2']),
           'S8':(.12,['S6','S7']),'S9':(.35,['S8'])}
    check('DAG_e2e_seconds','1',lambda:dag_finish(nodes)['S9'],6.70)
    check('DAG_tool_end_seconds','1',lambda:dag_finish(nodes)['S7'],.88)
    reduced=dict(nodes);reduced['S6']=(3.1*.7,['S5'])
    check('DAG_decode30pct','1',lambda:dag_finish(reduced)['S9'],5.77)
    zero=dict(nodes);zero['S6']=(0,['S5'])
    check('DAG_decode_zero','1',lambda:dag_finish(zero)['S9'],3.6)
    check('reject_DAG_cycle','1',lambda:raises(lambda:dag_finish({'a':(1,['b']),'b':(1,['a'])})),True)
    intervals=[(134,141),(141,600),(600,620),(641,900),(1180,4210)]
    check('device_union_ms','9',lambda:interval_union(intervals,21,4210),3775.)
    check('device_idle_ms','9',lambda:4189-interval_union(intervals,21,4210),414.)
    check('overlap_not_double_counted','9',lambda:interval_union([(0,10),(5,15)],0,20),15.)
    check('union_clips_window','9',lambda:interval_union([(-10,10),(18,30)],0,20),12.)
    check('sample_30_at_1pct','9',lambda:1-.99**30,0.2602996266117198)
    check('sample_30_at_5pct','9',lambda:1-.95**30,0.7853612360570628)
    check('non_matrix_busy_time','9',lambda:288-126,162)
    check('idle_separate_time','9',lambda:300-288,12)
    check('spec_drafts_07_k4','2,11',lambda:progress(.7,4)-1,1.7731)
    check('spec_progress_07_k4','2,11',lambda:progress(.7,4),2.7731)
    check('spec_alpha0','11',lambda:progress(0,4),1.)
    check('spec_alpha1','11',lambda:progress(1,4),5.)
    check('spec_k0','11',lambda:progress(.7,0),1.)
    check('reject_bad_acceptance','11',lambda:raises(lambda:progress(1.1,4)),True)
    check('spec_exact_distribution','11',lambda:exact_spec_distribution([.2,.3,.5],[.5,.4,.1]),[.2,.3,.5])
    check('spec_draft_zero_support','11',lambda:exact_spec_distribution([.2,.3,.5],[.6,.4,0]),[.2,.3,.5])
    check('spec_identical_distributions','11',lambda:exact_spec_distribution([.2,.8],[.2,.8]),[.2,.8])
    check('request_graph_fallback_not_iteration','11',lambda:1-.96**100,0.9831296806411504)
    check('AB_interaction_tokens_s','11',lambda:1150-1120-1080+1000,-50)
    check('NVFP4_block_effective_bits','3,11',lambda:4+8/16,4.5)
    check('MXFP4_block_effective_bits','11',lambda:4+8/32,4.25)
    check('handoff_minimum_GBs','12',lambda:2**30/.08/1e9,13.4217728)
    check('DistServe_ideal_GPU_normalized_NOT_MEASURED','12',lambda:min(2*5.6,10)/3,10/3)
    for cv, expected in [(0,.04),(1,.08),(4,.20)]:
        check(f'MG1_CV2_{cv}_mean_wait_s','5',lambda cv=cv:mg1_wait(40,.02,cv),expected)
    check('reject_unstable_queue','5',lambda:raises(lambda:mg1_wait(50,.02,1)),True)
    check('finite_window_inflight_balance','5,16',lambda:8+120-100-5,23)
    check('burst_backlog_requests','16',lambda:(40-25)*60,900)
    check('burst_recovery_seconds','16',lambda:900/(25-20),180.)
    check('scale_out_delay_range','16',lambda:control_delay(15,3,115),(145.,160.))
    check('one_confirmation_delay','16',lambda:control_delay(15,1,115),(115.,130.))
    check('Nplus1_baseline_replicas','16,17',lambda:replicas(35,8),6)
    check('Nplus1_candidate_replicas','17',lambda:replicas(35,10),5)
    check('board_yearly_energy_cost','17',lambda:5.6*8760*.8,39244.8)
    check('system_yearly_energy_cost','17',lambda:9.8*8760*.8,68678.4)
    check('net_simple_payback_months','17',lambda:36000/(122640-8000)*12,432000/114640)
    check('first_year_net_saving','17',lambda:122640-8000-36000,78640)
    check('maintenance_sensitivity','17',lambda:60000/44000-1,4/11)
    check('throughput30_not_resource30','17',lambda:1-1/1.3,3/13)
    check('unit_effective_task_cost','17',lambda:96/1000,.096)
    check('multi_test_false_alarm_example','18',lambda:1-.95**20,0.6415140775914581)
    return results


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path, default=Path(__file__).resolve().parents[1]/'data')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    results=run_tests()
    report=dict(run_type='E0_CALCULATION_TEST', hardware_experiments_executed=False,
                python_version=platform.python_version(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                total=len(results), passed=sum(r['status']=='PASS' for r in results),
                failed=sum(r['status']=='FAIL' for r in results), results=results)
    (args.output/'e0_test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output/'tp_capacity.json').write_text(json.dumps(make_tp_rows(),ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# E0 计算测试记录','',f'Python {report["python_version"]}；{report["passed"]}/{report["total"]} 项通过。',
           '','这里只验证列明的算术与参考实现；不表示全部书稿、硬件性能或推理服务已经验证。','',
           '| 测试 | 章节 | 状态 | 实际结果 |','|---|---|---|---|']
    lines += [f'| {r["test"]} | {r["chapters"]} | {r["status"]} | `{r.get("actual",r.get("error"))}` |' for r in results]
    (args.output/'e0_test_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['run_type','total','passed','failed']},ensure_ascii=False))
    for r in results:
        if r['status']=='FAIL': print(r)
    return 0 if report['failed']==0 else 1


if __name__=='__main__':
    sys.exit(main())
