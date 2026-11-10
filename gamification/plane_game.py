import pygame

from boat_game import (
    BOAT_SPEED as PLANE_SPEED,
    FPS,
    GAME_OVER,
    HEIGHT,
    LANE_WIDTH,
    LANES,
    MENU,
    PLAYING,
    REGIMEN,
    WAVE_INTERVAL,
    WIDTH,
)
from plane_sprites import make_plane, make_shadow, make_sky

PLANE_WIDTH = round(LANE_WIDTH * 0.6)
PLANE_HEIGHT = round(PLANE_WIDTH * 0.55)
PLANE_HITBOX_SHRINK = 0.6  # forgiving hitbox relative to the wingspan
MAX_BANK = 20  # degrees of roll when steering

CYCLES = 2  # full passes through the regimen before the game ends
TOTAL_HOOPS = CYCLES * len(REGIMEN)
FINISHED = "finished"

HOOP_RADIUS = round(LANE_WIDTH * 0.6)
HOOP_THICKNESS = round(HOOP_RADIUS * 0.14)

# Camera sits behind the plane; distances are measured forward from the plane
FOCAL = HEIGHT
FLY_SPEED = HEIGHT * 0.9  # pixels (at plane depth) per second
SPAWN_DISTANCE = 6 * FOCAL
HOOP_SPACING = FLY_SPEED * WAVE_INTERVAL
HOOP_REMOVE_DISTANCE = -0.45 * FOCAL  # hoops fly past the camera before vanishing

VANISH_X = WIDTH / 2
HORIZON_Y = round(HEIGHT * 0.35)
PLANE_Y = round(HEIGHT * 0.72)
GROUND_Y = PLANE_Y + round(HOOP_RADIUS * 1.15)  # ground level under the plane
BAND_LENGTH = FOCAL * 0.4

GROUND_DARK = (80, 170, 80)
GROUND_LIGHT = (100, 190, 95)
LANE_LINE = (120, 200, 115)
HOOP_COLOR = (255, 150, 30)
HOOP_EDGE = (150, 60, 20)
POLE = (150, 150, 160)
FOG = (205, 232, 250)
TEXT = (255, 255, 255)
TEXT_SHADOW = (30, 50, 90)


def scale_at(d):
    return FOCAL / (FOCAL + d)


def ground_y(d):
    if FOCAL + d <= 0:
        return HEIGHT * 3
    return HORIZON_Y + (GROUND_Y - HORIZON_Y) * scale_at(d)


def lane_center(lane):
    return lane * LANE_WIDTH + LANE_WIDTH / 2


