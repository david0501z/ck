#!/bin/bash

# 定义要检查的目录，可根据实际情况修改
TARGET_DIR="./"

# 遍历目标目录中的所有文件
for file in $(find $TARGET_DIR -type f); do
    # 获取文件大小（单位：字节）
    file_size=$(du -b "$file" | cut -f1)
    # 检查文件大小是否超过 25MB（25MB = 25 * 1024 * 1024 字节）
    if [ $file_size -gt 26214400 ]; then
        echo "Skipping large file: $file"
        # 删除大文件
        rm "$file"
    fi
done

# 这里可以添加其他部署步骤，例如打包、上传等
echo "Deployment process continues..."
