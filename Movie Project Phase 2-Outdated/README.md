# 🎬 My Movies Database CLI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-green.svg)](https://www.python.org/)

> A sleek, interactive command-line application to manage your personal movie collection with persistent JSON storage, fuzzy search, filtering, and advanced statistics. 🚀

---

## 📋 Table of Contents

* [Features](#-features)
* [🎯 Getting Started](#-getting-started)

  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [🛠️ Usage](#️-usage)

  * [Menu Options](#menu-options)
* [⚙️ Configuration](#️-configuration)
* [🔄 Demo GIF](#-demo-gif)
* [📈 Screenshots](#-screenshots)
* [🧑‍💻 Contributing](#-contributing)
* [📄 License](#-license)

---

## ✨ Features

* 💾 **Persistent JSON Storage**: All movie data is saved in `data.json` for durability.
* 🎨 **Interactive CLI**: Colorful terminal UI using [Colorama](https://pypi.org/project/colorama/).
* 🔍 **Fuzzy Search**: Rapid fuzzy matching powered by [RapidFuzz](https://github.com/maxbachmann/RapidFuzz).
* 📊 **Statistics**: Compute average, median, best, and worst ratings.
* 🎲 **Random Pick**: Let the app pick a movie for you at random.
* 📉 **Histogram**: Generate and save rating histograms with Matplotlib.
* 📆 **Sorting & Filtering**: Sort by rating or release year, filter by rating range and release period.
* 🚀 **Modular Design**: Clean separation between CLI logic and storage module for easy extensibility.

---

## 🎯 Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

* Python 3.7 or higher
* Git (optional)

Install dependencies:

```bash
pip install -r requirements.txt
```

### Installation

1. **Clone the repo**:

   ```bash
   ```

git clone [https://github.com/yourusername/my-movies-db.git](https://github.com/yourusername/my-movies-db.git)
cd my-movies-db

````

2. **Initialize storage**:
   ```bash
echo "{}" > data.json
````

3. **Run the application**:

   ```bash
   ```

python movies.py

```

---

## 🛠️ Usage

Upon running, you'll see a colorful menu. Simply enter the number corresponding to the action you'd like to perform.

### Menu Options

| Option | Action                                |
|------:|:---------------------------------------|
| `0`   | Exit the application                   |
| `1`   | List all movies                        |
| `2`   | Add a new movie (with validation)      |
| `3`   | Delete a movie by title                |
| `4`   | Update an existing movie's rating      |
| `5`   | View statistics (avg, median, best, worst) |
| `6`   | Pick a random movie                    |
| `7`   | Fuzzy search for movies                |
| `8`   | Sort and display movies by rating      |
| `9`   | Create and save a rating histogram     |
| `10`  | Sort movies by release year            |
| `11`  | Filter movies by rating & release year |

> **Tip:** Use blank inputs where indicated to skip optional filters.

---

## ⚙️ Configuration

- **`DATA_FILE`** in `movie_storage.py`: Change the JSON filename if desired.
- **Histogram styling**: Adjust bins/size in `create_rating_histogram()`.

---


## 🧑‍💻 Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature-name`)  
3. Commit your changes (`git commit -m 'Add new feature'`)  
4. Push to the branch (`git push origin feature-name`)  
5. Open a Pull Request

Feel free to propose enhancements or report issues! ✨

---

## 📄 License

Distributed under the MIT License.

---

Made with ❤️ by **Lina Chioma Anaso**

```
# Movie-Project-Phase-2
