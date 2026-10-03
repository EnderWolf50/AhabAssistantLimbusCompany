import re, sys, statistics as st, datetime as dt

def parse(path):
    steps, penter = {}, []
    for l in open(path, encoding="utf-8", errors="replace"):
        m = re.search(r"结束执行 (\S+) 耗时:(\d+):(\d+):(\d+)", l)
        if m:
            steps.setdefault(m.group(1), []).append(int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4)))
        if "使用P+Enter开始战斗" in l:
            penter.append(dt.datetime.strptime(l.split()[2], "%H:%M:%S,%f"))
    pairs = sum(1 for a, b in zip(penter, penter[1:]) if (b - a).total_seconds() < 1.5)
    return steps, len(penter), pairs

for path in sys.argv[1:]:
    steps, n, pairs = parse(path)
    print(path.split("/")[-2])
    for k in sorted(steps):
        v = steps[k]
        print(f"  {k:10s} n={len(v):2d} median={st.median(v):5.1f}s total={sum(v):5d}s")
    print(f"  P+Enter {n} 次，間隔 <1.5 s 的成對重複 {pairs} 次")
