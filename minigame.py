import pygame
import sys
import random
from japanese_font import get_font

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("こうかとんミニゲーム集 ホーム画面")
clock = pygame.time.Clock()

# 現在の画面状態（home, game1~game6, または playing_game6）
current_screen = "home"

# ボタンリスト
games = ["ゲーム1", "ゲーム2", "ゲーム3", "ゲーム4", "ゲーム5", "ゲーム6"]

# キャラクターの初期位置
player_x = 320
player_y = 300
player_speed = 5

# ゲーム6用の変数
game6_player_x = 320
game6_player_y = 400
game6_player_speed = 7
falling_items = []
score = 0

# 門の位置とサイズ
gates = []
for i in range(6):
    # 2列3行で門を配置
    col = i % 2
    row = i // 2
    gate_x = 120 + col * 320
    gate_y = 150 + row * 100
    gates.append(pygame.Rect(gate_x, gate_y, 120, 80))

def draw_home_screen():
    """
    ホーム画面を描写
    """
    screen.fill((30, 30, 30))
    font_title = get_font(32)
    font_gate = get_font(20)

    # タイトル表示
    title = font_title.render("こうかとんミニゲーム集", True, (255, 255, 255))
    screen.blit(title, (100, 50))

    # 門を描画
    for i, gate in enumerate(gates):
        pygame.draw.rect(screen, (139, 69, 19), gate)  # 茶色の門
        pygame.draw.rect(screen, (255, 255, 255), gate, 3)  # 白い枠線
        gate_text = font_gate.render(f"ゲーム{i+1}", True, (255, 255, 255))
        # 文字を門の中央に配置
        text_x = gate.x + (gate.width - gate_text.get_width()) // 2
        text_y = gate.y + (gate.height - gate_text.get_height()) // 2
        screen.blit(gate_text, (text_x, text_y))

    # プレイヤーキャラクター（こうかとん）を描画
    player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)
    pygame.draw.circle(screen, (255, 255, 0), (player_x, player_y), 15)  # 黄色い円
    pygame.draw.circle(screen, (0, 0, 0), (player_x - 5, player_y - 5), 3)  # 左目
    pygame.draw.circle(screen, (0, 0, 0), (player_x + 5, player_y - 5), 3)  # 右目
    
    # 操作説明
    instruction_text = font_gate.render("WASDキーで移動、門をくぐってゲームを選択", True, (255, 255, 255))
    screen.blit(instruction_text, (50, 450))

    return player_rect

def draw_game_screen(game_number):
    """
    それぞれのゲームへの遷移
    """
    screen.fill((0, 0, 0))
    font_title = get_font(64)
    font_button = get_font(32)

    # ゲームタイトル表示
    title_text = font_title.render(f"ゲーム{game_number}", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(320, 150))
    screen.blit(title_text, title_rect)

    # スタートボタン
    start_rect = pygame.Rect(220, 220, 200, 60)
    pygame.draw.rect(screen, (50, 180, 50), start_rect)
    pygame.draw.rect(screen, (255, 255, 255), start_rect, 3)
    start_text = font_button.render("スタート", True, (255, 255, 255))
    start_text_rect = start_text.get_rect(center=start_rect.center)
    screen.blit(start_text, start_text_rect)

    # 「ホームに戻る」ボタン
    back_rect = pygame.Rect(220, 320, 200, 60)
    pygame.draw.rect(screen, (180, 50, 50), back_rect)
    pygame.draw.rect(screen, (255, 255, 255), back_rect, 3)
    back_text = font_button.render("ホームに戻る", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)

    return start_rect, back_rect

