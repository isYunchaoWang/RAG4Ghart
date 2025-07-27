import os

# 设置路径
base_path = "../Dataset-ZXQ/"  # 根目录路径
txt_folder = os.path.join(base_path, "sample100")  # txt 文件夹路径

number = 0
number1 = 0
# 遍历 txt 文件夹中的所有文件
for root, dirs, files in os.walk(txt_folder):
    for filename in files:
        if filename.endswith(".txt"):  # 只处理 .txt 文件
            number1 +=1
            file_path = os.path.join(root, filename)  # 获取完整文件路径

            # 打开文件并读取内容
            with open(file_path, 'r', encoding='GBK') as file:
                content = file.read()
                content_length = len(content)
                if content_length < 200:
                    number += 1
                    # print(f" \"{file_path}\" ，的字符长度: {content_length}")
                    print(f"r\"{file_path}\",")

print(number)
print(number1)
