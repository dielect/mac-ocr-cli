import base64
import io
from datetime import datetime

import typer
import uvicorn
from PIL import Image
from fastapi import FastAPI, HTTPException
from ocrmac import ocrmac
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

app = FastAPI()
cli = typer.Typer()
console = Console()


class ImageBase64(BaseModel):
    image: str


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


@app.post("/ocr")
async def perform_ocr(image_data: ImageBase64):
    """
    Perform OCR on the provided base64 encoded image.

    Parameters:
    image_data (ImageBase64): Base64 encoded image data.

    Returns:
    dict: OCR recognition results.

    Raises:
    HTTPException: If there is an error during the OCR process.
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.image)
        image = Image.open(io.BytesIO(image_bytes))

        # Perform OCR using ocrmac
        annotations = ocrmac.OCR(image, language_preference=["zh-Hans"]).recognize()
        result = merge_text_by_line(annotations)
        beautify_ocr_result(result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cli.command()
def start_server(
        port: int = typer.Option(8000, "--port", "-p", help="服务器运行的端口"),
        host: str = typer.Option("0.0.0.0", "--host", "-h", help="服务器运行的主机地址"),
        log_level: str = typer.Option("info", "--log-level", "-l", help="日志级别")
):
    """
    启动具有指定配置的 OCR 服务器。
    """
    start_message = f"正在启动 OCR 服务器，地址：[bold cyan]{host}[/bold cyan]，端口：[bold green]{port}[/bold green]"
    console.print(Panel(start_message, title="mac ocr", expand=False, border_style="bold magenta"))

    uvicorn.run(app, host=host, port=port, log_level=log_level)


if __name__ == '__main__':
    cli()
