# utils/scan_engine.py
from multiprocessing import Pool, cpu_count
from typing import Callable, Iterable, Any, List


def run_scan(
    seeds: Iterable[int],
    worker: Callable[[int], Any],
    processes: int | None = None,
    chunksize: int = 1000,
) -> List[Any]:
    """
    并行扫描通用引擎：
    - seeds: 可迭代的种子序列
    - worker(seed) -> Any: 对单个 seed 的计算逻辑（由功能模块提供）
    - processes: 进程数（默认用 cpu_count()）
    - chunksize: 每批分发给子进程的任务量（按你的任务耗时可调大一点更快）
    返回：按 seeds 顺序对应的结果列表
    """
    procs = processes or cpu_count()
    with Pool(processes=procs) as pool:
        return list(pool.imap(worker, seeds, chunksize=chunksize))
