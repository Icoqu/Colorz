from PIL import Image
from collections import namedtuple
from math import sqrt
import random


def dominant_colour(file_path: str, colors: int):
    im = Image.open(file_path)
    out = im.convert("P", palette=Image.ADAPTIVE, colors=colors).convert('RGB')

    return tuple("#{:02x}{:02x}{:02x}".format(*rgb_tuple) for c, rgb_tuple in out.getcolors())


def k_means(file_path: str, colors: int):
    Point = namedtuple('Point', ('coords', 'n', 'ct'))
    Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

    def get_points(img):
        points = []
        w, h = img.size
        for count, color in img.getcolors(w * h):
            points.append(Point(color, 3, count))
        return points

    def euclidean(p1, p2):
        return sqrt(sum([
            (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
        ]))

    def calculate_center(points, n):
        vals = [0.0 for i in range(n)]
        plen = 0
        for p in points:
            plen += p.ct
            for i in range(n):
                vals[i] += (p.coords[i] * p.ct)
        return Point([(v / plen) for v in vals], n, 1)

    def kmeans(points, k, min_diff):
        clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

        while 1:
            plists = [[] for i in range(k)]

            for p in points:
                smallest_distance = float('Inf')
                for i in range(k):
                    distance = euclidean(p, clusters[i].center)
                    if distance < smallest_distance:
                        smallest_distance = distance
                        idx = i
                plists[idx].append(p)

            diff = 0
            for i in range(k):
                old = clusters[i]
                center = calculate_center(plists[i], old.n)
                new = Cluster(plists[i], center, old.n)
                clusters[i] = new
                diff = max(diff, euclidean(old.center, new.center))

            if diff < min_diff:
                break

        return clusters

    img = Image.open(file_path)
    points = get_points(img)
    clusters = kmeans(points, colors, 1)
    rgbs = [map(int, c.center.coords) for c in clusters]
    return tuple("#{:02x}{:02x}{:02x}".format(*rgb_tuple) for rgb_tuple in rgbs)


if __name__ == '__main__':
    import argparse

    class ValueException(Exception):
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--strategy', dest='strategy', default='k-means',
                        help='startegy {dominant|k-means}|{d|k}')
    parser.add_argument('-c', '--colors', dest='colors', type=int, default=3, help='number of colors')
    parser.add_argument('-f', '--file', dest='filename', help='input file', required=True)
    args = parser.parse_args()

    filename = args.filename
    colors = args.colors
    strategy = args.strategy

    if strategy == 'dominant' or strategy == 'd':
        ret = dominant_colour(filename, colors)
    elif strategy == 'k-means' or strategy == 'k':
        ret = k_means(filename, colors)
    else:
        raise ValueException('strategy should be dominant or k-means, (d or k)')

    for hex_string in ret:
        print("rgb: {}".format(hex_string))
