# SeaQuiller 🐦

Ahoy, data explorers! Welcome aboard SeaQuiller, your trusty tool for navigating the vast oceans of databases! 🌊✨ 

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Requirements](#requirements)
- [Let's Set Sail!](#lets-set-sail)

## Features
- 🐠 Effortlessly query your databases.
- 🚀 User-friendly interface with Streamlit.
- 🌈 Supports various database types.
- 🔐 Secure your connections with ease.

## Getting Started

Ready to set sail? Follow these simple steps to launch your SeaQuiller adventure!

### 1. Start the FastAPI Server
Launch your server using the following command:
```bash
uvicorn main:app
```

### 2. Initialize the Streamlit UI
Fire up the user interface with this command:
```bash
streamlit run app.py
```

## Configuration

Before you dive in, you’ll need to configure your `config.json` file. Use the template below to ensure smooth sailing:

```json
{
    "database": null,
    "db_type": null,
    "model": null,
    "user": null,
    "password": null,
    "host": null,
    "port": null,
    "api_key": null
}
```

Make sure to fill in your details to keep your ship on course! 🛠️

## Requirements

Check out the `requirements.txt` file in the folder to ensure you have all the necessary packages installed. This keeps everything shipshape and ready for action! ⚓️

## Let's Set Sail! ⛵

Once everything is set up, you're ready to explore your database like never before! Whether you're querying, updating, or just admiring the data, SeaQuiller is here to help you navigate the waters of your data seas! 

### Happy Quilling! 🐦💙

Dive in, have fun, and may your data adventures be filled with treasure!
