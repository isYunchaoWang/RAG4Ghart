import os

def count_files_in_directory(directory):
    # 获取文件夹中的所有文件和文件夹
    items = os.listdir(directory)
    # 过滤出文件，排除文件夹
    files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
    return len(files)

# 示例：统计指定文件夹中的文件数量
directory = '/path/to/your/folder'  # 替换成你的文件夹路径
file_count = count_files_in_directory(directory)
print(f'文件夹中有 {file_count} 个文件')
