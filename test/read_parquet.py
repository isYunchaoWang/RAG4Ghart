import pyarrow.parquet as pq
import re
from tqdm import tqdm
from PIL import Image

base_path = "/home/public/ChartGen-200K"

mapping = {
    "3D Bar Chart": "bar",
    "3D Line Chart": "line",
    "3D Scatter Plot": "scatter",
    "Area Chart": "area",
    "Area Chart with Line": "line",
    "Bar Chart": "bar",
    "Barh Chart": "bar",
    "Box Plot": "box",
    "Boxen Plot": "box",
    "Bubble Chart": "bubble",
    "BubbleChart": "bubble",
    "Candlestick Chart": "bar",
    "Contour Plot": "heatmap",
    "Density Plot": "line",
    "Donut Chart": "pie",
    "Funnel Chart": "funnel",
    "Grouped Bar Chart": "bar",
    "Heatmap": "heatmap",
    "Histogram": "bar",
    "Horizontal Bar Chart": "bar",
    "Line Chart": "line",
    "Line Chart with Area": "line",
    "Line Chart with Markers": "line",
    "Line Chart with Points": "line",
    "Line Chart with Points and Area": "line",
    "Line Chart with Points and Dual Axes": "line",
    "Multi-Axes Chart": "multi_axes",
    "Multi-Line Chart": "line",
    "Pie Chart": "pie",
    "Point Plot": "scatter",
    "Radar Chart": "radar",
    "Radial Bar Chart": "bar",
    "Ring Chart": "ring",
    "Rose Chart": "rose",
    "RoseChart": "rose",
    "Scatter Plot": "scatter",
    "Scatter Plot with Regression Line": "scatter",
    "Stacked Area Chart": "stacked_area",
    "Stacked Bar Chart": "stacked_bar",
    "Stem Plot": "stem_plot",
    "Step Chart": "line",
    "Treemap": "treemap",
    "Treemap Chart": "treemap",
    "Tornado Chart": "bar",
    "Violin Plot": "violin",
}

source_path = f"{base_path}/data/test.parquet"
target_path = f"{base_path}/converted/test"
pf = pq.ParquetFile(source_path)

# 只读 code 列的这个 row group，避免一次性 materialize 大表
batch_tbl = pf.read_row_group(0, columns=["id", "code", "image_path", "summary", "csv"])
# 用 tqdm 包裹 zip
for id_, code, image_path, summary, csv in tqdm(
        zip(batch_tbl.column("id"),
            batch_tbl.column("code"),
            batch_tbl.column("image_path"),
            batch_tbl.column("summary"),
            batch_tbl.column("csv")),
        total=len(batch_tbl),
        desc="Processing"):

    match = re.search(r"ChartType\s*=\s*([^,]+)", code.as_py())
    if match:
        chart_type = mapping[match.group(1).strip()]
        # 写入csv
        with open(f"{target_path}/{chart_type}/csv/{id_}.csv", "w", encoding="utf-8") as f:
            f.write(csv.as_py())
        # 写入png
        image = Image.open(f"{base_path}/{image_path}")
        image.save(f"{target_path}/{chart_type}/png/{id_}.png")
        # 写入txt
        with open(f"{target_path}/{chart_type}/txt/{id_}.txt", "w", encoding="utf-8") as f:
            f.write(summary.as_py())
