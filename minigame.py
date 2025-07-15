import pygame
import random
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import random
from japanese_font import get_font
from game6.game6 import ShootingGame  # game6のimportを有効化
from game3.game3 import RhythmGame  # game3のimportを追加

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("こうかとんミニゲーム集 ホーム画面")
clock = pygame.time.Clock()

# 現在の画面状態（home または game1~game6）
current_screen = "home"

# ボタンリスト
games = ["ゲーム1", "ゲーム2", "ゲーム3", "ゲーム4", "ゲーム5", "ゲーム6"]

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

def clicker_main():
    """
    こうかとんクリッカーを動かすメイン関数。
    whileループの中でクリックとショップの判定、スコアとコインの更新。
    whileを抜けた際に画面を更新。
    クリア画面とショップ画面を作成。
    クリアしたかの判定。
    """
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("こうかとんクリッカー＋ショップ")
    clock = pygame.time.Clock()

    font = get_font(30)

    coin: int = 0 #コインの数
    click_power: int = 1 #1回ごとのスコア/コイン増加量
    auto_power: int = 0 #オートクリックの回数/秒
    count: int = 0  # スコア（クリック回数）

    CLEAR_SCORE: int = 1000  # クリア判定スコア

    #こうかとんの表示
    base_dir = os.path.dirname(__file__)
    image_path = os.path.join(base_dir, "fig", "3.png")
    try:
        koukaton_img = pygame.image.load(image_path)
        koukaton_img = pygame.transform.scale(koukaton_img, (150, 150))
    except:
        koukaton_img = pygame.Surface((150, 150))
        koukaton_img.fill((200, 50, 50))
    koukaton_rect = koukaton_img.get_rect(center=(320, 240))

    #クリック判定
    clicked = False
    click_timer = 0

    show_shop = False
    game_clear = False

    AUTO_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(AUTO_EVENT, 1000)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not show_shop and not game_clear and koukaton_rect.collidepoint(event.pos):
                    count += click_power      # スコア増加
                    coin += click_power
                    clicked = True
                    click_timer = 5

                elif show_shop:
                    x, y = event.pos
                    # ボタンを強化
                    if 50 <= x <= 250 and 100 <= y <= 140:
                        price = 10
                        if coin >= price:
                            coin -= price
                            click_power += 1
                    # オートクリッカーを強化
                    elif 50 <= x <= 250 and 160 <= y <= 200:
                        price = 30
                        if coin >= price:
                            coin -= price
                            auto_power += 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and not game_clear:
                    show_shop = not show_shop

            elif event.type == AUTO_EVENT and not game_clear:
                if auto_power > 0:
                    coin += auto_power

        screen.fill((30, 30, 30))

        if game_clear:
            # クリア画面
            clear_text = font.render(f"クリア！スコア: {count}", True, (255, 255, 0))
            sub_text = font.render("ゲームを終了するにはウィンドウを閉じてください", True, (255, 255, 255))
            screen.blit(clear_text, (100, 200))
            screen.blit(sub_text, (50, 260))

        elif show_shop:
            # ショップ画面描画
            title = font.render("ショップ (Sキーで戻る)", True, (255, 255, 255))
            screen.blit(title, (50, 30))

            pygame.draw.rect(screen, (50, 100, 200), (50, 100, 200, 40))
            text1 = font.render(f"クリック強化 +1 (10コイン) [{click_power}]", True, (255, 255, 255))
            screen.blit(text1, (60, 110))

            pygame.draw.rect(screen, (50, 200, 100), (50, 160, 200, 40))
            text2 = font.render(f"オートクリッカー +1 (30コイン) [{auto_power}]", True, (255, 255, 255))
            screen.blit(text2, (60, 170))

            coin_text = font.render(f"コイン: {coin}", True, (255, 255, 0))
            screen.blit(coin_text, (50, 230))

            score_text = font.render(f"スコア: {count}", True, (255, 255, 255))
            screen.blit(score_text, (50, 270))

        else:
            # ゲーム画面描画
            score_text = font.render(f"スコア: {count}", True, (255, 255, 255))
            score_rect = score_text.get_rect(topright=(620, 20))
            screen.blit(score_text, score_rect)

            coin_text = font.render(f"コイン: {coin}", True, (255, 255, 0))
            coin_rect = coin_text.get_rect(topright=(620, 60))
            screen.blit(coin_text, coin_rect)

            if clicked:
                scaled_img = pygame.transform.scale(koukaton_img, (180, 180))
                scaled_rect = scaled_img.get_rect(center=koukaton_rect.center)
                screen.blit(scaled_img, scaled_rect)
                click_timer -= 1
                if click_timer <= 0:
                    clicked = False
            else:
                screen.blit(koukaton_img, koukaton_rect)

            shop_hint = font.render("Sキーでショップ", True, (200, 200, 200))
            screen.blit(shop_hint, (20, 450))

            # クリア判定
            if count >= CLEAR_SCORE:
                game_clear = True

        pygame.display.flip()
        clock.tick(60)

