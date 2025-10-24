#!/usr/bin/env python3
"""
图标处理脚本 - 为PNG图标添加macOS标准的圆角效果
"""

from PIL import Image, ImageDraw
import os

def create_rounded_icon(input_path, output_path, size=1024, corner_radius=None):
    """
    创建带圆角的图标
    
    Args:
        input_path: 输入图标路径
        output_path: 输出图标路径
        size: 图标尺寸 (默认1024x1024)
        corner_radius: 圆角半径 (如果为None，使用macOS标准比例)
    """
    # macOS标准圆角半径约为图标尺寸的26%
    if corner_radius is None:
        corner_radius = int(size * 0.26)
    
    # 打开原始图标
    with Image.open(input_path) as img:
        # 转换为RGBA模式
        img = img.convert("RGBA")
        
        # 调整图标尺寸
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # 创建圆角遮罩
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        
        # 绘制圆角矩形
        draw.rounded_rectangle(
            [(0, 0), (size, size)], 
            radius=corner_radius, 
            fill=255
        )
        
        # 创建输出图像
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # 保存图标
        output.save(output_path, 'PNG')
        print(f"圆角图标已保存到: {output_path}")

def create_icns_from_png(png_path, icns_path):
    """
    从PNG创建ICNS文件 (macOS图标格式)
    """
    # 创建临时目录存放不同尺寸的图标
    temp_dir = "/tmp/breathVOICE_icons"
    os.makedirs(temp_dir, exist_ok=True)
    
    # macOS需要的图标尺寸
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    with Image.open(png_path) as img:
        img = img.convert("RGBA")
        
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(f"{temp_dir}/icon_{size}x{size}.png", 'PNG')
    
    # 使用iconutil创建icns文件
    iconset_dir = f"{temp_dir}/breathVOICE.iconset"
    os.makedirs(iconset_dir, exist_ok=True)
    
    # 复制图标文件到iconset目录
    icon_mappings = {
        16: "icon_16x16.png",
        32: ["icon_16x16@2x.png", "icon_32x32.png"],
        64: "icon_32x32@2x.png",
        128: ["icon_128x128.png", "icon_64x64@2x.png"],
        256: ["icon_128x128@2x.png", "icon_256x256.png"],
        512: ["icon_256x256@2x.png", "icon_512x512.png"],
        1024: "icon_512x512@2x.png"
    }
    
    for size, names in icon_mappings.items():
        src_file = f"{temp_dir}/icon_{size}x{size}.png"
        if isinstance(names, list):
            for name in names:
                dst_file = f"{iconset_dir}/{name}"
                os.system(f"cp '{src_file}' '{dst_file}'")
        else:
            dst_file = f"{iconset_dir}/{names}"
            os.system(f"cp '{src_file}' '{dst_file}'")
    
    # 使用iconutil创建icns文件
    os.system(f"iconutil -c icns '{iconset_dir}' -o '{icns_path}'")
    
    # 清理临时文件
    os.system(f"rm -rf '{temp_dir}'")
    
    print(f"ICNS图标已创建: {icns_path}")

if __name__ == "__main__":
    # 输入和输出路径
    input_icon = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/icon/breathVOICE icon.png"
    rounded_icon = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/icon/breathVOICE_rounded.png"
    icns_icon = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/icon/breathVOICE.icns"
    
    # 创建圆角图标
    create_rounded_icon(input_icon, rounded_icon)
    
    # 创建ICNS图标
    create_icns_from_png(rounded_icon, icns_icon)
    
    print("图标处理完成！")