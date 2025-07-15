import pygame
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from japanese_font import get_font
from .note import Note

class RhythmGame:
    def __init__(self):
        # 基本設定
        self.WIDTH = 600
        self.HEIGHT = 700
        self.FPS = 60
        self.JUDGE_LINE_Y = self.HEIGHT - 150 
        self.SPEED = 13

        # 色定義
        self.WHITE = (255, 255, 255)
        self.GRAY = (180, 180, 180)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)

        # 矢印の位置
        self.arrow_x = {
            'left': 100,
            'down': 200,
            'up': 300,
            'right': 400
        }

        # キー対応（S,F,J,Lキー）
        self.direction_keys = {
            'left': pygame.K_s,
            'down': pygame.K_f,
            'up': pygame.K_j,
            'right': pygame.K_l
        }

        self.note_directions = ['left', 'down', 'up', 'right']
        self.font = get_font(32)
        self.small_font = get_font(20)

        # ゲーム状態初期化
        self.reset_game()

    def reset_game(self):
        self.notes = []
        self.score = 0
        self.miss_count = 0
        self.feedback = ""
        self.feedback_timer = 0
        self.start_time = pygame.time.get_ticks()
        self.spawned_chart_times = set()
        self.game_cleared = False
        self.game_over = False
        self.MISS_LIMIT = 5
        self.NOTE_INTERVAL = 1000
        self.TOTAL_NOTES = 20
        # ランダムチャート生成
        self.chart = [(i * self.NOTE_INTERVAL + 1000, random.choice(self.note_directions)) for i in range(self.TOTAL_NOTES)]

    def run(self):
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("リズムゲーム")
        clock = pygame.time.Clock()
        
        running = True
        while running:
            now = pygame.time.get_ticks() - self.start_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "home"
                    elif event.key == pygame.K_r and (self.game_cleared or self.game_over):
                        self.reset_game()

            screen.fill(self.WHITE)

            # 判定ライン描画
            for d in self.arrow_x:
                pygame.draw.rect(screen, self.GRAY, (self.arrow_x[d] - 25, self.JUDGE_LINE_Y - 25, 50, 50), 2)

            # キーガイド（S,F,J,Lキー表示）
            key_labels = {'left': 'S', 'down': 'F', 'up': 'J', 'right': 'L'}
            for dir, label in key_labels.items():
                text = self.small_font.render(label, True, self.BLACK)
                text_rect = text.get_rect(center=(self.arrow_x[dir], self.JUDGE_LINE_Y + 40))
                screen.blit(text, text_rect)

            # 操作説明
            instruction_text = self.small_font.render("S / F / J / L キーでノーツを叩こう！", True, self.BLACK)
            screen.blit(instruction_text, (self.WIDTH // 2 - instruction_text.get_width() // 2, self.HEIGHT - 30))

            if not self.game_cleared and not self.game_over:
                self.update_game(now, screen)

            self.draw_ui(screen)

            # 戻るボタン
            back_rect = pygame.Rect(10, 10, 100, 30)
            pygame.draw.rect(screen, self.RED, back_rect)
            back_text = self.small_font.render("ESC: 戻る", True, self.WHITE)
            screen.blit(back_text, (back_rect.x + 5, back_rect.y + 5))

            pygame.display.flip()
            clock.tick(self.FPS)

        return "quit"

    def update_game(self, now, screen):
        frames_to_reach_judge_line = 120
        initial_y_offset = frames_to_reach_judge_line * self.SPEED
        initial_note_spawn_y = self.JUDGE_LINE_Y - initial_y_offset

        # ノーツ生成
        for time_ms, direction in self.chart:
            spawn_time_ms = time_ms - (frames_to_reach_judge_line * (1000 / self.FPS))
            
            if now >= spawn_time_ms and time_ms not in self.spawned_chart_times:
                self.notes.append(Note(direction, time_ms, self.arrow_x[direction], initial_note_spawn_y))
                self.spawned_chart_times.add(time_ms)

        # ノーツ更新と判定
        active_notes = []
        keys = pygame.key.get_pressed()

        for note in self.notes:
            if not note.hit:
                note.update(self.SPEED)
                note.draw(screen)

                # 判定処理
                if self.JUDGE_LINE_Y - 30 < note.y < self.JUDGE_LINE_Y + 30:
                    if keys[self.direction_keys[note.direction]]:
                        note.hit = True
                        self.score += 1
                        self.feedback = "Perfect!"
                        self.feedback_timer = 30

                elif note.y > self.JUDGE_LINE_Y + 30:
                    note.hit = True
                    self.miss_count += 1
                    self.feedback = "Miss..."
                    self.feedback_timer = 30

                    if self.miss_count >= self.MISS_LIMIT:
                        self.game_over = True
                        self.feedback = "GAME OVER"
                        self.feedback_timer = 180

                if not note.hit:
                    active_notes.append(note)

        self.notes = active_notes

        # クリア判定
        if len(self.spawned_chart_times) == len(self.chart) and not self.notes:
            self.game_cleared = True
            self.feedback = "CLEAR!!"
            self.feedback_timer = 180

    def draw_ui(self, screen):
        # スコア表示
        score_text = self.font.render(f"Score: {self.score}", True, self.BLACK)
        screen.blit(score_text, (10, 50))

        # ミス表示
        miss_text = self.small_font.render(f"Miss: {self.miss_count}/{self.MISS_LIMIT}", True, self.RED)
        screen.blit(miss_text, (10, 90))

        # フィードバック表示
        if self.feedback_timer > 0:
            color = self.GREEN if self.feedback in ["Perfect!", "CLEAR!!"] else self.RED
            text = self.font.render(self.feedback, True, color)
            text_rect = text.get_rect(center=(self.WIDTH // 2, 300))
            screen.blit(text, text_rect)
            self.feedback_timer -= 1

        # ゲーム終了時のメッセージ
        if self.game_cleared or self.game_over:
            restart_text = self.small_font.render("R: リスタート", True, self.BLACK)
            screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, 350))
