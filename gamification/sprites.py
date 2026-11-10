import math
import random
import pygame

SUPERSAMPLE = 4  # draw large, then shrink for smooth edges


def _finish(surf, size):
    return pygame.transform.smoothscale(surf, size)


def make_boat(width, height):
    s = SUPERSAMPLE
    w, h = width * s, height * s
    k = width / 50  # line widths and radii were designed for a 50px-wide boat
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    outline = (90, 30, 30)

    hull = [(w / 2, 0), (w, h * 0.35), (w * 0.9, h), (w * 0.1, h), (0, h * 0.35)]
    pygame.draw.polygon(surf, (220, 70, 60), hull)
    pygame.draw.polygon(surf, outline, hull, max(1, round(3 * s * k)))

    deck = [(w / 2, h * 0.12), (w * 0.82, h * 0.38), (w * 0.74, h * 0.9), (w * 0.26, h * 0.9), (w * 0.18, h * 0.38)]
    pygame.draw.polygon(surf, (245, 220, 170), deck)

    cabin = pygame.Rect(w * 0.3, h * 0.45, w * 0.4, h * 0.3)
    pygame.draw.rect(surf, (255, 255, 255), cabin, border_radius=round(4 * s * k))
    pygame.draw.rect(surf, outline, cabin, max(1, round(2 * s * k)), border_radius=round(4 * s * k))
    pygame.draw.circle(surf, (110, 190, 240), cabin.center, int(w * 0.09))
    pygame.draw.circle(surf, outline, cabin.center, int(w * 0.09), max(1, round(2 * s * k)))

    return _finish(surf, (width, height))


def make_iceberg(size):
    s = SUPERSAMPLE
    d = size * s
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = cy = d / 2

    count = random.randint(8, 11)
    offset = random.uniform(0, math.tau)
    points = []
    for i in range(count):
        angle = offset + i * math.tau / count
        r = d / 2 * random.uniform(0.75, 1.0)
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    # Shadowed base, lighter top, bright highlight
    pygame.draw.polygon(surf, (140, 190, 230), points)
    top = [(cx + (x - cx) * 0.8 - d * 0.03, cy + (y - cy) * 0.8 - d * 0.03) for x, y in points]
    pygame.draw.polygon(surf, (215, 238, 255), top)
    shine = [(cx + (x - cx) * 0.45 - d * 0.08, cy + (y - cy) * 0.45 - d * 0.08) for x, y in points]
    pygame.draw.polygon(surf, (255, 255, 255), shine)
    pygame.draw.polygon(surf, (60, 110, 160), points, max(1, round(3 * s * size / 110)))

    return _finish(surf, (size, size))


def make_water(width, height):
    surf = pygame.Surface((width, height))
    surf.fill((60, 150, 215))
    rng = random.Random(1)
    wave = (140, 205, 245)
    k = width / 600  # sizes were designed for a 600px wide screen
    thickness = max(1, round(k))

    for _ in range(round(45 * width * height / (600 * 800))):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        ww = round(rng.randint(24, 44) * k)
        for dy in (-height, 0, height):
            arc = pygame.Rect(x, y + dy, ww // 2, round(10 * k))
            pygame.draw.arc(surf, wave, arc, math.pi, math.tau, thickness)
            arc.x += ww // 2
            pygame.draw.arc(surf, wave, arc, math.pi, math.tau, thickness)
    return surf
