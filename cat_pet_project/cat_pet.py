# -*- coding: utf-8 -*-
"""
加菲猫桌面宠物 - Windows Desktop Pet
功能：透明窗口、无边框、始终置顶、可拖动、点击互动、对话气泡、右键菜单、滚轮缩放
"""

import tkinter as tk
from tkinter import Menu, simpledialog, messagebox
from PIL import Image, ImageTk
import random
import os
import sys

# ===================== 配置区域 =====================
# 图片素材列表
IMAGE_FILES = ["assets/cat1.png", "assets/cat2.png", "assets/cat3.png"]

# 对话气泡文本库
DIALOG_TEXTS = [
    "摸摸我~",
    "别打扰本喵睡觉",
    "再撸我就生气了！",
    "今天想吃罐头",
    "把我拖去窗边看看",
    "快给小鱼干！",
    "喵~你好呀",
    "不许摸我肚子！",
    "我是最胖的猫！",
    "困了...让我睡会儿",
    "你在看什么？",
    "给我开个罐罐呗",
    "我超凶的！",
    "摸摸头可以吗",
    "今天也是摆烂的一天",
    "铲屎官你好呀",
    "我的毛是不是很顺滑",
    "打个哈欠~",
    "我想吃小鱼干",
    "你工作累了吗",
]

# 默认配置
DEFAULT_SCALE = 0.3        # 初始缩放比例
DEFAULT_TOPMOST = True     # 默认始终置顶
ANIMATION_SPEED = 20       # 动画帧间隔（毫秒），越小越快
BUBBLE_DURATION = 3000     # 气泡显示时长（毫秒）
TRANSPARENT_COLOR = "#010101"  # 透明色

# 动画参数
JUMP_HEIGHT = 60           # 跳跃高度（像素）
SHAKE_DISTANCE = 6         # 抖动幅度（像素）
SHAKE_TIMES = 5            # 抖动次数
# ====================================================