def hoop_cleared(plane_x, lane):
    half = PLANE_WIDTH / 2 * PLANE_HITBOX_SHRINK
    return abs(plane_x - lane_center(lane)) + half <= HOOP_RADIUS


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw_text(screen, font, text, y, x=WIDTH // 2, align="center"):
    shadow_offset = max(2, round(HEIGHT * 0.003))
    for color, offset in ((TEXT_SHADOW, shadow_offset), (TEXT, 0)):
        surf = font.render(text, True, color)
        rect = surf.get_rect(**{align: (x + offset, y + offset)})
        screen.blit(surf, rect)


def draw_ground(screen, dist):
    screen.fill(GROUND_DARK, (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y))

    # Light bands, spaced evenly in world distance, bunch up toward the horizon
    offset = dist % (2 * BAND_LENGTH)
    k = -2
    while True:
        near = 2 * k * BAND_LENGTH - offset
        if near > 30 * FOCAL:
            break
        far = near + BAND_LENGTH
        y_far = max(ground_y(far), HORIZON_Y)
        y_near = min(ground_y(near), HEIGHT)
        if y_near > y_far:
            screen.fill(GROUND_LIGHT, (0, y_far, WIDTH, y_near - y_far))
        k += 1

    # Lane boundaries converge on the vanishing point
    reach = (HEIGHT - HORIZON_Y) / (GROUND_Y - HORIZON_Y)
    width = max(1, round(WIDTH * 0.002))
    for i in range(LANES + 1):
        x_end = VANISH_X + (i * LANE_WIDTH - VANISH_X) * reach
        pygame.draw.line(screen, LANE_LINE, (VANISH_X, HORIZON_Y), (x_end, HEIGHT), width)


def draw_hoop(screen, d, lane):
    scale = scale_at(d)
    cx = VANISH_X + (lane_center(lane) - VANISH_X) * scale
    cy = HORIZON_Y + (PLANE_Y - HORIZON_Y) * scale
    radius = round(HOOP_RADIUS * scale)
    thick = max(2, round(HOOP_THICKNESS * scale))
    fog = min(1.0, max(d, 0) / SPAWN_DISTANCE) * 0.7

    pole_w = max(2, thick // 2)
    pole_top = cy + radius
    pole_bottom = ground_y(d)
    if pole_bottom > pole_top:
        pygame.draw.rect(screen, mix(POLE, FOG, fog), (cx - pole_w / 2, pole_top, pole_w, pole_bottom - pole_top))

    edge = max(1, thick // 4)
    pygame.draw.circle(screen, mix(HOOP_COLOR, FOG, fog), (cx, cy), radius, thick)
    pygame.draw.circle(screen, mix(HOOP_EDGE, FOG, fog), (cx, cy), radius, edge)
    pygame.draw.circle(screen, mix(HOOP_EDGE, FOG, fog), (cx, cy), radius - thick + edge, edge)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hoop Flyer")
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, round(HEIGHT * 0.09))
    font = pygame.font.Font(None, round(HEIGHT * 0.045))

    plane_image = make_plane(PLANE_WIDTH, PLANE_HEIGHT)
    shadow_image = make_shadow(round(PLANE_WIDTH * 0.8), round(PLANE_HEIGHT * 0.3))
    sky_image = make_sky(WIDTH, HORIZON_Y)

    state = MENU
    plane_x = WIDTH / 2
    bank = 0.0
    dist = 0.0
    hoops = []  # [distance ahead of the plane, lane]
    spawn_timer = 0.0
    wave_index = 0
    hoops_cleared = 0

    def reset():
        nonlocal plane_x, bank, dist, hoops, spawn_timer, wave_index, hoops_cleared
        plane_x = WIDTH / 2
        bank = 0.0
        dist = 0.0
        hoops = []
        wave_index = 0
        hoops_cleared = 0
        d = FLY_SPEED * 2.0  # first hoop is two seconds away
        while d <= SPAWN_DISTANCE and wave_index < TOTAL_HOOPS:
            hoops.append([d, REGIMEN[wave_index % len(REGIMEN)]])
            wave_index += 1
            d += HOOP_SPACING
        # Next hoop appears once it has flown in from beyond the spawn distance
        spawn_timer = WAVE_INTERVAL - (d - SPAWN_DISTANCE) / FLY_SPEED

    reset()

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
            plane_x += direction * PLANE_SPEED * dt
            plane_x = min(max(plane_x, PLANE_WIDTH / 2), WIDTH - PLANE_WIDTH / 2)
            bank += (-direction * MAX_BANK - bank) * min(1.0, dt * 8)
            dist += FLY_SPEED * dt

            spawn_timer += dt
            if spawn_timer >= WAVE_INTERVAL:
                spawn_timer = 0.0
                if wave_index < TOTAL_HOOPS:
                    hoops.append([SPAWN_DISTANCE, REGIMEN[wave_index % len(REGIMEN)]])
                    wave_index += 1

            for hoop in hoops:
                previous = hoop[0]
                hoop[0] -= FLY_SPEED * dt
                if previous > 0 >= hoop[0]:
                    if not hoop_cleared(plane_x, hoop[1]):
                        state = GAME_OVER
                    else:
                        hoops_cleared += 1
                        if hoops_cleared >= TOTAL_HOOPS:
                            state = FINISHED
            hoops = [h for h in hoops if h[0] > HOOP_REMOVE_DISTANCE]

        screen.blit(sky_image, (0, 0))
        draw_ground(screen, dist)

        ordered = sorted(hoops, key=lambda h: -h[0])
        for d, lane in (h for h in ordered if h[0] > 0):
            draw_hoop(screen, d, lane)

        screen.blit(shadow_image, shadow_image.get_rect(center=(plane_x, GROUND_Y)))
        tilted = pygame.transform.rotozoom(plane_image, bank, 1)
        screen.blit(tilted, tilted.get_rect(center=(plane_x, PLANE_Y)))

        for d, lane in (h for h in ordered if h[0] <= 0):
            draw_hoop(screen, d, lane)

        margin = round(HEIGHT * 0.02)
        if state != MENU:
            draw_text(screen, font, f"Hoops: {hoops_cleared} / {TOTAL_HOOPS}", margin, x=margin, align="topleft")

        score = f"Score: {hoops_cleared} / {TOTAL_HOOPS}"
        if state == MENU:
            draw_text(screen, title_font, "Hoop Flyer", HEIGHT // 4)
            draw_text(screen, font, "Left / Right arrows to steer", HEIGHT // 4 + round(HEIGHT * 0.08))
            draw_text(screen, font, "Press Enter to start, Esc to quit", HEIGHT // 4 + round(HEIGHT * 0.13))
        elif state == GAME_OVER:
            draw_text(screen, title_font, "Missed a hoop!", HEIGHT // 4)
            draw_text(screen, font, score, HEIGHT // 4 + round(HEIGHT * 0.08))
            draw_text(screen, font, "Press Enter to restart, Esc to quit", HEIGHT // 4 + round(HEIGHT * 0.13))
        elif state == FINISHED:
            draw_text(screen, title_font, "Course complete!", HEIGHT // 4)
            draw_text(screen, font, score, HEIGHT // 4 + round(HEIGHT * 0.08))
            draw_text(screen, font, "Press Enter to restart, Esc to quit", HEIGHT // 4 + round(HEIGHT * 0.13))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
