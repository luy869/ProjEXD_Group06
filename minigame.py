import pygame
import random
import sys
from japanese_font import get_font

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("こうかとんミニゲーム集 ホーム画面")
clock = pygame.time.Clock()

# 現在の画面状態（home または game1~game5）
current_screen = "home"

# ボタンリスト
games = ["ゲーム1", "ゲーム2", "ゲーム3", "ゲーム4", "ゲーム5"]

def draw_home_screen():
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

class Card(pygame.sprite.Sprite):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.image = pygame.image.load(f"ex5/fig/{self.suit}_{self.rank}.png").convert_alpha()
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
                            if i == 1:
                                current_screen = "game2"
                                blackjack = BlackjackGame()
                            else:
                                # ゲーム1, 3, 4, 5は仮の画面として扱う
                                if i == 0:
                                    current_screen = "game1"
                                elif i == 2:
                                    current_screen = "game3"
                                elif i == 3:
                                    current_screen = "game4"
                                elif i == 4:
                                    current_screen = "game5"
                            current_screen = f"game{i+1}"
                else:
                    # ゲーム画面で「ホームに戻る」ボタンを押したら戻る
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

            
        else:
            game_num = int(current_screen[-1])
            draw_game_screen(game_num)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