def resource_path(relative_path):
    """获取资源文件的绝对路径（兼容打包后EXE运行）"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def remove_background(img, bg_tolerance=35):
    """
    自动去除图片背景
    使用泛洪填充算法从边缘开始标记背景区域
    """
    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # 采样边缘点计算背景色
    sample_points = []
    for x in range(0, width, max(1, width // 20)):
        sample_points.append(pixels[x, 0])
        sample_points.append(pixels[x, height - 1])
    for y in range(0, height, max(1, height // 20)):
        sample_points.append(pixels[0, y])
        sample_points.append(pixels[width - 1, y])

    bg_r = sum(c[0] for c in sample_points) // len(sample_points)
    bg_g = sum(c[1] for c in sample_points) // len(sample_points)
    bg_b = sum(c[2] for c in sample_points) // len(sample_points)

    # 泛洪填充标记背景
    visited = set()
    bg_pixels = set()
    queue = []

    # 从边缘点开始
    for x in range(0, width, max(1, width // 50)):
        for y in [0, height - 1]:
            if (x, y) not in visited:
                r, g, b, a = pixels[x, y]
                diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                if diff < bg_tolerance:
                    visited.add((x, y))
                    bg_pixels.add((x, y))
                    queue.append((x, y))

    for y in range(0, height, max(1, height // 50)):
        for x in [0, width - 1]:
            if (x, y) not in visited:
                r, g, b, a = pixels[x, y]
                diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                if diff < bg_tolerance:
                    visited.add((x, y))
                    bg_pixels.add((x, y))
                    queue.append((x, y))

    # BFS泛洪
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    while queue:
        cx, cy = queue.pop(0)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                visited.add((nx, ny))
                r, g, b, a = pixels[nx, ny]
                diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                if diff < bg_tolerance:
                    bg_pixels.add((nx, ny))
                    queue.append((nx, ny))

    # 应用透明
    new_data = []
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if (x, y) in bg_pixels:
                new_data.append((r, g, b, 0))
            else:
                new_data.append((r, g, b, a))

    img.putdata(new_data)

    # 智能裁剪
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    return img


class BubbleWindow:
    """对话气泡窗口"""

    def __init__(self, master, text, x, y):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.95)

        # 气泡框架
        frame = tk.Frame(self.window, bg="white", padx=12, pady=8)
        frame.pack()

        # 对话文本
        label = tk.Label(
            frame,
            text=text,
            bg="white",
            fg="#333333",
            font=("微软雅黑", 10),
            wraplength=160,
            justify="center"
        )
        label.pack()

        # 定位气泡（在角色上方）
        self.window.update_idletasks()
        bw = self.window.winfo_width()
        self.window.geometry(f"+{x - bw // 2}+{y}")

        # 定时关闭
        self.after_id = self.window.after(BUBBLE_DURATION, self.destroy)

    def destroy(self):
        """销毁气泡窗口"""
        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except:
            pass


class CatDesktopPet:
    """桌面宠物主类"""

    def __init__(self, root):
        self.root = root
        self.root.title("加菲猫桌宠")

        # 窗口设置
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", DEFAULT_TOPMOST)
        self.root.attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.root.config(bg=TRANSPARENT_COLOR)

        # 状态变量
        self.scale = DEFAULT_SCALE
        self.is_topmost = DEFAULT_TOPMOST
        self.is_animating = False
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.window_start_x = 0
        self.window_start_y = 0
        self.current_image_index = 0
        self.bubble = None
        self.click_pos = None

        # 加载图片
        self.original_images = []
        self._load_images()

        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )
        self.canvas.pack(fill="both", expand=True)

        # 显示初始图片
        self._update_display()

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)

        # 右键菜单
        self._create_context_menu()
        self.canvas.bind("<Button-3>", self._show_context_menu)

        # 窗口初始位置（屏幕底部居中）
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        x = (screen_w - win_w) // 2
        y = screen_h - win_h - 80
        self.root.geometry(f"+{x}+{y}")

    def _load_images(self):
        """加载并预处理所有图片"""
        for img_file in IMAGE_FILES:
            try:
                path = resource_path(img_file)
                img = Image.open(path)
                img = remove_background(img, bg_tolerance=40)
                self.original_images.append(img)
            except Exception as e:
                print(f"加载图片 {img_file} 失败: {e}")
                img = Image.new("RGBA", (100, 100), (255, 165, 0, 255))
                self.original_images.append(img)

    def _update_display(self):
        """更新显示的图片"""
        if not self.original_images:
            return

        img = self.original_images[self.current_image_index]
        w, h = img.size
        new_w = max(1, int(w * self.scale))
        new_h = max(1, int(h * self.scale))

        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.current_photo = ImageTk.PhotoImage(resized)

        self.canvas.config(width=new_w, height=new_h)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.current_photo)

    def _create_context_menu(self):
        """创建右键菜单"""
        self.menu = Menu(self.root, tearoff=0, bg="white", fg="black",
                         activebackground="#e0e0e0", activeforeground="black")
        self.menu.add_command(label="🐱 关于桌宠", command=self._show_about)
        self.menu.add_separator()
        self.menu.add_command(label="📏 调整大小...", command=self._ask_resize)
        self.menu.add_command(label="🔍 放大 (+)", command=lambda: self._zoom(0.1))
        self.menu.add_command(label="🔍 缩小 (-)", command=lambda: self._zoom(-0.1))
        self.menu.add_separator()
        self.menu.add_command(label="📌 取消置顶", command=self._toggle_topmost)
        self.menu.add_separator()
        self.menu.add_command(label="❌ 退出", command=self._quit)

    def _show_context_menu(self, event):
        """显示右键菜单"""
        self.menu.post(event.x_root, event.y_root)

    def _on_mouse_press(self, event):
        """鼠标按下"""
        self.is_dragging = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.window_start_x = self.root.winfo_x()
        self.window_start_y = self.root.winfo_y()
        self.click_pos = (event.x_root, event.y_root)

    def _on_mouse_drag(self, event):
        """鼠标拖动"""
        if self.is_dragging:
            dx = event.x_root - self.drag_start_x
            dy = event.y_root - self.drag_start_y
            new_x = self.window_start_x + dx
            new_y = self.window_start_y + dy
            self.root.geometry(f"+{new_x}+{new_y}")

    def _on_mouse_release(self, event):
        """鼠标释放"""
        was_dragging = self.is_dragging
        self.is_dragging = False

        # 判断是否为点击（移动距离很小）
        if self.click_pos and was_dragging:
            dx = abs(event.x_root - self.click_pos[0])
            dy = abs(event.y_root - self.click_pos[1])
            if dx < 5 and dy < 5:
                self._on_click()

        self.click_pos = None

    def _on_mouse_wheel(self, event):
        """鼠标滚轮缩放"""
        if event.delta > 0:
            self._zoom(0.05)
        else:
            self._zoom(-0.05)

    def _zoom(self, delta):
        """缩放图片，保持中心位置"""
        new_scale = self.scale + delta
        new_scale = max(0.1, min(2.0, new_scale))

        if new_scale != self.scale:
            # 保持中心位置
            old_w = self.canvas.winfo_width()
            old_h = self.canvas.winfo_height()
            cx = self.root.winfo_x() + old_w // 2
            cy = self.root.winfo_y() + old_h // 2

            self.scale = new_scale
            self._update_display()

            new_w = self.canvas.winfo_width()
            new_h = self.canvas.winfo_height()
            new_x = cx - new_w // 2
            new_y = cy - new_h // 2
            self.root.geometry(f"+{new_x}+{new_y}")

    def _ask_resize(self):
        """弹窗调整大小"""
        result = simpledialog.askfloat(
            "调整大小",
            "请输入缩放倍数（0.1 ~ 2.0）：",
            initialvalue=round(self.scale, 2),
            minvalue=0.1,
            maxvalue=2.0
        )
        if result is not None:
            self.scale = result
            self._update_display()

    def _toggle_topmost(self):
        """切换置顶状态"""
        self.is_topmost = not self.is_topmost
        self.root.attributes("-topmost", self.is_topmost)
        # 更新菜单文字（第6个菜单项，索引从0开始）
        if self.is_topmost:
            self.menu.entryconfigure(5, label="📌 取消置顶")
        else:
            self.menu.entryconfigure(5, label="📌 设为置顶")

    def _show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于加菲猫桌宠",
            "🐱 加菲猫桌面宠物 v1.0\n\n"
            "✨ 功能说明：\n"
            "• 左键按住拖动：移动猫咪位置\n"
            "• 左键点击：触发互动动画\n"
            "• 鼠标滚轮：调整猫咪大小\n"
            "• 右键点击：打开功能菜单\n\n"
            "Made with ❤️"
        )

    def _show_bubble(self):
        """显示对话气泡"""
        if self.bubble:
            self.bubble.destroy()

        text = random.choice(DIALOG_TEXTS)
        win_x = self.root.winfo_x()
        win_y = self.root.winfo_y()
        win_w = self.canvas.winfo_width()

        # 气泡在角色上方居中
        bubble_x = win_x + win_w // 2
        bubble_y = win_y - 55

        self.bubble = BubbleWindow(self.root, text, bubble_x, bubble_y)

    def _on_click(self):
        """点击触发互动"""
        if self.is_animating:
            return

        self.is_animating = True
        self._show_bubble()

        # 随机选择动画
        anim_type = random.choice(["jump", "squash", "shake"])

        if anim_type == "jump":
            self._animate_jump()
        elif anim_type == "squash":
            self._animate_squash()
        else:
            self._animate_shake()

    def _animate_jump(self):
        """跳跃动画（带缓动）"""
        original_y = self.root.winfo_y()
        frames = []

        # 上升（缓出）
        for i in range(8):
            t = i / 8
            offset = -JUMP_HEIGHT * (1 - (1 - t) ** 2)
            frames.append(int(original_y + offset))

        # 下降（缓入）
        for i in range(8):
            t = i / 8
            offset = -JUMP_HEIGHT * ((1 - t) ** 2)
            frames.append(int(original_y + offset))

        def play_frame(idx=0):
            if idx < len(frames):
                self.root.geometry(f"+{self.root.winfo_x()}+{frames[idx]}")
                self.root.after(ANIMATION_SPEED, lambda: play_frame(idx + 1))
            else:
                self._switch_image()
                self.is_animating = False

        play_frame()

    def _animate_squash(self):
        """压扁回弹动画"""
        original_scale = self.scale
        frames = []

        # 压扁
        for i in range(6):
            t = (i + 1) / 6
            sy = original_scale * (1 - 0.25 * t)
            sx = original_scale * (1 + 0.12 * t)
            frames.append((sx, sy))

        # 回弹
        for i in range(6):
            t = (i + 1) / 6
            sy = original_scale * (0.75 + 0.25 * t)
            sx = original_scale * (1.12 - 0.12 * t)
            frames.append((sx, sy))

        # 轻微过冲
        for i in range(3):
            t = (i + 1) / 3
            sy = original_scale * (1 + 0.06 * (1 - t))
            sx = original_scale * (1 - 0.03 * (1 - t))
            frames.append((sx, sy))

        def play_frame(idx=0):
            if idx < len(frames):
                sx, sy = frames[idx]
                self._set_scale_non_uniform(sx, sy)
                self.root.after(ANIMATION_SPEED, lambda: play_frame(idx + 1))
            else:
                self.scale = original_scale
                self._update_display()
                self._switch_image()
                self.is_animating = False

        play_frame()

    def _set_scale_non_uniform(self, scale_x, scale_y):
        """非均匀缩放（压扁效果，保持底部对齐）"""
        if not self.original_images:
            return

        img = self.original_images[self.current_image_index]
        w, h = img.size
        new_w = max(1, int(w * scale_x))
        new_h = max(1, int(h * scale_y))

        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.current_photo = ImageTk.PhotoImage(resized)

        # 保持底部位置不变
        old_h = self.canvas.winfo_height()
        old_y = self.root.winfo_y()
        new_y = old_y + old_h - new_h

        self.canvas.config(width=new_w, height=new_h)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.current_photo)
        self.root.geometry(f"+{self.root.winfo_x()}+{new_y}")

    def _animate_shake(self):
        """左右抖动动画"""
        original_x = self.root.winfo_x()
        frames = []

        for i in range(SHAKE_TIMES):
            frames.append(original_x - SHAKE_DISTANCE)
            frames.append(original_x + SHAKE_DISTANCE)

        frames.append(original_x)

        def play_frame(idx=0):
            if idx < len(frames):
                self.root.geometry(f"+{frames[idx]}+{self.root.winfo_y()}")
                self.root.after(ANIMATION_SPEED + 8, lambda: play_frame(idx + 1))
            else:
                self._switch_image()
                self.is_animating = False

        play_frame()

    def _switch_image(self):
        """随机切换猫咪形象"""
        if len(self.original_images) > 1:
            new_index = random.randint(0, len(self.original_images) - 1)
            if new_index != self.current_image_index:
                # 保持底部位置不变
                old_h = self.canvas.winfo_height()
                old_y = self.root.winfo_y()
                old_bottom = old_y + old_h

                self.current_image_index = new_index
                self._update_display()

                new_h = self.canvas.winfo_height()
                new_y = old_bottom - new_h
                self.root.geometry(f"+{self.root.winfo_x()}+{new_y}")

    def _quit(self):
        """退出程序"""
        if self.bubble:
            self.bubble.destroy()
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()

    # 检查资源目录
    assets_dir = resource_path("assets")
    if not os.path.exists(assets_dir):
        messagebox.showerror(
            "错误",
            f"找不到资源文件夹：{assets_dir}\n"
            f"请确保 assets 文件夹与程序在同一目录下。"
        )
        return

    app = CatDesktopPet(root)
    root.mainloop()


if __name__ == "__main__":
    main()
