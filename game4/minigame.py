import pygame
import sys
import os
from japanese_font import get_font

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("こうかとんミニゲーム集 ホーム画面")
clock = pygame.time.Clock()

# 現在の画面状態（home または game1~game5）
current_screen = "home"

# ボタンリスト
games = ["こうかとんクリッカー", "ゲーム2", "ゲーム3", "ゲーム4", "ゲーム5"]

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
    image_path = os.path.join(base_dir, "fig", "koukaton.png")
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
                            if i == 0:
                                clicker_main()
                            else:
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