def draw_home_screen():
    screen.fill((30, 30, 30))
    font_title = get_font(64)
    font_button = get_font(40)

    # タイトル表示
    title = font_title.render("こうかとんミニゲーム集", True, (255, 255, 255))
    screen.blit(title, (100, 50))

    button_rects = []
    for i, game_name in enumerate(games):
        rect = pygame.Rect(300, 150 + i * 60, 200, 50)
        pygame.draw.rect(screen, (70, 130, 180), rect)
        text = font_button.render(game_name, True, (255, 255, 255))
        screen.blit(text, (rect.x + 20, rect.y + 10))
        button_rects.append(rect)

    return button_rects

def draw_game_screen(game_number):
    screen.fill((0, 0, 0))
    font = get_font(50)
    
    if game_number == 6:
        # ゲーム6のタイトル画面
        title_text = font.render("弾幕シューティングゲーム", True, (255, 255, 255))
        screen.blit(title_text, (100, 180))
        
        # スタートボタン
        start_rect = pygame.Rect(220, 250, 200, 60)
        pygame.draw.rect(screen, (50, 180, 50), start_rect)
        start_text = get_font(32).render("スタート", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=start_rect.center)
        screen.blit(start_text, text_rect)
        
        # 戻るボタン
        back_rect = pygame.Rect(220, 330, 200, 60)
        pygame.draw.rect(screen, (180, 50, 50), back_rect)
        back_text = get_font(32).render("ホームに戻る", True, (255, 255, 255))
        text_rect2 = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, text_rect2)
        
        return start_rect, back_rect
    else:
        # 他のゲーム画面
        text = font.render(f"ゲーム{game_number}画面（仮）", True, (255, 255, 255))
        screen.blit(text, (150, 200))

        # 「ホームに戻る」ボタン
        back_rect = pygame.Rect(20, 20, 120, 40)
        pygame.draw.rect(screen, (180, 50, 50), back_rect)
        back_text = font.render("ホームに戻る", True, (255, 255, 255))
        screen.blit(back_text, (back_rect.x + 5, back_rect.y + 5))

        return back_rect

class Card(pygame.sprite.Sprite):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        # 画像ファイルの絶対パスを作成
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, "fig", f"{self.suit}_{self.rank}.png")
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 120))
        self.rect = self.image.get_rect()
    
    def get_value(self):
        if self.rank in ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11
        else:
            return int(self.rank)


