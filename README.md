<h1 align="center">Mac-OCR-CLI</h1>
<p align="center">A powerful OCR tool for macOS - from terminal to API serve</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/mac-ocr-cli.svg" alt="PyPI version">
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/dielect/mac-ocr-cli/master/images/ocr-start.png" alt="OCR START" width="400" style="vertical-align: middle;"/>
</p>
MAC-OCR-CLI is a powerful command-line interface tool for Optical Character Recognition (OCR) on macOS.

It leverages `FastAPI`, `ocrmac`, and `Typer` to provide a seamless OCR experience directly from your terminal or through a local API server.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Easy-to-use CLI for starting an OCR server
- Restful API endpoint for OCR tasks.
- Built on FastAPI for high performance
- Utilizes ocrmac for accurate OCR on macOS
- Supports base64 encoded image input
- Intelligent text merging by line
- Beautiful console output using Rich library
- Customizable server settings (port, host, log level)

## Requirements

- Python 3.6+
- macOS (due to ocrmac dependency)
- pip (Python package installer)

## Installation

1. Ensure you have Python 3.6+ installed on your macOS system.
2. Install MAC-OCR-CLI using pip:

    ```sh
    pip install mac-ocr-cli
    ```

## Usage

### Starting the OCR CLI
<p>
  <img src="https://raw.githubusercontent.com/dielect/mac-ocr-cli/master/images/ocr-result.png" alt="OCR RESULT" width="400" style="vertical-align: middle;"/>
</p>

```sh
mac-ocr file <your_image_path>
```

### Starting the OCR Server

To start the OCR server with default settings:

```sh
mac-ocr server
```

You can customize the server settings using command-line options:

```sh
mac-ocr server --port 8080 --host 127.0.0.1 --log-level debug
```

Available options:

- `--port` or `-p`: Set the server port (default: 8000)
- `--host` or `-h`: Set the server host (default: 0.0.0.0)
- `--log-level` or `-l`: Set the log level (default: info)
- `--token` or `-t`: Set the token (default: None)

### Performing OCR

Once the server is running, you can perform OCR on an image using a POST request to the `/ocr` endpoint:

```sh
curl --location 'http://127.0.0.1:8080/ocr' \
--header 'Authorization: 123456' \
--header 'Content-Type: application/json' \
--data '{
    "image_path":"<your_image_path>"
}'
```
Replace `your_image_path` with your actual image path.
```sh
curl --location 'http://127.0.0.1:8080/ocr' \
--header 'Authorization: 123456' \
--header 'Content-Type: application/json' \
--data '{
    "image_base64":"<base64_encoded_image_data>"
}'
```

Replace `<base64_encoded_image_data>` with your actual base64-encoded image data.

The server will respond with the OCR results in JSON format:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "annotations": [
            [
                "INTP女",
                1.0,
                [
                    0.15561960485546392,
                    0.8036144575052732,
                    0.6772334149494265,
                    0.1295751962317041
                ]
            ],
            [
                "为什么罕见",
                1.0,
                [
                    0.08933718939980283,
                    0.6463855410040755,
                    0.8213256246225845,
                    0.11870066631271181
                ]
            ]
        ],
        "fullText": [
            "INTP女",
            "为什么罕见"
        ]
    }
}
```

Note: The OCR results are returned in reverse order (bottom to top) of the original image.

## Troubleshooting

### Common Issues

1. **Issue**: OCR server fails to start
   **Solution**: Ensure you have the necessary permissions and that the specified port is not in use.

2. **Issue**: OCR results are inaccurate
   **Solution**: Check that your image is clear and well-lit. Try preprocessing the image to improve contrast.

For more troubleshooting tips, please refer to our [FAQ](link_to_faq) or open an issue on GitHub.

## Contributing

Contributions to MAC-OCR-CLI are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

Please ensure your code adheres to the project's coding standards and include tests for new features.

## License

This project is licensed under the MIT License. See the [LICENSE]("./LICENSE"") file for details.
