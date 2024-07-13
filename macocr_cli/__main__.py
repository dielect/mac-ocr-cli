import base64
import io
import os
from typing import Optional

import typer
import uvicorn
from PIL import Image
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from ocrmac import ocrmac
from pydantic import BaseModel
from rich.panel import Panel

from macocr_cli.utils import merge_text_by_line, beautify_ocr_result, console

app = FastAPI()
cli = typer.Typer()

VERSION = "0.2.9"
# 全局变量用于存储 token
AUTH_TOKEN = None


# 修改验证函数以使用全局 token
def verify_token(request: Request):
    if AUTH_TOKEN is None:
        # if no token is set, skip authentication
        return None
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header
    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": str(exc), "data": None},
    )


# 定义HTTPException处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


class ImageInput(BaseModel):
    image_path: str = None
    image_base64: str = None


@app.post("/ocr")
async def perform_ocr(image_input: ImageInput, token: str = Depends(verify_token)):
    if image_input.image_path is None and image_input.image_base64 is None:
        raise HTTPException(status_code=400, detail="Either 'image_path' or 'image_base64' must be provided")

    try:
        if image_input.image_path:
            if os.path.isfile(image_input.image_path):
                image = Image.open(image_input.image_path)
            else:
                return {
                    "code": 400,
                    "message": "File not found",
                    "data": None
                }
        else:
            image_bytes = base64.b64decode(image_input.image_base64)
            image = Image.open(io.BytesIO(image_bytes))

        annotations = ocrmac.OCR(image, language_preference=["zh-Hans"]).recognize()
        result = merge_text_by_line(annotations)
        beautify_ocr_result(result)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "annotations": annotations,
                "fullText": result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


def ocr_file(file_path: str):
    image = Image.open(file_path)
    annotations = ocrmac.OCR(image, language_preference=["zh-Hans"]).recognize()
    result = merge_text_by_line(annotations)
    beautify_ocr_result(result)


def version_callback(value: bool):
    if value:
        typer.echo(f"v{VERSION}")
        raise typer.Exit()


@cli.callback()
def main(version: Optional[bool] = typer.Option(
    None, "--version", "-v",
    help="show version information",
    callback=version_callback,
    is_eager=True,
    is_flag=True
)):
    """
        MAC-OCR-CLI: A powerful OCR command-line tool for macOS.

        This tool leverages macOS native OCR capabilities to provide
        high-accuracy text recognition from images. It offers both
        a simple command-line interface for quick OCR tasks and
        a server mode for integrating OCR capabilities into other applications.
     """
    pass


@cli.command()
def file(file_path: str = typer.Argument(..., help="Path to the image file for OCR processing")):
    """
    Perform OCR on a specified image file.

    This command takes an image file as input, performs Optical Character Recognition (OCR),
    and outputs the recognized text. It supports common image formats such as PNG, JPEG, and TIFF.

    The OCR process uses macOS native OCR capabilities for high accuracy.

    Example:
        mac-ocr file /path/to/your/image.png
    """
    ocr_file(file_path)


@cli.command()
def server(
        port: int = typer.Option(8000, "--port", "-p", help="Port on which the server will run"),
        host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host address to bind the server"),
        log_level: str = typer.Option("info", "--log-level", "-l",
                                      help="Logging level (debug, info, warning, error, critical)"),
        token: str = typer.Option(None, "--token", "-t", help="Authentication token for API access")
):
    """
        Start the OCR server with specified configuration.

        This command launches a FastAPI-based OCR server that can process images via HTTP requests.
        The server utilizes macOS native OCR capabilities for high-accuracy text recognition.

        You can customize the server's port, host, logging level, and set an authentication token.

        Examples:
            mac-ocr server
            mac-ocr server --port 9000 --host 127.0.0.1 --log-level debug --token your_secret_token
    """
    global AUTH_TOKEN
    AUTH_TOKEN = token

    start_message = f"Starting OCR server on:[bold cyan]{host}[/bold cyan]，port：[bold green]{port}[/bold green]"
    console.print(Panel(start_message, title=f"mac ocr v{VERSION}", expand=False, border_style="bold magenta"))

    uvicorn.run(app, host=host, port=port, log_level=log_level)


if __name__ == '__main__':
    cli()
