import pygame
import sys
import random
import math
from japanese_font import get_font

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("こうかとんミニゲーム集 ホーム画面")
clock = pygame.time.Clock()

# 現在の画面状態（home または game1~game6）
current_screen = "home"

# ボタンリスト
games = ["ゲーム1", "ゲーム2", "ゲーム3", "ゲーム4", "ゲーム5", "ゲーム6"]

class TouhouGame:
    """東方風弾幕ゲーム（本格的な実装）"""
    def __init__(self):
        pygame.mixer.init()
        self.screen = screen
        self.clock = clock
        self.width, self.height = 800, 600
        
        # プレイヤー設定
        self.player_pos = [400, 500]
        self.player_size = 20
        self.player_speed = 5
        self.player_bullets = []
        self.player_power = 1
        self.shoot_timer = 0
        
        # ゲーム進行状態
        self.game_state = "stage"  # "stage" or "boss"
        self.stage_timer = 0
        self.stage_duration = 1800  # 30秒
        
        # 雑魚敵設定
        self.enemies = []
        self.enemy_spawn_timer = 0
        
        # ボス設定
        self.boss_pos = [400, 100]
        self.boss_hp = 1000
        self.boss_max_hp = 1000
        self.boss_phase = 1
        self.boss_move_timer = 0
        
        # 弾幕設定
        self.enemy_bullets = []
        self.pattern_timer = 0
        self.spell_timer = 0
        
        # ゲーム状態
        self.score = 0
        self.lives = 3
        self.bombs = 3
        self.invincible_timer = 0
        self.game_over = False
        self.stage_clear = False
        
        # BGMとSE設定
        self.init_audio()
    
    def init_audio(self):
        """音声システムの初期化"""
        try:
            # BGMファイルを順番に試す
            bgm_files = ["stage_bgm.mp3", "bgm.mp3", "stage_bgm.wav", "bgm.wav"]
            for bgm_file in bgm_files:
                try:
                    pygame.mixer.music.load(bgm_file)
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                    break
                except:
                    continue
        except:
            pass
        
        # 効果音の初期化
        try:
            self.shoot_sound = pygame.mixer.Sound("shoot.wav")
            self.shoot_sound.set_volume(0.1)
        except:
            self.shoot_sound = None
        
        try:
            self.enemy_death_sound = pygame.mixer.Sound("enemy_death.wav")
            self.enemy_death_sound.set_volume(0.2)
        except:
            self.enemy_death_sound = None
    
    def spawn_enemy(self):
        """雑魚敵の生成"""
        enemy_types = ["normal", "fast", "shooter"]
        enemy_type = random.choice(enemy_types)
        
        enemy = {
            'x': random.randint(50, self.width - 50),
            'y': -30,
            'type': enemy_type,
            'hp': 3 if enemy_type == "normal" else 1,
            'speed': 1 if enemy_type == "normal" else 2,
            'shoot_timer': 0,
            'move_pattern': random.choice(["straight", "zigzag", "sine"])
        }
        self.enemies.append(enemy)
    
    def update_enemies(self):
        """雑魚敵の更新"""
        for enemy in self.enemies[:]:
            # 敵の移動
            if enemy['move_pattern'] == "straight":
                enemy['y'] += enemy['speed']
            elif enemy['move_pattern'] == "zigzag":
                enemy['y'] += enemy['speed']
                enemy['x'] += math.sin(enemy['y'] * 0.1) * 3
            elif enemy['move_pattern'] == "sine":
                enemy['y'] += enemy['speed']
                enemy['x'] += math.sin(enemy['y'] * 0.05) * 2
            
            # 敵の射撃
            if enemy['type'] == "shooter":
                enemy['shoot_timer'] += 1
                if enemy['shoot_timer'] % 60 == 0:  # 1秒ごと
                    # プレイヤーに向かって弾を撃つ
                    dx = self.player_pos[0] - enemy['x']
                    dy = self.player_pos[1] - enemy['y']
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        bullet = {
                            'x': enemy['x'],
                            'y': enemy['y'],
                            'dx': (dx / distance) * 2,
                            'dy': (dy / distance) * 2,
                            'color': (255, 200, 100),
                            'size': 4
                        }
                        self.enemy_bullets.append(bullet)
            
            # 画面外に出た敵を削除
            if enemy['y'] > self.height + 50:
                self.enemies.remove(enemy)
            
            # プレイヤー弾との当たり判定
            enemy_rect = pygame.Rect(enemy['x']-15, enemy['y']-15, 30, 30)
            for bullet in self.player_bullets[:]:
                bullet_rect = pygame.Rect(bullet['x']-2, bullet['y']-2, 4, 4)
                if enemy_rect.colliderect(bullet_rect):
                    self.player_bullets.remove(bullet)
                    enemy['hp'] -= 1
                    self.score += 5
                    
                    if enemy['hp'] <= 0:
                        self.enemies.remove(enemy)
                        self.score += 50
                        if self.enemy_death_sound:
                            self.enemy_death_sound.play()
                    break
    
    def create_boss_pattern(self):
        """ボスの弾幕パターン"""
        if self.boss_phase == 1:
            # 円形弾幕
            for angle in range(0, 360, 12):
                rad = math.radians(angle + self.pattern_timer * 2)
                bullet = {
                    'x': self.boss_pos[0],
                    'y': self.boss_pos[1],
                    'dx': math.cos(rad) * 2,
                    'dy': math.sin(rad) * 2,
                    'color': (255, 100, 100),
                    'size': 4
                }
                self.enemy_bullets.append(bullet)
        
        elif self.boss_phase == 2:
            # スパイラル弾幕
            for i in range(8):
                angle = i * 45 + self.pattern_timer * 3
                rad = math.radians(angle)
                bullet = {
                    'x': self.boss_pos[0],
                    'y': self.boss_pos[1],
                    'dx': math.cos(rad) * 3,
                    'dy': math.sin(rad) * 3,
                    'color': (100, 255, 100),
                    'size': 5
                }
                self.enemy_bullets.append(bullet)
        
        elif self.boss_phase == 3:
            # ランダム弾幕（スペルカード）
            for _ in range(15):
                angle = random.uniform(0, 360)
                rad = math.radians(angle)
                speed = random.uniform(1, 4)
                bullet = {
                    'x': self.boss_pos[0],
                    'y': self.boss_pos[1],
                    'dx': math.cos(rad) * speed,
                    'dy': math.sin(rad) * speed,
                    'color': (255, 255, 100),
                    'size': 6
                }
                self.enemy_bullets.append(bullet)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return "home"
                elif event.key == pygame.K_r and (self.game_over or self.stage_clear):
                    self.__init__()
                elif event.key == pygame.K_x and self.bombs > 0 and not self.game_over:
                    # ボム使用
                    self.bombs -= 1
                    self.enemy_bullets.clear()
                    self.enemies.clear()
                    self.invincible_timer = 180
                    if self.game_state == "boss":
                        self.boss_hp -= 100
        return None
    
    def update(self):
        if self.game_over or self.stage_clear:
            return
        
        # プレイヤー移動
        keys = pygame.key.get_pressed()
        speed = self.player_speed // 2 if keys[pygame.K_LSHIFT] else self.player_speed
        
        if keys[pygame.K_LEFT] and self.player_pos[0] > 20:
            self.player_pos[0] -= speed
        if keys[pygame.K_RIGHT] and self.player_pos[0] < self.width - 20:
            self.player_pos[0] += speed
        if keys[pygame.K_UP] and self.player_pos[1] > 20:
            self.player_pos[1] -= speed
        if keys[pygame.K_DOWN] and self.player_pos[1] < self.height - 20:
            self.player_pos[1] += speed
        
        # プレイヤー連射システム
        self.shoot_timer += 1
        if keys[pygame.K_z] and self.shoot_timer >= 8:  # 連射間隔
            if len(self.player_bullets) < 20:
                bullet = {
                    'x': self.player_pos[0],
                    'y': self.player_pos[1] - 20,
                    'dy': -8
                }
                self.player_bullets.append(bullet)
                self.shoot_timer = 0
                if self.shoot_sound:
                    self.shoot_sound.play()
        
        # プレイヤー弾更新
        for bullet in self.player_bullets[:]:
            bullet['y'] += bullet['dy']
            if bullet['y'] < 0:
                self.player_bullets.remove(bullet)
            elif self.game_state == "boss":
                # ボスとの当たり判定
                boss_rect = pygame.Rect(self.boss_pos[0]-30, self.boss_pos[1]-30, 60, 60)
                bullet_rect = pygame.Rect(bullet['x']-2, bullet['y']-2, 4, 4)
                if boss_rect.colliderect(bullet_rect):
                    self.player_bullets.remove(bullet)
                    self.boss_hp -= self.player_power
                    self.score += 10
        
        # ゲーム進行管理
        if self.game_state == "stage":
            self.stage_timer += 1
            
            # 雑魚敵生成
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= 90:  # 1.5秒ごと
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
            
            # 雑魚敵更新
            self.update_enemies()
            
            # ボス戦への移行
            if self.stage_timer >= self.stage_duration:
                self.game_state = "boss"
                self.enemies.clear()
                self.enemy_bullets.clear()
                # ボス戦BGMに変更
                try:
                    boss_bgm_files = ["boss_bgm.mp3", "boss_bgm.wav"]
                    for bgm_file in boss_bgm_files:
                        try:
                            pygame.mixer.music.load(bgm_file)
                            pygame.mixer.music.play(-1)
                            break
                        except:
                            continue
                except:
                    pass
        
        elif self.game_state == "boss":
            # ボス移動
            self.boss_move_timer += 1
            if self.boss_move_timer < 120:
                self.boss_pos[0] += math.sin(self.boss_move_timer * 0.05) * 2
            else:
                self.boss_move_timer = 0
            
            # ボスフェーズ管理
            if self.boss_hp <= 700 and self.boss_phase == 1:
                self.boss_phase = 2
                self.enemy_bullets.clear()
            elif self.boss_hp <= 300 and self.boss_phase == 2:
                self.boss_phase = 3
                self.enemy_bullets.clear()
            
            # 弾幕生成
            self.pattern_timer += 1
            if self.pattern_timer % 30 == 0:
                self.create_boss_pattern()
        
        # 敵弾更新
        for bullet in self.enemy_bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            if (bullet['x'] < -20 or bullet['x'] > self.width + 20 or
                bullet['y'] < -20 or bullet['y'] > self.height + 20):
                self.enemy_bullets.remove(bullet)
        
        # プレイヤーとの当たり判定
        if self.invincible_timer <= 0:
            player_rect = pygame.Rect(
                self.player_pos[0] - 3, self.player_pos[1] - 3, 6, 6
            )
            
            # 敵弾との当たり判定
            for bullet in self.enemy_bullets:
                bullet_rect = pygame.Rect(
                    bullet['x'] - bullet['size']//2, 
                    bullet['y'] - bullet['size']//2, 
                    bullet['size'], bullet['size']
                )
                if player_rect.colliderect(bullet_rect):
                    self.lives -= 1
                    self.invincible_timer = 120
                    if self.lives <= 0:
                        self.game_over = True
                    break
            
            # 雑魚敵との接触判定
            for enemy in self.enemies:
                enemy_rect = pygame.Rect(enemy['x']-15, enemy['y']-15, 30, 30)
                if player_rect.colliderect(enemy_rect):
                    self.lives -= 1
                    self.invincible_timer = 120
                    self.enemies.remove(enemy)
                    if self.lives <= 0:
                        self.game_over = True
                    break
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # ボス撃破判定
        if self.game_state == "boss" and self.boss_hp <= 0:
            self.stage_clear = True
    
    def draw(self):
        self.screen.fill((5, 5, 25))
        
        # 道中の雑魚敵描画
        for enemy in self.enemies:
            color = (255, 100, 100) if enemy['type'] == "normal" else (100, 255, 100) if enemy['type'] == "fast" else (255, 255, 100)
            pygame.draw.circle(self.screen, color, (int(enemy['x']), int(enemy['y'])), 15)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(enemy['x']), int(enemy['y'])), 10)
        
        # ボス描画
        if self.game_state == "boss" and not self.stage_clear:
            pygame.draw.circle(self.screen, (200, 100, 200), self.boss_pos, 30)
            pygame.draw.circle(self.screen, (255, 150, 255), self.boss_pos, 25)
            
            # ボスHP表示
            hp_ratio = max(0, self.boss_hp / self.boss_max_hp)
            hp_bar_width = int(300 * hp_ratio)
            pygame.draw.rect(self.screen, (100, 100, 100), (250, 20, 300, 10))
            pygame.draw.rect(self.screen, (255, 0, 0), (250, 20, hp_bar_width, 10))
        
        # ステージ進行表示
        if self.game_state == "stage":
            progress = min(1.0, self.stage_timer / self.stage_duration)
            progress_width = int(200 * progress)
            pygame.draw.rect(self.screen, (50, 50, 50), (300, 40, 200, 8))
            pygame.draw.rect(self.screen, (100, 255, 100), (300, 40, progress_width, 8))
            stage_text = get_font(16).render("Stage Progress", True, (255, 255, 255))
            self.screen.blit(stage_text, (300, 50))
        
        # プレイヤー描画
        if self.invincible_timer == 0 or self.invincible_timer % 10 < 5:
            pygame.draw.circle(self.screen, (100, 255, 100), self.player_pos, 8)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LSHIFT]:
                pygame.draw.circle(self.screen, (255, 255, 255), self.player_pos, 3, 1)
        
        # プレイヤー弾描画
        for bullet in self.player_bullets:
            pygame.draw.circle(self.screen, (255, 255, 255), (int(bullet['x']), int(bullet['y'])), 3)
        
        # 敵弾描画
        for bullet in self.enemy_bullets:
            pygame.draw.circle(self.screen, bullet['color'], 
                             (int(bullet['x']), int(bullet['y'])), bullet['size'])
        
        # UI描画
        score_text = get_font(20).render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        lives_text = get_font(20).render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 35))
        
        bombs_text = get_font(20).render(f"Bombs: {self.bombs}", True, (255, 255, 255))
        self.screen.blit(bombs_text, (10, 60))
        
        if self.game_state == "boss":
            phase_text = get_font(20).render(f"Boss Phase: {self.boss_phase}", True, (255, 255, 255))
            self.screen.blit(phase_text, (10, 85))
        else:
            enemies_text = get_font(20).render(f"Enemies: {len(self.enemies)}", True, (255, 255, 255))
            self.screen.blit(enemies_text, (10, 85))
        
        # 操作説明
        controls = [
            "矢印キー: 移動",
            "Shift: 低速移動", 
            "Z: 射撃(連射)",
            "X: ボム",
            "ESC: ホームに戻る"
        ]
        for i, control in enumerate(controls):
            control_text = get_font(14).render(control, True, (200, 200, 200))
            self.screen.blit(control_text, (10, self.height - 80 + i * 15))
        
        if self.game_over:
            game_over_text = get_font(48).render("GAME OVER", True, (255, 0, 0))
            restart_text = get_font(24).render("Rキーでリスタート", True, (255, 255, 255))
            self.screen.blit(game_over_text, (250, 250))
            self.screen.blit(restart_text, (280, 300))
        
        elif self.stage_clear:
            clear_text = get_font(48).render("STAGE CLEAR!", True, (0, 255, 0))
            restart_text = get_font(24).render("Rキーでリスタート", True, (255, 255, 255))
            final_score = get_font(24).render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(clear_text, (220, 250))
            self.screen.blit(final_score, (280, 300))
            self.screen.blit(restart_text, (280, 330))
    
    def run(self):
        while True:
            result = self.handle_events()
            if result:
                return result
                
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

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
        rect = pygame.Rect(300, 150 + i * 60, 200, 50)
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
    
    if game_number == 6:
        # ゲーム6のタイトル画面
        title_text = font.render("東方風弾幕ゲーム", True, (255, 255, 255))
        screen.blit(title_text, (150, 180))
        
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
                            if i == 5:  # ゲーム6
                                current_screen = "game6"
                            else:
                                current_screen = f"game{i+1}"
                elif current_screen == "game6":
                    # ゲーム6のタイトル画面でのボタン処理
                    start_rect, back_rect = draw_game_screen(6)
                    if start_rect.collidepoint(pos):
                        # スタートボタンが押された時に東方風弾幕ゲームを開始
                        game6 = TouhouGame()
                        result = game6.run()
                        if result == "home":
                            current_screen = "home"
                        elif result == "quit":
                            running = False
                    elif back_rect.collidepoint(pos):
                        current_screen = "home"
                elif current_screen.startswith("game") and current_screen != "game6":
                    # 他のゲーム画面で「ホームに戻る」ボタンを押したら戻る
                    back_rect = draw_game_screen(int(current_screen[-1]))
                    if back_rect.collidepoint(pos):
                        current_screen = "home"

        if current_screen == "home":
            button_rects = draw_home_screen()
        elif current_screen == "game6":
            draw_game_screen(6)
        elif current_screen.startswith("game"):
            game_num = int(current_screen[-1])
            draw_game_screen(game_num)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
