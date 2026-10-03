import re, sys, statistics as st, datetime as dt

ts = lambda l: dt.datetime.strptime(l.split()[2], "%H:%M:%S,%f")
PAUSE = re.compile(r"battle\.py:\d+: 目标图片：battle/pause_assets.png.*相似度：(0\.9|1\.0)")
GEAR = re.compile(r"battle\.py:\d+: 目标图片：battle/(gear_left|more_information_assets).png.*相似度：(0\.9|1\.0)")


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))]


for path in sys.argv[1:]:
    A, B = [], []
    last_pause = gear = None
    for l in open(path, encoding="utf-8", errors="replace"):
        if "[AALC]" not in l:
            continue
        if GEAR.search(l) and gear is None:
            gear = ts(l)
            if last_pause is not None:
                A.append((gear - last_pause).total_seconds())
            last_pause = None
        elif PAUSE.search(l):
            if gear is not None:
                B.append((ts(l) - gear).total_seconds())
                gear = None
            last_pause = ts(l)
        elif "结束执行 一次战斗" in l:
            last_pause = gear = None
    A = [a for a in A if a < 60]
    B = [b for b in B if b < 60]
    print(path.split("/")[-2])
    print(f"  A turn end -> gear seen : n={len(A):3d} median {st.median(A):5.2f}s p90 {q(A, .9):5.2f}s")
    print(f"  B gear seen -> turn runs: n={len(B):3d} median {st.median(B):5.2f}s p90 {q(B, .9):5.2f}s")
