"""
日本語フォント設定ユーティリティ
matplotlibで日本語文字を正しく表示するための設定
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import warnings
from typing import Optional, List


class JapaneseFontConfig:
    """日本語フォント設定クラス"""

    def __init__(self):
        self.system = platform.system()
        self.available_fonts = self._get_available_fonts()
        self.japanese_font = self._find_japanese_font()

    def _get_available_fonts(self) -> List[str]:
        """利用可能なフォント一覧を取得"""
        try:
            fonts = [f.name for f in fm.fontManager.ttflist]
            return fonts
        except Exception as e:
            print(f"フォント一覧取得エラー: {e}")
            return []

    def _find_japanese_font(self) -> Optional[str]:
        """日本語対応フォントを検索"""
        japanese_fonts = [
            # macOS
            "Hiragino Sans",
            "Hiragino Kaku Gothic Pro",
            "Yu Gothic",
            "YuGothic",
            "Hiragino Mincho Pro",
            "Klee",
            "Osaka",
            # Windows
            "MS Gothic",
            "MS Mincho",
            "Meiryo",
            "Yu Gothic",
            "YuGothic",
            "MS PGothic",
            "MS PMincho",
            "MS UI Gothic",
            # Linux
            "Noto Sans CJK JP",
            "Noto Serif CJK JP",
            "Takao",
            "IPAexGothic",
            "IPAPGothic",
            "IPAMincho",
            "IPAPMincho",
            "VL Gothic",
            "VL PGothic",
        ]

        for font in japanese_fonts:
            if font in self.available_fonts:
                return font

        # フォールバック: システムデフォルト
        if self.system == "Darwin":  # macOS
            return "Hiragino Sans"
        elif self.system == "Windows":
            return "MS Gothic"
        else:  # Linux
            return "DejaVu Sans"

    def configure_matplotlib(self) -> bool:
        """matplotlibの日本語フォント設定"""
        try:
            if self.japanese_font:
                # フォント設定
                plt.rcParams["font.family"] = self.japanese_font
                plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化け防止

                # 警告を抑制
                warnings.filterwarnings(
                    "ignore", category=UserWarning, module="matplotlib"
                )

                print(f"✅ 日本語フォント設定完了: {self.japanese_font}")
                return True
            else:
                print(
                    "⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します。"
                )
                return False

        except Exception as e:
            print(f"❌ フォント設定エラー: {e}")
            return False

    def test_japanese_display(self) -> bool:
        """日本語表示テスト"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # テスト用の簡単なグラフを作成
            fig, ax = plt.subplots(figsize=(8, 6))
            x = np.linspace(0, 10, 100)
            y = np.sin(x)

            ax.plot(x, y, label="サイン波")
            ax.set_title("日本語表示テスト")
            ax.set_xlabel("時間")
            ax.set_ylabel("振幅")
            ax.legend()
            ax.grid(True)

            # 一時ファイルに保存してテスト
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                plt.savefig(tmp.name, dpi=100, bbox_inches="tight")
                plt.close()

                # ファイルが正常に作成されたかチェック
                if os.path.exists(tmp.name) and os.path.getsize(tmp.name) > 0:
                    os.unlink(tmp.name)  # 一時ファイルを削除
                    print("✅ 日本語表示テスト成功")
                    return True
                else:
                    print("❌ 日本語表示テスト失敗")
                    return False

        except Exception as e:
            print(f"❌ 日本語表示テストエラー: {e}")
            return False

    def get_font_info(self) -> dict:
        """フォント情報を取得"""
        return {
            "system": self.system,
            "japanese_font": self.japanese_font,
            "available_fonts_count": len(self.available_fonts),
            "font_family": plt.rcParams.get("font.family", "default"),
        }


# グローバル設定
_font_config = None


def get_font_config() -> JapaneseFontConfig:
    """フォント設定インスタンスを取得"""
    global _font_config
    if _font_config is None:
        _font_config = JapaneseFontConfig()
    return _font_config


def setup_japanese_font() -> bool:
    """日本語フォント設定を実行"""
    config = get_font_config()
    return config.configure_matplotlib()


def test_japanese_font() -> bool:
    """日本語フォントテストを実行"""
    config = get_font_config()
    return config.test_japanese_display()


def get_font_status() -> dict:
    """フォント設定状況を取得"""
    config = get_font_config()
    return config.get_font_info()


if __name__ == "__main__":
    # テスト実行
    print("🔍 日本語フォント設定テスト開始")

    config = get_font_config()
    print(f"システム: {config.system}")
    print(f"利用可能フォント数: {len(config.available_fonts)}")
    print(f"選択された日本語フォント: {config.japanese_font}")

    # フォント設定
    if config.configure_matplotlib():
        # テスト実行
        if test_japanese_font():
            print("✅ 日本語フォント設定完了")
        else:
            print("⚠️ 日本語フォント設定に問題があります")
    else:
        print("❌ 日本語フォント設定に失敗しました")
