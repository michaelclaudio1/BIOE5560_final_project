import random
import pygame

SUPERSAMPLE = 4  # draw large, then shrink for smooth edges


def _finish(surf, size):
    return pygame.transform.smoothscale(surf, size)


def make_car(width, height):
    """Top-down cartoon car, nose pointing up."""
    s = SUPERSAMPLE
    w, h = width * s, height * s
    k = width / 44  # line widths and radii were designed for a 44px-wide car
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    outline = (40, 40, 60)

    def line(n):
        return max(1, round(n * s * k))

    # Wheels poke out from under the body
    wheel_w, wheel_h = w * 0.16, h * 0.2
    for x in (0, w - wheel_w):
        for y in (h * 0.14, h * 0.66):
            wheel = pygame.Rect(x, y, wheel_w, wheel_h)
            pygame.draw.rect(surf, (35, 35, 40), wheel, border_radius=line(2))

    body = pygame.Rect(w * 0.09, 0, w * 0.82, h)
    pygame.draw.rect(surf, (250, 200, 40), body, border_radius=int(w * 0.28))
    pygame.draw.rect(surf, outline, body, line(3), border_radius=int(w * 0.28))

    pygame.draw.rect(surf, (230, 60, 50), pygame.Rect(w * 0.44, h * 0.02, w * 0.12, h * 0.96))

    windshield = pygame.Rect(w * 0.2, h * 0.28, w * 0.6, h * 0.17)
    pygame.draw.rect(surf, (140, 210, 250), windshield, border_radius=line(3))
    pygame.draw.rect(surf, outline, windshield, line(2), border_radius=line(3))
    rear = pygame.Rect(w * 0.22, h * 0.68, w * 0.56, h * 0.1)
    pygame.draw.rect(surf, (140, 210, 250), rear, border_radius=line(3))
    pygame.draw.rect(surf, outline, rear, line(2), border_radius=line(3))

    for x in (w * 0.24, w * 0.76):
        pygame.draw.circle(surf, (255, 255, 200), (x, h * 0.07), int(w * 0.07))

    return _finish(surf, (width, height))


def make_grass(width, height):
    """Vertically tileable grass with tufts and flowers."""
    surf = pygame.Surface((width, height))
    surf.fill((95, 190, 90))
    rng = random.Random(2)
    k = width / 600  # sizes were designed for a 600px-wide screen
    area = width * height / (600 * 800)
    tuft_w, tuft_h = round(5 * k), round(8 * k)

    for _ in range(round(90 * area)):
        x, y = rng.randint(0, width), rng.randint(0, height)
        for dy in (-height, 0, height):
            points = [(x - tuft_w, y + dy), (x, y + dy - tuft_h), (x + tuft_w, y + dy)]
            pygame.draw.lines(surf, (60, 150, 65), False, points, max(1, round(3 * k)))

    colors = [(255, 255, 255), (255, 130, 160), (255, 220, 80)]
    for _ in range(round(25 * area)):
        x, y = rng.randint(0, width), rng.randint(0, height)
        color = rng.choice(colors)
        for dy in (-height, 0, height):
            pygame.draw.circle(surf, color, (x, y + dy), max(1, round(5 * k)))
            pygame.draw.circle(surf, (240, 160, 40), (x, y + dy), max(1, round(2 * k)))
    return surf
