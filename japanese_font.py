import pygame as pg
import os

def get_font(size=30):
    # まずファイルパスから直接フォントを読み込む
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
        "C:/Windows/Fonts/msgothic.ttc",  # Windows
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = pg.font.Font(font_path, size)
                # 日本語のテスト
                test = font.render("あ", True, (255, 255, 255))
                if test.get_width() > 5:  # 正常に描画できている
                    return font
            except Exception as e:
                print(f"フォント読み込み失敗: {font_path}, エラー: {e}")
                continue
    
    # システムフォントを試す
    system_fonts = [
        "NotoSansCJK-Regular",
        "DejaVu Sans",
        "Liberation Sans",
        "Arial"
    ]
    
    for font_name in system_fonts:
        try:
            font = pg.font.SysFont(font_name, size)
            test = font.render("あ", True, (255, 255, 255))
            if test.get_width() > 5:
                print(f"システムフォント使用: {font_name}")
                return font
        except Exception as e:
            print(f"システムフォント失敗: {font_name}, エラー: {e}")
            continue
    
    # 最後の手段：デフォルトフォント
    print("デフォルトフォントを使用")
    return pg.font.Font(None, size)