def draw_game6():
    """
    ゲーム6の実際のゲーム画面
    """
    global game6_player_x, game6_player_y, falling_items, score
    
    screen.fill((0, 50, 100))  # 濃い青色の背景
    font_title = get_font(32)
    font_ui = get_font(24)
    
    # ゲームタイトル
    title_text = font_title.render("ゲーム6: こうかとんキャッチゲーム", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(320, 50))
    screen.blit(title_text, title_rect)
    
    # スコア表示
    score_text = font_ui.render(f"スコア: {score}", True, (255, 255, 255))
    screen.blit(score_text, (50, 100))
    
    # 操作説明
    instruction_text = font_ui.render("WASDキーで移動してアイテムをキャッチしよう！", True, (255, 255, 255))
    screen.blit(instruction_text, (50, 130))
    
    # プレイヤーキャラクター（こうかとん）を描画
    pygame.draw.circle(screen, (255, 255, 0), (game6_player_x, game6_player_y), 20)  # 黄色い円
    pygame.draw.circle(screen, (0, 0, 0), (game6_player_x - 8, game6_player_y - 8), 4)  # 左目
    pygame.draw.circle(screen, (0, 0, 0), (game6_player_x + 8, game6_player_y - 8), 4)  # 右目
    pygame.draw.polygon(screen, (255, 165, 0), [(game6_player_x, game6_player_y + 5), 
                                               (game6_player_x - 6, game6_player_y + 12), 
                                               (game6_player_x + 6, game6_player_y + 12)])  # オレンジのくちばし
    
    # 落ちてくるアイテムを描画
    for item in falling_items:
        pygame.draw.circle(screen, (255, 0, 0), (item['x'], item['y']), 10)  # 赤い円
    
    # 戻るボタン
    back_rect = pygame.Rect(520, 20, 100, 40)
    pygame.draw.rect(screen, (180, 50, 50), back_rect)
    pygame.draw.rect(screen, (255, 255, 255), back_rect, 2)
    back_text = font_ui.render("戻る", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    
    return back_rect

def main():
    global current_screen, player_x, player_y, game6_player_x, game6_player_y, falling_items, score

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if current_screen == "playing_game6":
                    # ゲーム6のプレイ中の戻るボタン判定
                    back_rect = pygame.Rect(520, 20, 100, 40)
                    if back_rect.collidepoint(pos):
                        current_screen = "home"
                        player_x = 320
                        player_y = 300
                        # ゲーム6の状態をリセット
                        game6_player_x = 320
                        game6_player_y = 400
                        falling_items.clear()
                        score = 0
                elif current_screen != "home":
                    # ゲーム画面でボタンクリック判定（描画前に判定）
                    game_num = int(current_screen[-1])
                    start_rect = pygame.Rect(220, 220, 200, 60)
                    back_rect = pygame.Rect(220, 320, 200, 60)
                    
                    if start_rect.collidepoint(pos):
                        # スタートボタンが押された
                        if game_num == 6:
                            current_screen = "playing_game6"
                        else:
                            print(f"ゲーム{current_screen[-1]}をスタート！")
                    elif back_rect.collidepoint(pos):
                        current_screen = "home"
                        # プレイヤーの位置を初期位置にリセット
                        player_x = 320
                        player_y = 300

        # キーボード入力の処理（ホーム画面のみ）
        if current_screen == "home":
            keys = pygame.key.get_pressed()
            
            # WASDキーでキャラクターを移動
            new_x, new_y = player_x, player_y
            if keys[pygame.K_a]:  # A（左）
                new_x -= player_speed
            if keys[pygame.K_d]:  # D（右）
                new_x += player_speed
            if keys[pygame.K_w]:  # W（上）
                new_y -= player_speed
            if keys[pygame.K_s]:  # S（下）
                new_y += player_speed
            
            # 画面外に出ないように制限
            new_x = max(15, min(625, new_x))
            new_y = max(15, min(465, new_y))
            
            player_x, player_y = new_x, new_y
            
            # プレイヤーと門の衝突判定
            player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)
            for i, gate in enumerate(gates):
                if player_rect.colliderect(gate):
                    current_screen = f"game{i+1}"
                    break
        
        elif current_screen == "playing_game6":
            keys = pygame.key.get_pressed()
            
            # ゲーム6でのプレイヤー移動
            if keys[pygame.K_a] and game6_player_x > 20:  # A（左）
                game6_player_x -= game6_player_speed
            if keys[pygame.K_d] and game6_player_x < 620:  # D（右）
                game6_player_x += game6_player_speed
            if keys[pygame.K_w] and game6_player_y > 170:  # W（上）
                game6_player_y -= game6_player_speed
            if keys[pygame.K_s] and game6_player_y < 460:  # S（下）
                game6_player_y += game6_player_speed
            
            # 新しいアイテムを追加（ランダムに）
            if random.randint(1, 60) == 1:  # 60分の1の確率で新しいアイテム
                new_item = {
                    'x': random.randint(20, 620),
                    'y': 160,
                    'speed': random.randint(2, 5)
                }
                falling_items.append(new_item)
            
            # アイテムを落下させる
            for item in falling_items[:]:
                item['y'] += item['speed']
                
                # プレイヤーとアイテムの衝突判定
                distance = ((game6_player_x - item['x'])**2 + (game6_player_y - item['y'])**2)**0.5
                if distance < 30:  # プレイヤーとアイテムが接触
                    falling_items.remove(item)
                    score += 1
                
                # 画面下に落ちたアイテムを削除
                elif item['y'] > 480:
                    falling_items.remove(item)

        if current_screen == "home":
            draw_home_screen()
        elif current_screen == "playing_game6":
            draw_game6()
        else:
            game_num = int(current_screen[-1])
            start_rect, back_rect = draw_game_screen(game_num)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
