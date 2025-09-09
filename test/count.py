import os
from collections import defaultdict

base_path = "/home/public/dataset-MegaCQA/train"

# 22 个类别
# categories = [
#     "area", "bar", "box", "bubble", "funnel", "heatmap", "line", "multi_axes",
#     "pie", "radar", "ring", "rose", "scatter", "stacked_area", "stacked_bar",
#     "stem_plot", "treemap", "violin"
# ]

categories = ("bar", "box", "bubble", "funnel", "line", "pie", "radar", "scatter", "treemap", "treemap")

# categories = [
#     "bar", "box", "scatter", "bubble", "pie" # 4000
# ]

# 5 个子目录
subdirs = ["csv", "png", "txt"]

# 统计结果：字典套字典
results = defaultdict(dict)
col_totals = defaultdict(int)
grand_total = 0

for cat in categories:
    row_total = 0
    for sub in subdirs:
        target = os.path.join(base_path, cat, sub)
        if os.path.isdir(target):
            # 递归统计
            count = sum(len(files) for _, _, files in os.walk(target))
            # 只统计第一层
            # count = len([f for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))])
        else:
            count = 0
        results[cat][sub] = count
        row_total += count
        col_totals[sub] += count
    results[cat]["TOTAL"] = row_total
    grand_total += row_total

# 打印表头
header = ["category"] + subdirs + ["TOTAL"]
print("{:<14}".format(header[0]), end="")
for h in header[1:]:
    print("{:>12}".format(h), end="")
print()

# 打印每一行
for cat in categories:
    print("{:<14}".format(cat), end="")
    for sub in subdirs:
        print("{:>12}".format(results[cat][sub]), end="")
    print("{:>12}".format(results[cat]["TOTAL"]))

# 打印总计
print("{:<14}".format("TOTAL"), end="")
for sub in subdirs:
    print("{:>12}".format(col_totals[sub]), end="")
print("{:>12}".format(grand_total))
