# **Telecharm userbot**

[![Python 3.7](https://img.shields.io/badge/Python-3.7%20or%20newer-blue.svg)](https://www.python.org/downloads/release/python-370/)  
A powerful, fast and simple Telegram userbot written in Python 3 and based on Pyrogram 1.X. Currently in active WIP
state, so feel free to contribute.

## Starting up

**_Ensure you have installed the Python 3.7 or above before proceeding._**

### Preparations

1. Git clone this repo.

   ```cmd
   git clone https://github.com/WhiteMemory99/telecharm-userbot.git
   ```

2. Visit <https://my.telegram.org/apps> to get your own `api_id` and `api_hash`.
3. Rename `.env.dist` to `.env` and open it.
4. Edit `.env` file: fill in your `api_id`, `api_hash`.

### Poetry deployment

**_Make sure you have [poetry](https://python-poetry.org/docs/)._**

1. Install requirements.

   ```cmd
   poetry install
   ```

2. You can also install an optional **opencv-python** module to extend `.anime` functionality.

   ```cmd
   poetry install -E opencv
   ```

3. Run the userbot with poetry.

   ```cmd
   poetry run python app
   ```

### Plain python deployment

1. Install dependencies.

   ```cmd
   pip install -r requirements.txt
   ```

2. If you want to extend `.anime` functionality, install an optional `opencv-python` module.

   ```cmd
   pip install opencv-python
   ```

3. Run the userbot.

   ```cmd
   python3 -m app
   ```

## Usage

After logging in just send `.help` command to any chat to get the available commands or share Telecharm.

Thanks for using **Telecharm** :)
