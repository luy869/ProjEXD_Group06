# rhythm_game_basic/main.py
import pygame
import sys
import os
import random
from note import Note

# --- 設定 ---
WIDTH, HEIGHT = 600, 700
FPS = 60
JUDGE_LINE_Y = HEIGHT - 150 
SPEED = 13  # ノーツの落下スピード

# 色定義
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# 矢印の位置
arrow_x = {
    'left': 100,
    'down': 200,
    'up': 300,
    'right': 400
}

# キー対応（左から順にs, f, j, l）
direction_keys = {
    'left': pygame.K_s,
    'down': pygame.K_f,
    'up': pygame.K_j,
    'right': pygame.K_l
}

# ノーツ方向のリスト
note_directions = ['left', 'down', 'up', 'right']

# 初期化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("リズムゲーム - ランダムノーツ")
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

# 状態
notes = []
score = 0
miss_count = 0
feedback = ""
feedback_timer = 0
start_time = pygame.time.get_ticks()
spawned_chart_times = set()
game_cleared = False
game_over = False

MISS_LIMIT = 5  # ゲームオーバーになるミス回数
NOTE_INTERVAL = 1000  # ノーツ間隔（ミリ秒）
TOTAL_NOTES = 20

# ランダムチャート生成（開始時1回）
chart = [(i * NOTE_INTERVAL + 1000, random.choice(note_directions)) for i in range(TOTAL_NOTES)]

running = True
while running:
    now = pygame.time.get_ticks() - start_time
    screen.fill(WHITE)

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 判定ライン描画 + キーガイド
    for d in arrow_x:
        pygame.draw.rect(screen, GRAY, (arrow_x[d] - 25, JUDGE_LINE_Y - 25, 50, 50), 2)

    key_labels = {
        'left': 'S',
        'down': 'F',
        'up': 'J',
        'right': 'L'
    }
    for dir, label in key_labels.items():
        text = small_font.render(label, True, BLACK)
        text_rect = text.get_rect(center=(arrow_x[dir], JUDGE_LINE_Y + 40))
        screen.blit(text, text_rect)

    # 操作説明表示
    instruction_text = small_font.render("操作: S / F / J / L キーでノーツを叩こう！", True, BLACK)
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 30))

    if not game_cleared and not game_over:
        frames_to_reach_judge_line = 120
        initial_y_offset = frames_to_reach_judge_line * SPEED
        initial_note_spawn_y = JUDGE_LINE_Y - initial_y_offset

        for time_ms, direction in chart:
            spawn_time_ms = time_ms - (frames_to_reach_judge_line * (1000 / FPS))
            is_already_spawned = any(n.appear_time == time_ms for n in notes)

            if now >= spawn_time_ms and time_ms not in spawned_chart_times:
                notes.append(Note(direction, time_ms, arrow_x[direction], initial_note_spawn_y))
                spawned_chart_times.add(time_ms)

        active_notes = []
        keys = pygame.key.get_pressed()

        for note in notes:
            if not note.hit:
                note.update(SPEED)
                note.draw(screen)

                if JUDGE_LINE_Y - 30 < note.y < JUDGE_LINE_Y + 30:
                    if keys[direction_keys[note.direction]]:
                        note.hit = True
                        score += 1
                        feedback = "Perfect!"
                        feedback_timer = 30

                elif note.y > JUDGE_LINE_Y + 30:
                    note.hit = True
                    miss_count += 1
                    feedback = "Miss..."
                    feedback_timer = 30

                    if miss_count >= MISS_LIMIT:
                        game_over = True
                        feedback = "GAME OVER"
                        feedback_timer = 180

                if not note.hit:
                    active_notes.append(note)

        notes = active_notes

        if len(spawned_chart_times) == len(chart) and not notes:
            game_cleared = True
            feedback = "CLEAR!!"
            feedback_timer = 180

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    miss_text = small_font.render(f"Miss: {miss_count}/{MISS_LIMIT}", True, RED)
    screen.blit(miss_text, (10, 60))

    if feedback_timer > 0:
        color = GREEN if feedback in ["Perfect!", "CLEAR!!"] else RED
        text = font.render(feedback, True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, 300))
        screen.blit(text, text_rect)
        feedback_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
