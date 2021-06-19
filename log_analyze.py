#!/usr/bin/env python3

from collections import defaultdict, Counter
from pprint import pprint

from matplotlib import rcParams, pyplot as plt

rcParams["svg.fonttype"] = "none"


def main():
    with open("stderr.log") as f:
        lines = list(map(lambda l: l.split("\t"), map(str.strip, f)))

    pprint(len(set(map(lambda t: t[1], lines))))

    points = list(map(lambda t: (" ".join([t[0].split()[0].split("/")[-1], t[0].split()[1].split(":")[0]]), t[2][len("got list for "):]), filter(lambda t: t[2].startswith("got list for"), lines)))
    c = Counter(map(lambda p: p[1], points)).most_common()
    pprint(c)

    plots = defaultdict(lambda: defaultdict(int))
    for point in points:
        plots[point[1]][point[0]] += 1
    # pprint(plots)

    fig = plt.figure(figsize=(35, 5))
    for city, counts in plots.items():
        xs = ["%d %d" % (d, h) for d in range(14, 19) for h in range(0, 24)]
        ys = [counts[x] for x in xs]
        plt.plot(xs, ys, label=city)
    fig.autofmt_xdate()
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
