import os

# 设置路径
base_path = "../Dataset-ZXQ/sample100/line/"  # 你的根目录
txt_folder = os.path.join(base_path, "png")  # 原始 txt 文件夹路径
new_txt_folder = os.path.join(base_path, "txt")  # 新建的存储文件夹

# 如果新的文件夹不存在，则创建它
if not os.path.exists(new_txt_folder):
    os.makedirs(new_txt_folder)

# 遍历 png 文件夹中的所有 txt 文件
for filename in os.listdir(txt_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(txt_folder, filename)

        # 打开 txt 文件并读取内容
        with open(file_path, 'r', encoding='GBK') as file:
            content = file.read()


        # 查找 'Final Summary' 之后的内容
        start_index = content.find("Final Summary")
        if start_index != -1:
            filtered_content = content[1+start_index + len("Final Summary"):].lstrip()
        else:
            filtered_content = content


        # 创建新文件并保存提取的内容
        new_file_path = os.path.join(new_txt_folder, filename)
        with open(new_file_path, 'w', encoding='GBK') as new_file:
            new_file.write(filtered_content)

print("文件处理完成，提取的文本已保存到新文件夹中。")
