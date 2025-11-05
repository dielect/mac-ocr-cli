from datetime import datetime

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

console = Console()


def get_line_number(bbox, threshold=0.05):
    """
    Calculate the line number based on the bounding box.

    Parameters:
    bbox (list): Bounding box coordinates.
    threshold (float): Threshold to determine the line number.

    Returns:
    int: The calculated line number.
    """
    return int(bbox[1] // threshold)


def merge_text_by_line(ocr_results):
    """
    Merge OCR results by line number.

    Parameters:
    ocr_results (list): OCR results containing text, confidence, and bounding box.

    Returns:
    list: Merged text lines in reverse order.
    """
    lines = {}
    for result in ocr_results:
        text, confidence, bbox = result
        line_number = get_line_number(bbox)
        if line_number not in lines:
            lines[line_number] = []
        lines[line_number].append(text)

    merged_text = ["".join(lines[line_number]) for line_number in sorted(lines.keys())]
    return merged_text[::-1]


def beautify_ocr_result(result):
    """
    使用 Rich 美化 OCR 结果输出，采用优雅的表格和面板设计。

    Parameters:
    result (list): OCR 识别结果列表。

    Returns:
    None: 直接打印美化后的结果。
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 创建一个优雅的表格来展示 OCR 结果
    table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        border_style="bright_blue",
        box=ROUNDED,
        padding=(0, 1),
        title="[bold bright_magenta]✨ OCR 识别结果 ✨[/bold bright_magenta]",
        title_style="bold bright_magenta",
        caption=f"[dim italic]识别时间: {current_time}[/dim italic]",
        caption_style="dim cyan"
    )

    # 添加表格列
    table.add_column("行号", justify="center", style="bright_yellow", width=6)
    table.add_column("识别内容", justify="left", style="bright_white", no_wrap=False)

    # 添加每一行识别结果
    for idx, line in enumerate(result, start=1):
        # 为不同行使用渐变色效果
        line_number = f"[bold]{idx}[/bold]"
        text_content = Text(line, style="bright_cyan" if idx % 2 == 0 else "bright_green")
        table.add_row(line_number, text_content)

    # 使用面板包装表格，增加视觉层次
    panel = Panel(
        table,
        border_style="bold bright_magenta",
        padding=(1, 2),
        box=ROUNDED
    )

    console.print("\n")
    console.print(panel)
    console.print()
