# GenStega Telegram Bot
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.10-red?logo=telegram)](https://docs.aiogram.dev/)
[![Cryptography](https://img.shields.io/badge/Security-AES--128-gold?logo=shield)](https://cryptography.io/)
[![Vercel](https://img.shields.io/badge/Deployment-Vercel-black?logo=vercel)](https://vercel.com/)
![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-black?style=flat-square)

**StegoBot** is a Telegram bot designed for covert information transmission. The project combines cryptography methods and classic steganography, allowing you to turn ordinary images into protected containers for your secrets.

---

## 📋 Overview

- [🌟 Key Features](#-key-features)
- [🛠 Technical Architecture](#-technical-architecture)
- [🧩 Workflow Process](#-workflow-process)
- [🚫 Limitations and Usage Rules](#-limitations-and-usage-rules)
- [📄 License](#-license)

---

## 🌟 Key Features

* **🔐 Two-Level Protection**:
    * **Encryption**: Text is protected by the **Fernet (AES-128)** algorithm. The key is not stored in the code but is dynamically generated from your password using the cryptographically strong **PBKDF2HMAC** function with a unique salt and 100,000 iterations of SHA256 hashing.
    * **Steganography**: Encrypted data is embedded directly into the PNG file structure using the **LSB** (Least Significant Bit) method. This guarantees that visually the image remains identical to the original.

* **⏳ Self-Destructing Messages (TTL)**:
    * Each secret has a built-in timestamp.
    * By default, the message lifetime is **60 minutes**.
    * After this time expires, the bot will refuse decryption even if the password is entered correctly.

* **🎨 Built-in Container Generator**:
    * If you don't have a suitable image, the bot uses the `image_utils` module to create a unique abstract background.
    * Various generation styles are available: geometric circles, chaotic lines, or rectangular "cyberpunk".

* **📤 Upload Flexibility**:
    * Support for processing both user photos and documents.
    * Automatic conversion of incoming files to PNG format to preserve the integrity of hidden bits.

---

## 🛠 Technical Architecture

The project is built on a modular system that ensures code cleanliness and ease of maintenance:

* [core/crypto_utils.py](core/crypto_utils.py): Security core. Responsible for key generation, data encryption, and interaction with the `stepic` library for steganography.
* [core/handlers.py](core/handlers.py): Interaction logic. Uses Finite State Machine (FSM) to manage step-by-step encryption and decryption processes.
* [core/image_utils.py](core/image_utils.py): Graphics engine based on `Pillow`, creating 512x512 canvases with procedural art.
* [api/index.py](api/index.py): Adapter for working in Webhook mode via FastAPI, optimized for Serverless hosting.

---

## 🧩 Workflow Process

1.  **Launch**: The user selects `Encrypt` or `Decrypt` mode through an interactive menu.
2.  **Preparation**: When encrypting, the bot requests text, password, and the method of obtaining an image (generation or upload).
3.  **Processing**: The bot packs the text into JSON with an expiry date, encrypts it, and "dissolves" it in the image pixels.
4.  **Output**: The result is sent to the user as a PNG document.

---

## 🚫 Limitations and Usage Rules

* **File Format**: The bot works exclusively with the **PNG** format, as lossy formats (like JPEG) destroy hidden information during compression.
* **Data Transfer**: For successful decryption, files must be transferred within Telegram as **Documents**. When forwarded as "Photos", the messenger's compression algorithms will remove the embedded secret.
* **Copyright**: This code is a private development. Copying, distribution, or use of the source code for commercial and personal purposes without the owner's permission is prohibited.

---

## 📄 License

**Copyright © 2026. All Rights Reserved.**

This software and associated documentation files (the "Software") are the exclusive property of the copyright holder. 

**The following actions are strictly prohibited without prior written permission:**
- Copying, modifying, or distributing the Software
- Using the Software for commercial purposes
- Using the Software for personal purposes
- Reverse engineering, decompiling, or disassembling the Software
- Creating derivative works based on the Software

**Disclaimer:**
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For permissions or inquiries, please contact the copyright holder.

---

<div align="center">

**Made with ❤️ by Yan Shytyk**

</div>