class BlackjackGame:
    def __init__(self):
        self.font_m = pygame.font.Font(None, 40)
        self.font_l = pygame.font.Font(None, 60)
        
        self.hit_button = pygame.Rect(450, 100, 150, 50)
        self.stand_button = pygame.Rect(450, 400, 150, 50)
        
        self.continue_button = pygame.Rect(150, 400, 180, 50)
        self.home_button = pygame.Rect(400, 400, 180, 50)

        self.deal_delay = 750
        self.last_deal_time = 0
        self.start_new_game()

    def create_deck(self):
        suits = ["heart", "daiya", "clover", "spade"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.deck)

    def deal_initial_cards(self):
        for _ in range(2):
            self.player_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())

    def calculate_score(self, hand):
        value = sum(card.get_value() for card in hand)
        aces = sum(1 for card in hand if card.rank == "A")
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value
    
    def start_new_game(self):
        self.create_deck()
        self.player_hand = []
        self.dealer_hand = []   
        self.game_state = "dealing"
        self.message = "hand out cards..."
        self.last_deal_time = pygame.time.get_ticks()
        texe_msg = self.font_m.render("Your Turn", True, (255, 255, 255))
        screen.blit(texe_msg, (250, 400))
    
    def handle_event(self, event):
        if self.game_state == "player_turn" and event.type == pygame.MOUSEBUTTONDOWN:
            if self.hit_button.collidepoint(event.pos):
                self.player_hand.append(self.deck.pop())
                if self.calculate_score(self.player_hand) > 21:
                    self.message = "BUST! YOU LOSE..."
                    self.game_state = "game_over"
            elif self.stand_button.collidepoint(event.pos):
                self.game_state = "dealer_turn"
                self.last_deal_time = pygame.time.get_ticks()
                self.message = "Dealer's Turn"
        elif self.game_state == "game_over" and event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.collidepoint(event.pos):
                return "continue"
            elif self.home_button.collidepoint(event.pos):
                return "home"
        return None
        
    def update(self):
        current_time = pygame.time.get_ticks()
        if self.game_state == "dealing":
            if current_time - self.last_deal_time > self.deal_delay:
                if len(self.player_hand) == 0:
                    self.player_hand.append(self.deck.pop())
                elif len(self.dealer_hand) == 0:
                    self.dealer_hand.append(self.deck.pop())
                elif len(self.player_hand) == 1:
                    self.player_hand.append(self.deck.pop())
                elif len(self.dealer_hand) == 1:
                    self.dealer_hand.append(self.deck.pop())
                    player_score = self.calculate_score(self.player_hand)
                    if player_score == 21:
                        self.message = "BLACKJACK! YOU WIN!"
                        self.game_state = "game_over"
                    else:
                        self.message = "Your Turn"
                        self.game_state = "player_turn"
                self.last_deal_time = current_time
        elif self.game_state == "dealer_turn":
            self.message = "Dealer's Turn"
            if current_time - self.last_deal_time > self.deal_delay:
                if self.calculate_score(self.dealer_hand) < 17:
                    self.dealer_hand.append(self.deck.pop())
                    self.last_deal_time = current_time
                else:
                    player_score = self.calculate_score(self.player_hand)
                    dealer_score = self.calculate_score(self.dealer_hand)
                    if dealer_score > 21 or player_score > dealer_score:
                        self.message = "YOU WIN!"
                    elif player_score < dealer_score:
                        self.message = "YOU LOSE..."
                    else:
                        self.message = "DRAW"
                    self.game_state = "game_over"
    
    def draw(self):
        screen.fill((0, 128, 0))
        
        # ディーラーの手札を描画
        if self.game_state == "player_turn":
        # プレイヤーのターンの時は、1枚目のカードの点数だけを表示
            score = self.dealer_hand[0].get_value()
            dealer_score_str = f"Dealer's Score: {score}"
        else:
        # それ以外の時は、全カードの合計点を表示
            score = self.calculate_score(self.dealer_hand)
            dealer_score_str = f"Dealer's Score: {score}"
        for i, card in enumerate(self.dealer_hand):
            card.rect.topleft = (100 + i * 110, 50)
            if self.game_state == "player_turn" and i == 1:
                # ディーラーの2枚目のカードは非表示
                pygame.draw.rect(screen, (80, 80, 80), card.rect)
            else:
                screen.blit(card.image, card.rect)
        
        dealer_text_surface = self.font_m.render(dealer_score_str, True, (255, 255, 255))
        screen.blit(dealer_text_surface, (100, 180))

        player_score = self.calculate_score(self.player_hand)
        player_score_str = f"Your Score: {player_score}"
        for i, card in enumerate(self.player_hand):
            card.rect.topleft = (100 + i * 110, 300)
            screen.blit(card.image, card.rect)
        
        player_text_surface = self.font_m.render(player_score_str, True, (255, 255, 255))
        screen.blit(player_text_surface, (100, 430))
        msg_surface = self.font_l.render(self.message, True, (255, 255, 0))
        msg_rect = msg_surface.get_rect(center=(screen.get_width() // 2, 240))
        screen.blit(msg_surface, msg_rect)
        # ボタンを描画
        if self.game_state == "player_turn":
            pygame.draw.rect(screen, (0, 0, 255), self.hit_button)
            pygame.draw.rect(screen, (255, 0, 0), self.stand_button)
            hit_text = self.font_m.render("Hit", True, (255, 255, 255))
            stand_text = self.font_m.render("Stand", True, (255, 255, 255))
            screen.blit(hit_text, (self.hit_button.x + 35, self.hit_button.y + 10))
            screen.blit(stand_text, (self.stand_button.x + 25, self.stand_button.y + 10))
        if self.game_state == "game_over":
            continues = pygame.Surface((screen.get_width(), screen.get_height()))
            continues.set_alpha(200)  # 半透明にする
            screen.blit(continues, (0, 0))
            pygame.draw.rect(screen, (0, 255, 0), self.continue_button)
            pygame.draw.rect(screen, (255, 0, 0), self.home_button)
            continue_text = self.font_m.render("Continue", True, (255, 255, 255))
            home_text = self.font_m.render("Home", True, (255, 255, 255))
            screen.blit(continue_text, (self.continue_button.x + 20, self.continue_button.y + 10))
            screen.blit(home_text, (self.home_button.x + 50, self.home_button.y + 10))

class BlockBreakerGame:
    """ブロック崩しゲームのクラス"""
    def __init__(self, screen_surface: pygame.Surface):
        self.screen = screen_surface
        self.font_large = get_font(48)
        self.font_medium = get_font(32)
        self.font_small = get_font(24)
        
        # 色定義
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 100, 100)
        self.BLUE = (100, 100, 255)
        self.GREEN = (100, 255, 100)
        self.YELLOW = (255, 255, 100)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        
        # ゲーム設定
        self.PADDLE_WIDTH = 100
        self.PADDLE_HEIGHT = 15
        self.BALL_SIZE = 15
        self.BLOCK_WIDTH = 70
        self.BLOCK_HEIGHT = 25
        self.ROWS = 5
        self.COLS = 10
        
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_clear = False
        self.back_rect = pygame.Rect(10, 10, 150, 40)
        
        self.reset_game()
    
    def reset_game(self):
        """ゲームリセット"""
        # パドル初期化
        self.paddle_x = 400 - self.PADDLE_WIDTH // 2
        self.paddle_y = 550
        
        # ボール初期化
        self.ball_x = 400
        self.ball_y = 300
        self.ball_dx = 5
        self.ball_dy = 5
        
        # ブロック初期化
        self.blocks = []
        colors = [self.RED, self.ORANGE, self.YELLOW, self.GREEN, self.BLUE]
        
        total_width = self.COLS * self.BLOCK_WIDTH
        start_x = (800 - total_width) // 2
        start_y = 60
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                block_x = start_x + col * self.BLOCK_WIDTH
                block_y = start_y + row * self.BLOCK_HEIGHT
                color = colors[row % len(colors)]
                self.blocks.append({
                    'rect': pygame.Rect(block_x, block_y, self.BLOCK_WIDTH, self.BLOCK_HEIGHT),
                    'color': color,
                    'points': (5 - row) * 10
                })
    
    def run(self):
        """ゲームメインループ"""
        game_running = True
        clock = pygame.time.Clock()
        
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_rect.collidepoint(event.pos):
                        game_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (self.game_over or self.game_clear):
                        self.score = 0
                        self.lives = 3
                        self.game_over = False
                        self.game_clear = False
                        self.reset_game()
            
            if not self.game_over and not self.game_clear:
                self.update()
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
    
    def update(self):
        """ゲーム更新"""
        # パドル操作（マウス）
        mouse_x = pygame.mouse.get_pos()[0]
        self.paddle_x = max(0, min(800 - self.PADDLE_WIDTH, mouse_x - self.PADDLE_WIDTH // 2))
        
        # ボール移動
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # 壁との当たり判定
        if self.ball_x <= self.BALL_SIZE // 2 or self.ball_x >= 800 - self.BALL_SIZE // 2:
            self.ball_dx *= -1
        if self.ball_y <= self.BALL_SIZE // 2:
            self.ball_dy *= -1
        
        # パドルとの当たり判定
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x - self.BALL_SIZE // 2, self.ball_y - self.BALL_SIZE // 2, 
                               self.BALL_SIZE, self.BALL_SIZE)
        
        if ball_rect.colliderect(paddle_rect) and self.ball_dy > 0:
            self.ball_dy *= -1
            hit_pos = (self.ball_x - self.paddle_x) / self.PADDLE_WIDTH
            self.ball_dx = (hit_pos - 0.5) * 10
        
        # ブロックとの当たり判定
        for block in self.blocks[:]:
            if ball_rect.colliderect(block['rect']):
                self.blocks.remove(block)
                self.score += block['points']
                self.ball_dy *= -1
                break
        
        # ボールが下に落ちた場合
        if self.ball_y > 600:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_x = 400
                self.ball_y = 300
                self.ball_dx = 5
                self.ball_dy = 5
        
        # クリア判定
        if not self.blocks:
            self.game_clear = True
    
    def draw(self):
        """画面描画"""
        self.screen.fill(self.BLACK)
        
        # 戻るボタン
        pygame.draw.rect(self.screen, (180, 50, 50), self.back_rect)
        back_text = self.font_small.render("ホームに戻る", True, self.WHITE)
        self.screen.blit(back_text, (self.back_rect.x + 10, self.back_rect.y + 10))
        
        if not self.game_over and not self.game_clear:
            # パドル描画
            pygame.draw.rect(self.screen, self.WHITE, 
                           (self.paddle_x, self.paddle_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
            
            # ボール描画
            pygame.draw.circle(self.screen, self.WHITE, 
                             (int(self.ball_x), int(self.ball_y)), self.BALL_SIZE // 2)
            
            # ブロック描画
            for block in self.blocks:
                pygame.draw.rect(self.screen, block['color'], block['rect'])
                pygame.draw.rect(self.screen, self.WHITE, block['rect'], 2)
            
            # UI描画
            score_text = self.font_medium.render(f"スコア: {self.score}", True, self.WHITE)
            self.screen.blit(score_text, (50, 520))
            
            lives_text = self.font_medium.render(f"残機: {self.lives}", True, self.WHITE)
            self.screen.blit(lives_text, (50, 550))
            
            instruction = self.font_small.render("マウスでパドルを操作", True, self.WHITE)
            self.screen.blit(instruction, (500, 520))
            
        elif self.game_over:
            game_over_text = self.font_large.render("ゲームオーバー", True, self.RED)
            self.screen.blit(game_over_text, (250, 250))
            
            final_score = self.font_medium.render(f"最終スコア: {self.score}", True, self.WHITE)
            self.screen.blit(final_score, (280, 320))
            
            restart_text = self.font_small.render("Rキーでリスタート", True, self.WHITE)
            self.screen.blit(restart_text, (320, 370))
            
        elif self.game_clear:
            clear_text = self.font_large.render("ゲームクリア！", True, self.GREEN)
            self.screen.blit(clear_text, (250, 250))
            
            final_score = self.font_medium.render(f"最終スコア: {self.score}", True, self.WHITE)
            self.screen.blit(final_score, (280, 320))
            
            restart_text = self.font_small.render("Rキーでリスタート", True, self.WHITE)
            self.screen.blit(restart_text, (320, 370))

def main():
    global current_screen, blackjack

    running = True
    button_rects = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_screen == "game2" and blackjack:
                action = blackjack.handle_event(event)
                if action == "continue":
                    blackjack.start_new_game()
                elif action == "home":
                    current_screen = "home"
                    blackjack = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if current_screen == "home":
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(pos):
                            if i == 5:  # ゲーム6
                                game6 = ShootingGame()  
                                result = game6.run()
                                if result == "home":
                                    current_screen = "home"
                                elif result == "quit":
                                    running = False
                            elif i == 2:  # ゲーム3
                                game3 = RhythmGame()
                                result = game3.run()
                                if result == "home":
                                    current_screen = "home"
                                elif result == "quit":
                                    running = False
                            elif i == 0:
                                clicker_main()
                            elif i == 1:
                                current_screen = "game2"
                                blackjack = BlackjackGame()
                            elif i == 3:  # ゲーム4 - ブロック崩し
                                game4 = BlockBreakerGame(screen)
                                game4.run()
                                current_screen = "home"
                            else:
                                if i == 4:
                                    current_screen = "game5"
                            
                            # game3, game4, game6以外の場合のみcurrent_screenを変更
                            if i not in [2, 3, 5]:
                                current_screen = f"game{i+1}"
                elif current_screen.startswith("game") and current_screen != "game6":
                    back_rect = draw_game_screen(int(current_screen[-1]))
                    if back_rect.collidepoint(pos):
                        current_screen = "home"
                if current_screen == "game2":
                    blackjack.handle_event(event)

        if current_screen == "home":
            button_rects = draw_home_screen()
        elif current_screen == "game2" and blackjack:
            blackjack.update()
            blackjack.draw()
        elif current_screen == "game5":
            game5 = HockeyGame(screen)
            game5.run()
            current_screen = "home"
        elif current_screen.startswith("game") and current_screen not in ["game3", "game6"]:
            game_num = int(current_screen[-1])
            draw_game_screen(game_num)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    main()
