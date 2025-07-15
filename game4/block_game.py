import pygame
import sys
from japanese_font import get_font  # あなたの環境で用意されている前提

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("ブロック崩し")
clock = pygame.time.Clock()

# ゲーム状態
current_screen = "home"  # home or block_breaker or playing_block_breaker

# プレイヤー（ホーム画面）の位置
player_x = 320
player_y = 300
player_speed = 5

# ブロック崩し用変数
paddle_width = 100
paddle_height = 10
paddle_speed = 7

ball_radius = 8

block_rows = 5
block_cols = 8
block_width = 60
block_height = 20
block_padding = 5
block_offset_x = 35
block_offset_y = 40

# ブロック崩しゲームの状態変数（プレイ中に更新）
paddle_x = (640 - paddle_width) // 2
paddle_y = 480 - 30
ball_x = 320
ball_y = 240
ball_speed_x = 4
ball_speed_y = -4
blocks = []
score = 0
game_over = False
game_clear = False

def create_blocks():
    blocks = []
    for row in range(block_rows):
        for col in range(block_cols):
            x = col * (block_width + block_padding) + block_offset_x
            y = row * (block_height + block_padding) + block_offset_y
            blocks.append(pygame.Rect(x, y, block_width, block_height))
    return blocks

def reset_block_breaker():
    global paddle_x, paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y
    global blocks, score, game_over, game_clear
    
    paddle_x = (640 - paddle_width) // 2
    paddle_y = 480 - 30
    ball_x = 320
    ball_y = 240
    ball_speed_x = 4
    ball_speed_y = -4
    blocks = create_blocks()
    score = 0
    game_over = False
    game_clear = False

def draw_home_screen():
    screen.fill((30, 30, 30))
    font_title = get_font(32)
    font_game = get_font(24)
    
    title = font_title.render("ミニゲーム集 ホーム画面", True, (255, 255, 255))
    screen.blit(title, (150, 50))
    
    # ブロック崩しゲームへのゲート（ボタン）
    gate_rect = pygame.Rect(270, 200, 100, 80)
    pygame.draw.rect(screen, (139, 69, 19), gate_rect)
    pygame.draw.rect(screen, (255, 255, 255), gate_rect, 3)
    gate_text = font_game.render("ブロック崩し", True, (255, 255, 255))
    text_x = gate_rect.x + (gate_rect.width - gate_text.get_width()) // 2
    text_y = gate_rect.y + (gate_rect.height - gate_text.get_height()) // 2
    screen.blit(gate_text, (text_x, text_y))
    
    # プレイヤーキャラ（黄色い丸）
    player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)
    pygame.draw.circle(screen, (255, 255, 0), (player_x, player_y), 15)
    pygame.draw.circle(screen, (0, 0, 0), (player_x - 5, player_y - 5), 3)
    pygame.draw.circle(screen, (0, 0, 0), (player_x + 5, player_y - 5), 3)
    
    instruction = font_game.render("矢印キーで移動、ゲートに触れてゲーム開始", True, (255, 255, 255))
    screen.blit(instruction, (100, 450))
    
    return player_rect, gate_rect

def draw_block_breaker_start():
    screen.fill((0, 0, 0))
    font_title = get_font(48)
    font_button = get_font(32)
    
    title = font_title.render("ブロック崩し", True, (255, 255, 255))
    title_rect = title.get_rect(center=(320, 150))
    screen.blit(title, title_rect)
    
    start_rect = pygame.Rect(220, 220, 200, 60)
    pygame.draw.rect(screen, (50, 180, 50), start_rect)
    pygame.draw.rect(screen, (255, 255, 255), start_rect, 3)
    start_text = font_button.render("スタート", True, (255, 255, 255))
    start_text_rect = start_text.get_rect(center=start_rect.center)
    screen.blit(start_text, start_text_rect)
    
    back_rect = pygame.Rect(220, 320, 200, 60)
    pygame.draw.rect(screen, (180, 50, 50), back_rect)
    pygame.draw.rect(screen, (255, 255, 255), back_rect, 3)
    back_text = font_button.render("ホームに戻る", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    
    return start_rect, back_rect

def draw_block_breaker_playing():
    global paddle_x, paddle_y, ball_x, ball_y, blocks, score, game_over, game_clear
    
    screen.fill((0, 0, 0))
    font_score = get_font(24)
    font_message = get_font(36)
    
    # パドル描画
    paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
    pygame.draw.rect(screen, (255, 255, 255), paddle_rect)
    
    # ボール描画
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_x), int(ball_y)), ball_radius)
    
    # ブロック描画
    for block in blocks:
        pygame.draw.rect(screen, (255, 255, 255), block)
    
    # スコア表示
    score_text = font_score.render(f"スコア: {score}", True, (0, 255, 0))
    screen.blit(score_text, (10, 10))
    
    # ゲームオーバー・クリアメッセージ
    if game_over:
        message = font_message.render("ゲームオーバー！ Rで再スタート", True, (255, 0, 0))
        rect = message.get_rect(center=(320, 240))
        screen.blit(message, rect)
    elif game_clear:
        message = font_message.render("クリア！ Rで再スタート", True, (0, 255, 0))
        rect = message.get_rect(center=(320, 240))
        screen.blit(message, rect)

