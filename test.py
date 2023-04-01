import math


def calculate_math(m, n, lg, x):
    z = math.log(3 - x * 2 + (5.5 + x) + math.cos(x * 2 - 3))
    u = 8 * m - 0.5 * n * 2 / 3.8 * z
    return u
