import pygame
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
        self.image = pygame.image.load(f"{self.suit}_{self.rank}.png").convert_alpha()
        self.rect = self.image.get_rect()
    
    def getvalue(self):
        if self.rank == ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11
        else:
            return int(self.rank)


class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.deal_initial_cards()

    def create_deck(self):
        suits = ["heart", "daiya", "clover", "spade"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        return [Card(suit, rank) for suit in suits for rank in ranks]

    def deal_initial_cards(self):
        for _ in range(2):
            self.player_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())

    def calculate_hand_value(self, hand):
        value = sum(card.getvalue() for card in hand)
        aces = sum(1 for card in hand if card.rank == "A")
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value
    
    def start_new_game(self):
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.game_state = "player_turn"  # "dealer_turn", "game_over"
        self.message = "あなたのターン"
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.key == pygame.K_h:

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
        else:
            game_num = int(current_screen[-1])
            draw_game_screen(game_num)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
