import math

import pygame

from boat_game import (
    FPS,
    HEIGHT,
    ICEBERG_SCROLL_SPEED as SCROLL_SPEED,
    BOAT_SPEED as CAR_SPEED,
    GAME_OVER,
    LANE_WIDTH,
    MENU,
    PLAYING,
    REGIMEN,
    WAVE_INTERVAL,
    WIDTH,
    draw_text,
)
from car_sprites import make_car, make_grass

# Everything below scales with WIDTH and HEIGHT
CAR_WIDTH = round(LANE_WIDTH * 0.37)
CAR_HEIGHT = round(CAR_WIDTH * 76 / 44)
CAR_Y = round(HEIGHT * 0.97) - CAR_HEIGHT
CAR_HITBOX_SHRINK = 0.5  # forgiving hitbox relative to the sprite

ROAD_WIDTH = round(LANE_WIDTH * 1.25)  # a little wider than a lane so turns are forgiving
KERB_WIDTH = round(ROAD_WIDTH * 0.05)
DASH_LENGTH = round(ROAD_WIDTH * 0.27)
DASH_WIDTH = max(1, round(ROAD_WIDTH * 0.027))
SEGMENT_LENGTH = SCROLL_SPEED * WAVE_INTERVAL  # road distance covered per regimen step
HOLD_FRACTION = 0.1  # share of each segment where the road runs straight before turning
ROW_STEP = max(2, round(HEIGHT / 200))  # vertical resolution of the drawn road

ASPHALT = (70, 72, 80)
KERB = (240, 240, 240)
LANE_MARK = (250, 220, 90)


def smoothstep(t):
    return t * t * (3 - 2 * t)


def road_center(s):
    """Road centre x at distance s along the track (0 at the bottom of the screen at start)."""
    s = max(s, 0.0)
    index, rem = divmod(s, SEGMENT_LENGTH)
    index = int(index)
    u = rem / SEGMENT_LENGTH
    here = REGIMEN[index % len(REGIMEN)]
    nxt = REGIMEN[(index + 1) % len(REGIMEN)]
    t = 0.0 if u < HOLD_FRACTION else smoothstep((u - HOLD_FRACTION) / (1 - HOLD_FRACTION))
    return (here + (nxt - here) * t) * LANE_WIDTH + LANE_WIDTH / 2


def track_distance(y, dist):
    return dist + HEIGHT - y


def road_slope(y, dist):
    """Horizontal shift of the road centre per pixel of screen height."""
    ahead = road_center(track_distance(y - 1, dist))
    behind = road_center(track_distance(y + 1, dist))
    return (behind - ahead) / 2


def off_track(car_rect, dist):
    hit = car_rect.scale_by(CAR_HITBOX_SHRINK)
    for y in (hit.top, hit.centery, hit.bottom):
        cx = road_center(track_distance(y, dist))
        # Constant width measured perpendicular to the road is wider horizontally on a slope
        half = ROAD_WIDTH / 2 * math.hypot(1, road_slope(y, dist))
        if hit.left < cx - half or hit.right > cx + half:
            return True
    return False


def draw_road(screen, dist):
    # Overscan so the slanted edge offsets still reach past the screen edges
    ys = list(range(-ROAD_WIDTH, HEIGHT + ROAD_WIDTH, ROW_STEP))
    centers = [road_center(track_distance(y, dist)) for y in ys]
    slopes = [road_slope(y, dist) for y in ys]

    for half, color in ((ROAD_WIDTH / 2 + KERB_WIDTH, KERB), (ROAD_WIDTH / 2, ASPHALT)):
        left, right = [], []
        for cx, y, slope in zip(centers, ys, slopes):
            norm = math.hypot(1, slope)
            # Edge points sit half a road width away along the normal (1, -slope)
            dx, dy = half / norm, half * slope / norm
            left.append((cx - dx, y + dy))
            right.append((cx + dx, y - dy))
        pygame.draw.polygon(screen, color, left + right[::-1])

    for i in range(len(ys) - 1):
        if int(track_distance(ys[i], dist) // DASH_LENGTH) % 2 == 0:
            pygame.draw.line(screen, LANE_MARK, (centers[i], ys[i]), (centers[i + 1], ys[i + 1]), DASH_WIDTH)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Track Driver")
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, round(HEIGHT * 0.09))
    font = pygame.font.Font(None, round(HEIGHT * 0.045))

    car_image = make_car(CAR_WIDTH, CAR_HEIGHT)
    grass_image = make_grass(WIDTH, HEIGHT)

    state = MENU
    car = pygame.Rect(0, CAR_Y, CAR_WIDTH, CAR_HEIGHT)
    car_x = 0.0
    dist = 0.0

    def reset():
        nonlocal car_x, dist
        car_x = (WIDTH - CAR_WIDTH) / 2
        dist = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN and state != PLAYING:
                    reset()
                    state = PLAYING

        if state == PLAYING:
            keys = pygame.key.get_pressed()
            direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            car_x = min(max(car_x + direction * CAR_SPEED * dt, 0), WIDTH - CAR_WIDTH)
            car.x = round(car_x)
            dist += SCROLL_SPEED * dt

            if off_track(car, dist):
                state = GAME_OVER

        grass_y = int(dist) % HEIGHT
        screen.blit(grass_image, (0, grass_y))
        screen.blit(grass_image, (0, grass_y - HEIGHT))
        draw_road(screen, dist)
        if state != MENU:
            screen.blit(car_image, car)

        if state == MENU:
            draw_text(screen, title_font, "Track Driver", HEIGHT // 3)
            draw_text(screen, font, "Left / Right arrows to steer", HEIGHT // 2)
            draw_text(screen, font, "Press Enter to start, Esc to quit", HEIGHT // 2 + round(HEIGHT * 0.05))
        elif state == GAME_OVER:
            draw_text(screen, title_font, "Off the track!", HEIGHT // 3)
            draw_text(screen, font, "Press Enter to restart, Esc to quit", HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
