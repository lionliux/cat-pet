# -*- coding: utf-8 -*-
"""
图片预处理工具 - 自动抠图并保存为透明PNG
运行一次即可，预处理后的图片会让桌宠启动更快
"""

from PIL import Image
import os
import shutil
from collections import deque


def remove_background_smart(img_path, output_path, bg_tolerance=40):
    """
    智能去背景：边缘采样 + 泛洪填充算法
    """
    img = Image.open(img_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    print(f"  图片尺寸: {width}x{height}")

    # 采样边缘点计算背景色
    sample_points = []
    step = max(1, min(width, height) // 30)
    for x in range(0, width, step):
        sample_points.append(pixels[x, 0])
        sample_points.append(pixels[x, height - 1])
    for y in range(0, height, step):
        sample_points.append(pixels[0, y])
        sample_points.append(pixels[width - 1, y])

    bg_r = sum(c[0] for c in sample_points) // len(sample_points)
    bg_g = sum(c[1] for c in sample_points) // len(sample_points)
    bg_b = sum(c[2] for c in sample_points) // len(sample_points)

    print(f"  检测背景色: R={bg_r}, G={bg_g}, B={bg_b}")

    # 泛洪填充标记背景
    visited = [[False] * height for _ in range(width)]
    bg_mask = [[False] * height for _ in range(width)]
    queue = deque()

    # 从边缘开始
    for x in range(0, width, max(1, step // 2)):
        for y in [0, height - 1]:
            if not visited[x][y]:
                r, g, b, a = pixels[x, y]
                diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                if diff < bg_tolerance:
                    visited[x][y] = True
                    bg_mask[x][y] = True
                    queue.append((x, y))

    for y in range(0, height, max(1, step // 2)):
        for x in [0, width - 1]:
            if not visited[x][y]:
                r, g, b, a = pixels[x, y]
                diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                if diff < bg_tolerance:
                    visited[x][y] = True
                    bg_mask[x][y] = True
                    queue.append((x, y))

    # 8方向泛洪
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    count = 0
    while queue:
        cx, cy = queue.popleft()
        count += 1
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[nx][ny]:
                visited[nx][ny] = True
                r, g, b, a = pixels[nx, ny]
                diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                if diff < bg_tolerance:
                    bg_mask[nx][ny] = True
                    queue.append((nx, ny))

    print(f"  标记背景像素: {count} 个")

    # 应用掩码
    new_data = []
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if bg_mask[x][y]:
                new_data.append((r, g, b, 0))
            else:
                new_data.append((r, g, b, a))

    img.putdata(new_data)

    # 智能裁剪透明边缘
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        print(f"  裁剪后尺寸: {img.size}")

    img.save(output_path, "PNG")
    return img


def process_all_images():
    """处理assets目录下的所有图片"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")

    if not os.path.exists(assets_dir):
        print("❌ 找不到 assets 文件夹！")
        return

    # 备份目录
    backup_dir = os.path.join(assets_dir, "original")
    os.makedirs(backup_dir, exist_ok=True)

    # 查找图片文件
    image_files = []
    for f in sorted(os.listdir(assets_dir)):
        fpath = os.path.join(assets_dir, f)
        if os.path.isfile(fpath) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(f)

    if not image_files:
        print("❌ assets 文件夹中没有找到图片！")
        return

    print("=" * 50)
    print("  🐱 猫咪图片预处理工具")
    print("=" * 50)
    print(f"\n📁 找到 {len(image_files)} 张图片\n")

    for i, filename in enumerate(image_files, 1):
        input_path = os.path.join(assets_dir, filename)
        output_path = os.path.join(assets_dir, f"cat{i}.png")
        backup_path = os.path.join(backup_dir, filename)

        print(f"[{i}/{len(image_files)}] 处理: {filename}")

        # 备份原图（如果还没备份过）
        if not os.path.exists(backup_path):
            shutil.copy2(input_path, backup_path)

        # 处理图片
        try:
            remove_background_smart(input_path, output_path)
            print(f"  ✅ 已保存: cat{i}.png\n")
        except Exception as e:
            print(f"  ❌ 处理失败: {e}\n")

    print("=" * 50)
    print("  ✅ 所有图片处理完成！")
    print("=" * 50)
    print(f"\n📝 原始图片备份: {backup_dir}")
    print("🚀 现在可以运行 cat_pet.py 启动桌宠了！")
    print("\n💡 提示：如果自动抠图效果不理想，")
    print("   可以用 remove.bg 等在线工具手动抠图，")
    print("   然后替换 assets 文件夹里的 cat1.png ~ cat3.png")


if __name__ == "__main__":
    process_all_images()
    input("\n按回车键退出...")
