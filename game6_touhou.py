import pygame
import math
import random
import sys
import os
from japanese_font import get_font

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.slow_speed = 2
        self.radius = 3
        self.invulnerable = 0
        self.lives = 3
        self.power = 100
        self.character = "reimu"  # 霊夢
        
    def update(self, keys):
        speed = self.slow_speed if keys[pygame.K_LSHIFT] else self.speed
        
        if keys[pygame.K_LEFT] and self.x > 20:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < 780:
            self.x += speed
        if keys[pygame.K_UP] and self.y > 20:
            self.y -= speed
        if keys[pygame.K_DOWN] and self.y < 580:
            self.y += speed
            
        if self.invulnerable > 0:
            self.invulnerable -= 1
    
    def draw(self, screen):
        # 霊夢らしい巫女キャラクター描画
        if self.invulnerable % 10 < 5:  # 点滅効果
            # 本体（赤色）
            pygame.draw.circle(screen, (255, 100, 100), (int(self.x), int(self.y)), 8)
            # 髪（黒色）
            pygame.draw.circle(screen, (50, 50, 50), (int(self.x), int(self.y - 5)), 6)
            # 髪飾り（赤色）
            pygame.draw.circle(screen, (255, 50, 50), (int(self.x - 3), int(self.y - 8)), 2)
            pygame.draw.circle(screen, (255, 50, 50), (int(self.x + 3), int(self.y - 8)), 2)
            
            # 当たり判定の表示（低速時）
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 1)

class PlayerBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.radius = 3
        
    def update(self):
        self.y -= self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)

class EnemyBullet:
    def __init__(self, x, y, angle, speed, color=(255, 100, 100)):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.radius = 4
        self.color = color
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class SmallEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 30
        self.max_hp = 30
        self.radius = 12
        self.speed = 1.5
        self.bullet_timer = 0
        self.move_timer = 0
        self.move_direction = random.choice([-1, 1])
        
    def update(self, player):
        self.bullet_timer += 1
        self.move_timer += 1
        
        # 左右に移動しながら下に降りる
        self.x += self.move_direction * self.speed
        self.y += 0.8
        
        # 画面端で反転
        if self.x < 50 or self.x > 750:
            self.move_direction *= -1
            
        # 時々方向を変える
        if self.move_timer % 120 == 0:
            self.move_direction = random.choice([-1, 1])
    
    def shoot(self):
        """雑魚敵の弾幕（シンプル）"""
        bullets = []
        if self.bullet_timer % 60 == 0:  # 1秒に1回射撃
            # プレイヤー方向に3way弾
            for i in range(3):
                angle = math.pi / 2 + (i - 1) * 0.3  # 下向き扇状
                bullets.append(EnemyBullet(self.x, self.y, angle, 2, (255, 150, 150)))
        return bullets
    
    def draw(self, screen):
        # 雑魚敵キャラクター（小さめの妖精風）
        # 本体
        pygame.draw.circle(screen, (150, 255, 150), (int(self.x), int(self.y)), self.radius)
        # 目
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 4), int(self.y - 3)), 2)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 4), int(self.y - 3)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x - 4), int(self.y - 3)), 1)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 4), int(self.y - 3)), 1)

