import pygame
import sys
import random
from japanese_font import get_font

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("こうかとんミニゲーム集 ホーム画面")
clock = pygame.time.Clock()

# 現在の画面状態（home または game1~game5）
current_screen = "home"

# ボタンリスト
games = ["ゲーム1", "ゲーム2", "ゲーム3", "ゲーム4", "ゲーム5"]

class HockeyGame:
    """ホッケーゲームのクラス
    このクラスは、ホッケーゲームのロジックと描画を管理します。"""
    def __init__(self, screen_surface:pygame.Surface):
        self.screen = screen_surface
        self.font_score = get_font(50)
        self.font_small = get_font(24)
        self.font_winner = get_font(80)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 50, 50)
        self.back_rect = pygame.Rect(10, 10, 150, 40)
        self.reset_game()

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
        self.setup_objects()

    def setup_objects(self):
        self.player_paddle = pygame.Rect(580, 200, 20, 100)
        self.ai_paddle = pygame.Rect(40, 200, 20, 100)
        self.puck = pygame.Rect(310, 230, 20, 20)
        self.puck_speed_x = 5 * random.choice((1, -1))
        self.puck_speed_y = 5 * random.choice((1, -1))

    def run(self):
        game_running = True
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_rect.collidepoint(event.pos):
                        game_running = False
                    if self.winner:
                        self.reset_game()
            if not self.winner:
                self.update_game_state()
            self.draw_elements()
            pygame.display.flip()
            clock.tick(60)

    def update_game_state(self):
        mouse_y = pygame.mouse.get_pos()[1]
        self.player_paddle.centery = mouse_y
        self.player_paddle.clamp_ip(self.screen.get_rect())
        # AIの速度をプレイヤーのスコアに応じて決定
        ai_speed = 4 + self.player_score  # 基本速度4にプレイヤーのスコアを足す

        # AIパドルの操作（パックを追いかける）
        if self.ai_paddle.centery < self.puck.centery:
            self.ai_paddle.y += ai_speed
        if self.ai_paddle.centery > self.puck.centery:
            self.ai_paddle.y -= ai_speed
        self.ai_paddle.clamp_ip(self.screen.get_rect())
        self.puck.x += self.puck_speed_x
        self.puck.y += self.puck_speed_y
        if self.puck.top <= 0 or self.puck.bottom >= 480: self.puck_speed_y *= -1
        if self.puck.colliderect(self.player_paddle) or self.puck.colliderect(self.ai_paddle):
            self.puck_speed_x *= -1.1
            self.puck.x += self.puck_speed_x
        if self.puck.left <= 0:
            self.player_score += 1
            if self.player_score >= 5: self.winner = "Player"
            self.setup_objects()
        if self.puck.right >= 640:
            self.ai_score += 1
            if self.ai_score >= 5: self.winner = "AI"
            self.setup_objects()

    def draw_elements(self):
        self.screen.fill(self.BLACK)
        pygame.draw.line(self.screen, self.WHITE, (320, 0), (320, 480), 2)
        pygame.draw.rect(self.screen, self.BLUE, self.player_paddle)
        pygame.draw.rect(self.screen, self.RED, self.ai_paddle)
        pygame.draw.ellipse(self.screen, self.WHITE, self.puck)
        player_text = self.font_score.render(str(self.player_score), True, self.WHITE)
        self.screen.blit(player_text, (400, 20))
        ai_text = self.font_score.render(str(self.ai_score), True, self.WHITE)
        self.screen.blit(ai_text, (200, 20))
        pygame.draw.rect(screen, (180, 50, 50), self.back_rect)
        back_text = self.font_small.render("ホームに戻る", True, (255, 255, 255))
        screen.blit(back_text, (self.back_rect.x + 10, self.back_rect.y + 10))
        if self.winner:
            win_text = self.font_winner.render(f"{self.winner} Wins!", True, self.WHITE)
            self.screen.blit(win_text, win_text.get_rect(center=(320, 240)))
            restart_text = self.font_small.render("クリックしてリスタート", True, self.WHITE)
            self.screen.blit(restart_text, restart_text.get_rect(center=(320, 320)))

def draw_home_screen():
    """
    ホーム画面を描写
    """
    screen.fill((30, 30, 30))
    font_title = get_font(64)
    font_button = get_font(40)

    # タイトル表示
    title = font_title.render("こうかとんミニゲーム集", True, (255, 255, 255))
    screen.blit(title, (100, 50))

    button_rects = []
    for i, game_name in enumerate(games):
        rect = pygame.Rect(220, 150 + i * 70, 200, 50)
        pygame.draw.rect(screen, (70, 130, 180), rect)
        text = font_button.render(game_name, True, (255, 255, 255))
        screen.blit(text, (rect.x + 20, rect.y + 10))
        button_rects.append(rect)

    return button_rects

def draw_game_screen(game_number):
    """
    それぞれのゲームへの遷移
    """
    screen.fill((0, 0, 0))
    font = get_font(50)
    text = font.render(f"ゲーム{game_number}画面（仮）", True, (255, 255, 255))
    screen.blit(text, (150, 200))

    # 「ホームに戻る」ボタン
    back_rect = pygame.Rect(20, 20, 120, 40)
    pygame.draw.rect(screen, (180, 50, 50), back_rect)
    back_text = font.render("ホームに戻る", True, (255, 255, 255))
    screen.blit(back_text, (back_rect.x + 5, back_rect.y + 5))

    return back_rect

def main():
    global current_screen

    running = True
    button_rects = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                #もしクリックされたときにホームなら、ボタンとの接触を判定する
                if current_screen == "home":
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(pos):
                            current_screen = f"game{i+1}"
                else:
                    # ゲーム画面で「ホームに戻る」ボタンを押したら戻る
                    back_rect = draw_game_screen(int(current_screen[-1]))
                    if back_rect.collidepoint(pos):
                        current_screen = "home"

        if current_screen == "home":
            button_rects = draw_home_screen()
        elif current_screen == "game5":
            game5 = HockeyGame(screen) # ゲームの準備
            game5.run()                # ゲーム開始
            current_screen = "home"    # ゲームが終わったらホームに戻る
        else:
            game_num = int(current_screen[-1])
            draw_game_screen(game_num)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
