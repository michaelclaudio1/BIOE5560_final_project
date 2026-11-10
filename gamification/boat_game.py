import pygame
from sprites import make_boat, make_iceberg, make_water

WIDTH, HEIGHT = 2000, 1500
FPS = 60

# Everything below scales with WIDTH and HEIGHT
LANES = 5
LANE_WIDTH = WIDTH // LANES

BOAT_WIDTH = round(LANE_WIDTH * 0.42)
BOAT_HEIGHT = round(BOAT_WIDTH * 1.5)
BOAT_SPEED = WIDTH / 2  # pixels per second
BOAT_Y = round(HEIGHT * 0.97) - BOAT_HEIGHT

ICEBERG_SIZE = round(LANE_WIDTH * 0.75)
ICEBERG_SCROLL_SPEED = HEIGHT / 4  # pixels per second
WAVE_INTERVAL = 2.5  # seconds between rows of icebergs

ICEBERG_HITBOX_SHRINK = 0.8  # forgiving hitbox
SHOW_HITBOXES = False  # press H in-game to toggle
TEXT = (255, 255, 255)

MENU, PLAYING, GAME_OVER = "menu", "playing", "game_over"


def build_regimen():
    center, last = LANES // 2, LANES - 1
    warmup = [center, center - 1, center, center + 1] * 2  # small range of motion
    main = [0, center, last, center] * 3  # full range, returning to neutral
    cooldown = list(range(LANES)) + list(range(LANES - 2, 0, -1))  # slow sweep
    return warmup + main + cooldown


REGIMEN = build_regimen()


def draw_text(screen, font, text, y):
    surf = font.render(text, True, TEXT)
    screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Iceberg Dodger")
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, round(HEIGHT * 0.09))
    font = pygame.font.Font(None, round(HEIGHT * 0.045))

    boat_image = make_boat(BOAT_WIDTH, BOAT_HEIGHT)
    water_image = make_water(WIDTH, HEIGHT)
    water_offset = 0.0

    state = MENU
    boat = pygame.Rect(0, BOAT_Y, BOAT_WIDTH, BOAT_HEIGHT)
    print(boat.top)
    icebergs = []  # (rect, image) pairs
    spawn_timer = 0.0
    wave_index = 0

    def reset():
        nonlocal icebergs, spawn_timer, wave_index
        boat.centerx = WIDTH // 2
        icebergs = []
        spawn_timer = WAVE_INTERVAL
        wave_index = 0

    def iceberg_hitbox(berg):
        return berg.scale_by(ICEBERG_HITBOX_SHRINK)

    def boat_is_past(hitbox):
        return hitbox.top > boat.centery

    show_hitboxes = SHOW_HITBOXES

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_h:
                    show_hitboxes = not show_hitboxes
                elif event.key == pygame.K_RETURN and state != PLAYING:
                    reset()
                    state = PLAYING

        if state == PLAYING:
            keys = pygame.key.get_pressed()
            direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            boat.x += direction * BOAT_SPEED * dt
            boat.clamp_ip(screen.get_rect())

            spawn_timer += dt
            if spawn_timer >= WAVE_INTERVAL:
                spawn_timer = 0.0
                open_lane = REGIMEN[wave_index % len(REGIMEN)]
                wave_index += 1
                for lane in range(LANES):
                    if lane == open_lane:
                        continue
                    x = lane * LANE_WIDTH + (LANE_WIDTH - ICEBERG_SIZE) // 2
                    rect = pygame.Rect(x, -ICEBERG_SIZE, ICEBERG_SIZE, ICEBERG_SIZE)
                    icebergs.append((rect, make_iceberg(ICEBERG_SIZE)))

            for berg, _ in icebergs:
                berg.y += ICEBERG_SCROLL_SPEED * dt
            icebergs = [(r, img) for r, img in icebergs if r.top < HEIGHT]
            water_offset = (water_offset + ICEBERG_SCROLL_SPEED * dt) % HEIGHT

            for berg, _ in icebergs:
                hitbox = iceberg_hitbox(berg)
                if boat_is_past(hitbox):
                    continue
                if boat.colliderect(hitbox):
                    state = GAME_OVER
                    break

        y = int(water_offset)
        screen.blit(water_image, (0, y))
        screen.blit(water_image, (0, y - HEIGHT))
        for berg, image in icebergs:
            screen.blit(image, berg)
        if state != MENU:
            screen.blit(boat_image, boat)

        if show_hitboxes:
            for berg, _ in icebergs:
                hitbox = iceberg_hitbox(berg)
                color = (150, 150, 150) if boat_is_past(hitbox) else (255, 0, 0)
                pygame.draw.rect(screen, color, hitbox, 3)
            if state != MENU:
                pygame.draw.rect(screen, (0, 255, 0), boat, 3)

        if state == MENU:
            draw_text(screen, title_font, "Iceberg Dodger", HEIGHT // 3)
            draw_text(screen, font, "Left / Right arrows to steer", HEIGHT // 2)
            draw_text(screen, font, "Press Enter to start, Esc to quit", HEIGHT // 2 + round(HEIGHT * 0.05))
        elif state == GAME_OVER:
            draw_text(screen, title_font, "Game Over", HEIGHT // 3)
            draw_text(screen, font, "Press Enter to restart, Esc to quit", HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