class Enemy:
    def __init__(self, x, y, hp=300):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.radius = 25
        self.bullet_timer = 0
        self.pattern_timer = 0
        self.pattern_phase = 0
        self.name = "妖怪"
        
    def update(self, player):
        self.bullet_timer += 1
        self.pattern_timer += 1
        
        # 移動パターン（東方らしいS字移動）
        if self.pattern_timer < 120:
            self.x += math.sin(self.pattern_timer * 0.08) * 3
        elif self.pattern_timer < 240:
            self.x += math.cos(self.pattern_timer * 0.06) * 2
        elif self.pattern_timer < 360:
            self.x += math.sin(self.pattern_timer * 0.04) * 1.5
        else:
            self.pattern_timer = 0
            
    def shoot_pattern1(self):
        """放射状弾幕（基本パターン）"""
        bullets = []
        if self.bullet_timer % 25 == 0:
            for i in range(16):
                angle = (i * 22.5 + self.bullet_timer * 1.5) * math.pi / 180
                bullets.append(EnemyBullet(self.x, self.y, angle, 2.5, (255, 100, 100)))
        return bullets
        
    def shoot_pattern2(self):
        """螺旋弾幕（綺麗なパターン）"""
        bullets = []
        if self.bullet_timer % 6 == 0:
            for i in range(4):
                angle = (self.bullet_timer * 8 + i * 90) * math.pi / 180
                bullets.append(EnemyBullet(self.x, self.y, angle, 3, (100, 255, 150)))
                # 二重螺旋
                angle2 = (self.bullet_timer * 8 + i * 90 + 45) * math.pi / 180
                bullets.append(EnemyBullet(self.x, self.y, angle2, 2, (150, 255, 100)))
        return bullets
        
    def shoot_pattern3(self):
        """花弾幕（東方らしいパターン）"""
        bullets = []
        if self.bullet_timer % 30 == 0:
            for i in range(8):
                # 外側の花びら
                angle = (i * 45 + self.bullet_timer * 2) * math.pi / 180
                bullets.append(EnemyBullet(self.x, self.y, angle, 3.5, (255, 150, 255)))
                # 内側の花びら
                angle2 = (i * 45 + self.bullet_timer * 2 + 22.5) * math.pi / 180
                bullets.append(EnemyBullet(self.x, self.y, angle2, 2.5, (255, 200, 255)))
        return bullets
        
    def shoot_pattern4(self):
        """レーザー風直線弾幕"""
        bullets = []
        if self.bullet_timer % 15 == 0:
            for i in range(5):
                angle = math.pi / 2 + (i - 2) * 0.3  # 下向き扇状
                bullets.append(EnemyBullet(self.x, self.y, angle, 4, (255, 255, 100)))
        return bullets
        
    def shoot(self):
        """弾幕パターンの切り替え（東方らしく時間で変化）"""
        pattern = (self.bullet_timer // 200) % 4
        if pattern == 0:
            return self.shoot_pattern1()
        elif pattern == 1:
            return self.shoot_pattern2()
        elif pattern == 2:
            return self.shoot_pattern3()
        else:
            return self.shoot_pattern4()
            
    def draw(self, screen):
        # 敵キャラクター（東方らしい妖怪風）
        # 本体
        pygame.draw.circle(screen, (200, 100, 255), (int(self.x), int(self.y)), self.radius)
        # 目
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 8), int(self.y - 5)), 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 8), int(self.y - 5)), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x - 8), int(self.y - 5)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 8), int(self.y - 5)), 2)
        
        # HPバー
        bar_width = 150
        bar_height = 12
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 50
        
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        hp_width = int((self.hp / self.max_hp) * bar_width)
        pygame.draw.rect(screen, (255, 50, 50), (bar_x, bar_y, hp_width, bar_height))
        
        # 敵の名前表示
        font = get_font(20)
        name_text = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (bar_x, bar_y - 25))

class TouhouGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("東方風弾幕ゲーム")
        self.clock = pygame.time.Clock()
        
        # BGM初期化
        try:
            pygame.mixer.init()
            self.load_bgm()
        except:
            print("音声システムの初期化に失敗しました")
        
        # ゲーム状態
        self.state = "title"  # title, playing, game_over, victory
        self.game_phase = "small_enemies"  # small_enemies, boss_fight
        self.game_timer = 0  # ゲーム開始からの時間
        self.player = Player(400, 500)
        self.enemy = Enemy(400, 100)
        self.small_enemies = []
        self.small_enemy_spawn_timer = 0
        self.player_bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.shooting = False
        self.shoot_timer = 0
        
    def load_bgm(self):
        """BGMの読み込み（ファイルがない場合は自動生成）"""
            # BGMファイルがあれば読み込み
        if os.path.exists("bgm.mp3"):
            pygame.mixer.music.load("bgm.mp3")
            print("BGM: bgm.mp3を読み込みました")
        elif os.path.exists("bgm.wav"):
            pygame.mixer.music.load("bgm.wav")
            print("BGM: bgm.wav を読み込みました")
            
            
    def play_bgm(self):
        """BGM再生"""
        try:
            pygame.mixer.music.play(-1, 0.0)
            pygame.mixer.music.set_volume(0.3)
        except:
            pass
            
    def stop_bgm(self):
        """BGM停止"""
        try:
            pygame.mixer.music.stop()
        except:
            pass
            
    def draw_title(self):
        """タイトル画面"""
        self.screen.fill((20, 20, 50))
        
        font_big = get_font(48)
        font_medium = get_font(32)
        font_small = get_font(24)
        
        title = font_big.render("東方風弾幕ゲーム", True, (255, 255, 255))
        self.screen.blit(title, (120, 100))
        
        subtitle = font_medium.render("～ Danmaku Shooting ～", True, (200, 200, 255))
        self.screen.blit(subtitle, (150, 160))
        
        instruction1 = font_small.render("矢印キー: 移動", True, (255, 255, 255))
        self.screen.blit(instruction1, (250, 220))
        
        instruction2 = font_small.render("Z: ショット", True, (255, 255, 255))
        self.screen.blit(instruction2, (250, 250))
        
        instruction3 = font_small.render("Shift: 低速移動", True, (255, 255, 255))
        self.screen.blit(instruction3, (250, 280))
        
        start_text = font_medium.render("Zキーでスタート", True, (255, 255, 100))
        self.screen.blit(start_text, (200, 350))
        
        back_text = font_small.render("ESC: ホームに戻る", True, (200, 200, 200))
        self.screen.blit(back_text, (230, 420))
        
    def draw_game_over(self):
        """ゲームオーバー画面"""
        self.screen.fill((50, 20, 20))
        
        font_big = get_font(48)
        font_medium = get_font(32)
        
        game_over_text = font_big.render("GAME OVER", True, (255, 100, 100))
        self.screen.blit(game_over_text, (180, 150))
        
        score_text = font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (250, 220))
        
        restart_text = font_medium.render("R: リスタート", True, (255, 255, 100))
        self.screen.blit(restart_text, (200, 280))
        
        back_text = font_medium.render("ESC: ホームに戻る", True, (200, 200, 200))
        self.screen.blit(back_text, (170, 320))
        
    def draw_victory(self):
        """勝利画面"""
        self.screen.fill((20, 50, 20))
        
        font_big = get_font(48)
        font_medium = get_font(32)
        
        victory_text = font_big.render("VICTORY!", True, (100, 255, 100))
        self.screen.blit(victory_text, (200, 150))
        
        score_text = font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (250, 220))
        
        restart_text = font_medium.render("R: リスタート", True, (255, 255, 100))
        self.screen.blit(restart_text, (200, 280))
        
        back_text = font_medium.render("ESC: ホームに戻る", True, (200, 200, 200))
        self.screen.blit(back_text, (170, 320))
        
    def draw_game(self):
        """ゲーム画面"""
        self.screen.fill((10, 10, 30))
        
        # UI描画
        font = get_font(24)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f"Lives: {self.player.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 40))
        
        power_text = font.render(f"Power: {self.player.power}", True, (255, 255, 255))
        self.screen.blit(power_text, (10, 70))
        
        # ゲームオブジェクト描画
        self.player.draw(self.screen)
        
        # フェーズによって敵を描画
        if self.game_phase == "small_enemies":
            for small_enemy in self.small_enemies:
                small_enemy.draw(self.screen)
        elif self.game_phase == "boss_fight":
            self.enemy.draw(self.screen)
            # ボス位置マーカーを描画
            self.draw_boss_marker()
        
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
            
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
            
    def draw_boss_marker(self):
        """ボス位置マーカーを画面下部に描画"""
        # ボスのX座標に対応する位置
        marker_x = int(self.enemy.x)
        marker_y = 580  # 画面下部
        
        # メインマーカー（三角形）
        marker_points = [
            (marker_x, marker_y - 15),       # 上の頂点
            (marker_x - 10, marker_y),       # 左下
            (marker_x + 10, marker_y)        # 右下
        ]
        pygame.draw.polygon(self.screen, (255, 255, 100), marker_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), marker_points, 2)
        
        # 追加の装飾（小さな点滅する点）
        if pygame.time.get_ticks() % 600 < 300:  # 0.5秒間隔で点滅
            pygame.draw.circle(self.screen, (255, 100, 100), (marker_x, marker_y - 20), 3)
        
        # ボス名表示
        font = get_font(16)
        boss_label = font.render("BOSS", True, (255, 255, 100))
        text_rect = boss_label.get_rect(center=(marker_x, marker_y - 35))
        self.screen.blit(boss_label, text_rect)
            
    def reset_game(self):
        """ゲームリセット"""
        self.player = Player(400, 500)
        self.enemy = Enemy(400, 100)
        self.small_enemies = []
        self.small_enemy_spawn_timer = 0
        self.game_phase = "small_enemies"
        self.game_timer = 0
        self.player_bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.shooting = False
        self.shoot_timer = 0
        
    def check_collisions(self):
        """当たり判定"""
        # プレイヤー弾と敵の当たり判定
        for bullet in self.player_bullets[:]:
            hit = False
            
            # ボス戦の場合
            if self.game_phase == "boss_fight":
                if (bullet.x - self.enemy.x) ** 2 + (bullet.y - self.enemy.y) ** 2 < (bullet.radius + self.enemy.radius) ** 2:
                    self.player_bullets.remove(bullet)
                    self.enemy.hp -= 10
                    self.score += 100
                    hit = True
            
            # 雑魚敵との当たり判定
            elif self.game_phase == "small_enemies":
                for small_enemy in self.small_enemies[:]:
                    if (bullet.x - small_enemy.x) ** 2 + (bullet.y - small_enemy.y) ** 2 < (bullet.radius + small_enemy.radius) ** 2:
                        self.player_bullets.remove(bullet)
                        small_enemy.hp -= 10
                        self.score += 50
                        hit = True
                        
                        # 雑魚敵のHPが0になったら削除
                        if small_enemy.hp <= 0:
                            self.small_enemies.remove(small_enemy)
                            self.score += 200
                        break
            
            if hit:
                break
                
        # 敵弾とプレイヤーの当たり判定
        if self.player.invulnerable == 0:
            for bullet in self.enemy_bullets[:]:
                if (bullet.x - self.player.x) ** 2 + (bullet.y - self.player.y) ** 2 < (bullet.radius + self.player.radius) ** 2:
                    self.enemy_bullets.remove(bullet)
                    self.player.lives -= 1
                    self.player.invulnerable = 120
                    if self.player.lives <= 0:
                        self.state = "game_over"
                        self.stop_bgm()
                    break
                    
    def run(self):
        """メインゲームループ"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stop_bgm()
                        return "home"
                    elif event.key == pygame.K_z:
                        if self.state == "title":
                            self.state = "playing"
                            self.play_bgm()
                        elif self.state in ["game_over", "victory"]:
                            self.reset_game()
                            self.state = "playing"
                            self.play_bgm()
                    elif event.key == pygame.K_r:
                        if self.state in ["game_over", "victory"]:
                            self.reset_game()
                            self.state = "playing"
                            self.play_bgm()
                            
            if self.state == "playing":
                keys = pygame.key.get_pressed()
                
                # ゲームタイマー更新
                self.game_timer += 1
                
                # プレイヤー更新
                self.player.update(keys)
                
                # 射撃処理
                if keys[pygame.K_z]:
                    if not self.shooting:
                        self.shooting = True
                        self.shoot_timer = 0
                    if self.shoot_timer % 5 == 0:
                        self.player_bullets.append(PlayerBullet(self.player.x, self.player.y - 10))
                    self.shoot_timer += 1
                else:
                    self.shooting = False
                
                # フェーズ管理（20秒でボス戦に移行）
                if self.game_timer > 1200 and self.game_phase == "small_enemies":  # 60fps * 20秒 = 1200フレーム
                    self.game_phase = "boss_fight"
                    self.small_enemies = []  # 雑魚敵をクリア
                    print("ボス戦開始！")
                
                # 雑魚敵フェーズの処理
                if self.game_phase == "small_enemies":
                    # 雑魚敵スポーン
                    self.small_enemy_spawn_timer += 1
                    if self.small_enemy_spawn_timer % 120 == 0:  # 2秒に1回
                        spawn_x = random.randint(50, 750)
                        self.small_enemies.append(SmallEnemy(spawn_x, 50))
                    
                    # 雑魚敵更新
                    for small_enemy in self.small_enemies[:]:
                        small_enemy.update(self.player)
                        new_bullets = small_enemy.shoot()
                        self.enemy_bullets.extend(new_bullets)
                        
                        # 画面外に出た雑魚敵を削除
                        if small_enemy.y > 650:
                            self.small_enemies.remove(small_enemy)
                
                # ボス戦フェーズの処理
                elif self.game_phase == "boss_fight":
                    # 敵更新
                    self.enemy.update(self.player)
                    new_bullets = self.enemy.shoot()
                    self.enemy_bullets.extend(new_bullets)
                
                # 弾更新
                for bullet in self.player_bullets[:]:
                    bullet.update()
                    if bullet.y < 0:
                        self.player_bullets.remove(bullet)
                        
                for bullet in self.enemy_bullets[:]:
                    bullet.update()
                    if bullet.x < -20 or bullet.x > 820 or bullet.y < -20 or bullet.y > 620:
                        self.enemy_bullets.remove(bullet)
                        
                # 当たり判定
                self.check_collisions()
                
                # 勝利判定（ボス戦のみ）
                if self.game_phase == "boss_fight" and self.enemy.hp <= 0:
                    self.state = "victory"
                    self.stop_bgm()
                    
            # 描画
            if self.state == "title":
                self.draw_title()
            elif self.state == "playing":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()
            elif self.state == "victory":
                self.draw_victory()
                
            pygame.display.flip()
            self.clock.tick(60)
            
        return "quit"