def main():
    global current_screen
    global player_x, player_y
    global paddle_x, ball_x, ball_y, ball_speed_x, ball_speed_y
    global blocks, score, game_over, game_clear
    
    reset_block_breaker()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                if current_screen == "block_breaker":
                    start_rect, back_rect = draw_block_breaker_start()
                    if start_rect.collidepoint(pos):
                        current_screen = "playing_block_breaker"
                        reset_block_breaker()
                    elif back_rect.collidepoint(pos):
                        current_screen = "home"
                
                elif current_screen == "playing_block_breaker":
                    # なし（クリック判定は不要）
                    pass
            
            elif event.type == pygame.KEYDOWN:
                if current_screen == "playing_block_breaker":
                    if game_over or game_clear:
                        if event.key == pygame.K_r:
                            reset_block_breaker()
        
        keys = pygame.key.get_pressed()
        
        if current_screen == "home":
            # プレイヤー移動（矢印キー）
            new_x, new_y = player_x, player_y
            if keys[pygame.K_LEFT]:
                new_x -= player_speed
            if keys[pygame.K_RIGHT]:
                new_x += player_speed
            if keys[pygame.K_UP]:
                new_y -= player_speed
            if keys[pygame.K_DOWN]:
                new_y += player_speed
            
            # 画面端制限
            new_x = max(15, min(625, new_x))
            new_y = max(15, min(465, new_y))
            player_x, player_y = new_x, new_y
            
            player_rect, gate_rect = draw_home_screen()
            if player_rect.colliderect(gate_rect):
                current_screen = "block_breaker"
        
        elif current_screen == "block_breaker":
            start_rect, back_rect = draw_block_breaker_start()
        
        elif current_screen == "playing_block_breaker":
            if not (game_over or game_clear):
                # パドル操作
                if keys[pygame.K_LEFT] and paddle_x > 0:
                    paddle_x -= paddle_speed
                if keys[pygame.K_RIGHT] and paddle_x < 640 - paddle_width:
                    paddle_x += paddle_speed
                
                # ボール移動
                ball_x += ball_speed_x
                ball_y += ball_speed_y
                
                # 壁衝突判定
                if ball_x - ball_radius < 0 or ball_x + ball_radius > 640:
                    ball_speed_x *= -1
                if ball_y - ball_radius < 0:
                    ball_speed_y *= -1
                
                # パドルとの衝突判定
                paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
                ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius*2, ball_radius*2)
                if ball_rect.colliderect(paddle_rect) and ball_speed_y > 0:
                    ball_speed_y *= -1
                    offset = (ball_x - (paddle_x + paddle_width / 2)) / (paddle_width / 2)
                    ball_speed_x = 5 * offset
                
                # ブロックとの衝突判定
                hit_index = ball_rect.collidelist(blocks)
                if hit_index != -1:
                    blocks.pop(hit_index)
                    ball_speed_y *= -1
                    score += 10
                
                # ボールが落ちたか判定
                if ball_y > 480:
                    game_over = True
                
                # 全ブロック破壊判定
                if not blocks:
                    game_clear = True
            
            draw_block_breaker_playing()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
