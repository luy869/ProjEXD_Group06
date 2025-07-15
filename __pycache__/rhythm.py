# rhythm_game_basic/main.py
import pygame
import sys
import os
from note import Note
from chart import chart

# --- 設定 ---
WIDTH, HEIGHT = 600, 700
FPS = 60
JUDGE_LINE_Y = 150
SPEED = 4  # ノーツの落下スピード

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

# キー対応
direction_keys = {
    'left': pygame.K_LEFT,
    'down': pygame.K_DOWN,
    'up': pygame.K_UP,
    'right': pygame.K_RIGHT
}

# 初期化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("リズムゲーム - ノーツ基準")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

# 状態
notes = []
score = 0
feedback = ""
feedback_timer = 0
start_time = pygame.time.get_ticks()

running = True
while running:
    now = pygame.time.get_ticks() - start_time
    screen.fill(WHITE)

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 判定ライン描画
    for d in arrow_x:
        pygame.draw.rect(screen, GRAY, (arrow_x[d] - 25, JUDGE_LINE_Y - 25, 50, 50), 2)

    # ノーツ出現
    for time_ms, direction in chart:
        if now >= time_ms and all(n.appear_time != time_ms for n in notes):
            notes.append(Note(direction, time_ms, arrow_x[direction], HEIGHT))

    # ノーツ更新・描画
    for note in notes:
        if not note.hit:
            note.update(SPEED)
            note.draw(screen)

    # 入力判定
    keys = pygame.key.get_pressed()
    for note in notes:
        if not note.hit and abs(note.y - JUDGE_LINE_Y) < 30:
            if keys[direction_keys[note.direction]]:
                note.hit = True
                score += 1
                feedback = "Perfect!"
                feedback_timer = 30

    # Miss判定
    for note in notes:
        if not note.hit and note.y < JUDGE_LINE_Y - 30:
            note.hit = True
            feedback = "Miss..."
            feedback_timer = 30

    # スコアとフィードバック表示
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    if feedback_timer > 0:
        color = GREEN if feedback == "Perfect!" else RED
        text = font.render(feedback, True, color)
        screen.blit(text, (WIDTH // 2 - 60, 300))
        feedback_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

# note.py
import pygame

class Note:
    def __init__(self, direction, appear_time, x, y):
        self.direction = direction
        self.appear_time = appear_time  # 出現予定時刻
        self.x = x
        self.y = y
        self.hit = False

    def update(self, speed):
        self.y -= speed

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (self.x, int(self.y)), 20)

# chart.py
chart = [
    (1000, 'left'),
    (2000, 'down'),
    (3000, 'up'),
    (4000, 'right'),
    (5000, 'left'),
    (6000, 'down'),
    (7000, 'up'),
    (8000, 'right'),
    (9000, 'left'),
    (10000, 'right')
]
