import math
import random

import pygame

SUPERSAMPLE = 4  # draw large, then shrink for smooth edges


def _finish(surf, size):
    return pygame.transform.smoothscale(surf, size)


def _lerp_color(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def make_plane(width, height):
    """Cartoon plane seen from behind."""
    s = SUPERSAMPLE
    w, h = width * s, height * s
    k = width / 120  # line widths were designed for a 120px-wide plane
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    outline = (70, 30, 30)
    red, cream, glass = (225, 70, 60), (255, 245, 225), (130, 205, 245)

    def line(n):
        return max(1, round(n * s * k))

    wings = pygame.Rect(0, h * 0.4, w, h * 0.22)
    pygame.draw.rect(surf, red, wings, border_radius=int(h * 0.1))
    pygame.draw.rect(surf, outline, wings, line(2), border_radius=int(h * 0.1))
    for x in (w * 0.01, w * 0.91):
        tip = pygame.Rect(x, h * 0.43, w * 0.08, h * 0.16)
        pygame.draw.rect(surf, cream, tip, border_radius=int(h * 0.06))

    body = pygame.Rect(w * 0.4, h * 0.28, w * 0.2, h * 0.64)
    pygame.draw.ellipse(surf, cream, body)
    pygame.draw.ellipse(surf, outline, body, line(2))
    pygame.draw.ellipse(surf, glass, pygame.Rect(w * 0.43, h * 0.3, w * 0.14, h * 0.22))
    pygame.draw.ellipse(surf, outline, pygame.Rect(w * 0.43, h * 0.3, w * 0.14, h * 0.22), line(2))

    stabilizer = pygame.Rect(w * 0.3, h * 0.74, w * 0.4, h * 0.13)
    pygame.draw.rect(surf, cream, stabilizer, border_radius=int(h * 0.06))
    pygame.draw.rect(surf, outline, stabilizer, line(2), border_radius=int(h * 0.06))

    fin = [(w * 0.45, h * 0.8), (w * 0.55, h * 0.8), (w * 0.535, h * 0.45), (w * 0.465, h * 0.45)]
    pygame.draw.polygon(surf, red, fin)
    pygame.draw.polygon(surf, outline, fin, line(2))

    return _finish(surf, (width, height))


def make_shadow(width, height):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (20, 70, 30, 110), surf.get_rect())
    return surf


def make_sky(width, horizon):
    """Gradient sky with hills and clouds, drawn down to the horizon line."""
    surf = pygame.Surface((width, horizon))
    top, bottom = (80, 165, 240), (205, 232, 250)
    for y in range(horizon):
        pygame.draw.line(surf, _lerp_color(top, bottom, y / horizon), (0, y), (width, y))

    rng = random.Random(3)
    unit = horizon * 0.1  # sizes scale with the sky height

    for _ in range(7):
        cx, cy = rng.randint(0, width), rng.randint(round(horizon * 0.08), round(horizon * 0.55))
        for _ in range(5):
            r = rng.randint(round(unit * 0.5), round(unit * 1.1))
            dx, dy = rng.randint(-round(unit * 1.5), round(unit * 1.5)), rng.randint(-round(unit * 0.3), round(unit * 0.3))
            pygame.draw.circle(surf, (255, 255, 255), (cx + dx, cy + dy), r)

    hills = [(0, horizon)]
    x = 0
    while x < width:
        hills.append((x, horizon - rng.randint(round(unit * 0.5), round(unit * 2))))
        x += rng.randint(round(unit * 2), round(unit * 4))
    hills += [(width, horizon), (width, horizon)]
    pygame.draw.polygon(surf, (150, 205, 185), hills)
    return surf
