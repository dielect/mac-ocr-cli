from datetime import datetime

from rich.console import Console
from rich.text import Text

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
    使用 Rich 美化 OCR 结果输出，包含当前时间和文本颜色。

    Parameters:
    result (list): OCR 识别结果列表。

    Returns:
    None: 直接打印美化后的结果。
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"\n[bold magenta]OCR 识别结果 ([cyan]{current_time}[/cyan]):[/bold magenta]")
    for line in result:
        text = Text(line, style="cyan")
        console.print(text)
    console.print()  # 添加一个空行
