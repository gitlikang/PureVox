import tkinter as tk
from pathlib import Path


class CustomFader(tk.Canvas):
    def __init__(self, master, image_path, width=600, height=110,
                 min_val=0, max_val=100, init_val=50,
                 thumb_target_height=30,
                 title_text="90s Channel",  # ← 顶部标题
                 label_text="Output",  # ← 底部标签
                 **kwargs):
        super().__init__(master, width=width, height=height,
                         bg="#2b2b2b", highlightthickness=0, **kwargs)

        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = init_val
        self.title_text = title_text
        self.label_text = label_text

        # ---- 加载并缩放推子图片 ----
        raw_img = tk.PhotoImage(file=image_path)
        self.scale_factor = max(1, round(raw_img.height() / thumb_target_height))
        self.thumb_image = raw_img.subsample(self.scale_factor, self.scale_factor)
        self._raw_img = raw_img

        self.img_width = self.thumb_image.width()
        self.img_height = self.thumb_image.height()

        # ---- 布局参数 ----
        self.track_y = height / 2 - 10
        self.track_height = 6
        self.track_margin = 60
        self.track_start = self.track_margin
        self.track_end = width - self.track_margin
        self.track_len = self.track_end - self.track_start

        # 绘制静态元素
        self.draw_track()
        self.draw_ticks()
        self.draw_labels()

        # 绘制推子帽
        self.create_thumb()

        # 绘制底部 "标签: xx" 动态文字
        self.create_output_text()

        # 事件绑定
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)

    def draw_track(self):
        self.create_rectangle(
            self.track_start, self.track_y - self.track_height / 2,
            self.track_end, self.track_y + self.track_height / 2,
            fill="#0a0a0a", outline="#111111", width=1
        )
        self.create_line(
            self.track_start, self.track_y,
            self.track_end, self.track_y,
            fill="#333333", width=1
        )

    def draw_ticks(self):
        num_ticks = 10
        for i in range(num_ticks + 1):
            x = self.track_start + (self.track_len * i / num_ticks)
            self.create_line(x, self.track_y + 15, x, self.track_y + 22,
                             fill="#888888", width=1)
            val_text = str(int(self.min_val + (self.max_val - self.min_val) * i / num_ticks))
            self.create_text(x, self.track_y + 35,
                             text=val_text, fill="#aaaaaa", font=("Arial", 9))

    def draw_labels(self):
        # 顶部标题（改为参数控制）
        self.create_text(self.width / 2, 14, text=self.title_text,
                         fill="#b0a0d0", font=("Arial", 13, "bold"))
        # 左右符号
        self.create_text(self.track_start - 25, self.track_y, text="-",
                         fill="#ffffff", font=("Arial", 14, "bold"))
        self.create_text(self.track_end + 25, self.track_y, text="+",
                         fill="#ffffff", font=("Arial", 14, "bold"))

    def create_thumb(self):
        x = self.track_start + (self.value - self.min_val) / (self.max_val - self.min_val) * self.track_len
        self.create_image(x, self.track_y, image=self.thumb_image,
                          anchor="center", tags="thumb")

    def create_output_text(self):
        """底部显示 '标签: xx'"""
        self.delete("output_text")
        self.create_text(
            self.width / 2, self.height - 12,
            text=f"{self.label_text}: {int(self.value)}",
            fill="#cccccc",
            font=("Arial", 11, "bold"),
            tags="output_text"
        )

    def set_value_from_x(self, x):
        min_x = self.track_start + self.img_width / 2
        max_x = self.track_end - self.img_width / 2
        if max_x < min_x:
            min_x = max_x = (self.track_start + self.track_end) / 2

        x = max(min_x, min(x, max_x))
        ratio = (x - min_x) / (max_x - min_x)
        self.value = self.min_val + ratio * (self.max_val - self.min_val)

        self.delete("thumb")
        self.create_thumb()
        self.create_output_text()

        if hasattr(self, 'command'):
            self.command(self.value)

    def on_click(self, event):
        self.set_value_from_x(event.x)

    def on_drag(self, event):
        self.set_value_from_x(event.x)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Custom Fader")
    root.configure(bg="#1e1e1e")

    import os
    import sys
    
    res = getattr(sys, "_MEIPASS", None) or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(res, "assets", "icons", "fader.png")
    # img_path = Path(__file__).parent / "image" / "滑块.png"

    fader_in = CustomFader(
        root,
        image_path=str(img_path),
        width=600, height=110,
        min_val=0, max_val=100, init_val=70,
        thumb_target_height=30,
        title_text="Input Channel",   # ← 顶部标题
        label_text="输入"             # ← 底部标签
    )
    fader_in.pack(padx=20, pady=(20, 5))

    fader_out = CustomFader(
        root,
        image_path=str(img_path),
        width=600, height=110,
        min_val=0, max_val=100, init_val=70,
        thumb_target_height=30,
        title_text="Output Channel",  # ← 顶部标题
        label_text="输出"             # ← 底部标签
    )
    fader_out.pack(padx=20, pady=(5, 20))

    root.mainloop()