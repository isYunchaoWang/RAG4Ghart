import os
import glob

csv_dir = os.path.join(os.path.dirname(__file__), '../Dataset-ZXQ/stream/csv')
csv_dir = os.path.abspath(csv_dir)

csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))

for file_path in csv_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) >= 3:
        # 交换第二行和第三行（索引1和2）
        lines[1], lines[2] = lines[2], lines[1]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        print(f'{file_path} 行数不足3行，未处理。')
