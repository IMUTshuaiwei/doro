"""可执行的py文件，用于将不透明的doroGIF转换成透明GIF"""

import os
from typing import List

import cv2
import numpy as np
from PIL import Image, ImageSequence, ImageFile

# 输入和输出目录
input_folder = "input"
output_folder = "output_gifs"
os.makedirs(output_folder, exist_ok=True)

# 遍历输入目录所有 GIF 文件
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(".gif"):
        continue

    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, filename)

    # 用 PIL 读取原始 GIF
    pil_gif: ImageFile.ImageFile = Image.open(input_path)
    frames: List[Image.Image] = []
    duration: int = pil_gif.info.get("duration", 100)

    for frame in ImageSequence.Iterator(pil_gif):
        rgba = frame.convert("RGBA")
        np_frame = np.array(rgba)
        h, w = np_frame.shape[:2]

        # 分离通道
        rgb = np_frame[:, :, :3].copy()
        alpha = np.ones((h, w), dtype=np.uint8) * 255

        # 创建 flood fill 掩码
        mask = np.zeros((h + 2, w + 2), np.uint8)
        flood = rgb.copy()

        # floodFill: 去除四角连接的白色背景
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        for x, y in corners:
            cv2.floodFill(
                image=flood,
                mask=mask,
                seedPoint=(x, y),
                newVal=(0, 0, 0),
                loDiff=(15, 15, 15),
                upDiff=(15, 15, 15),
                flags=cv2.FLOODFILL_MASK_ONLY,
            )

        bg_mask = mask[1:-1, 1:-1]
        alpha[bg_mask == 1] = 0

        # 组装 RGBA 图像
        final_rgba = np.dstack((rgb, alpha))
        pil_frame = Image.fromarray(final_rgba, mode="RGBA")

        # 每帧贴到全透明底图上，防止残影
        canvas: Image.Image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(pil_frame, (0, 0), pil_frame)
        frames.append(canvas)

    # 保存为新 GIF, 防止残影
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,  # 每帧显示完后清除
        transparency=0,
    )  # 指定透明色索引

    print(f"已处理: {filename}")
