# 🎬 My Movies Database CLI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-10%2B-green.svg)](https://www.python.org/)

A clean, modular command-line app to manage your personal movie collection with pluggable storage (JSON/CSV), OMDb lookup, fuzzy search, filters, stats, and static website generation. 🚀

---

## 📋 Table of Contents

* [Features](#-features)
* [🎯 Getting Started](#-getting-started)

  * [Prerequisites](#prerequisites)
  * [Environment](#environment)
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

* 💾 **Pluggable storage**: `StorageJson` and `StorageCsv` implement a common `IStorage` interface..
* 💾 **OMDb integration**: Add a movie by title; we fetch year/rating/poster automatically.
* 🎨 **Interactive CLI**: Colorful terminal UI using [Colorama](https://pypi.org/project/colorama/).
* 🔍 **Fuzzy Search**: Rapid fuzzy matching powered by [RapidFuzz](https://github.com/maxbachmann/RapidFuzz).
* 📊 **Statistics**: Compute average, median, best, and worst movie by ratings.
* 🎲 **Random Pick**: Let the app pick a movie for you at random.
* 📉 **Histogram**: Generate and save rating histograms via Matplotlib.
* 📉 **Website**: Generate a static HTML page (`static/index.html`) from your collection.
* 📆 **Sorting & Filtering**: Sort by rating or release year, filter by rating range and release period.
* 🚀 **Modular Design**: Clean separation between CLI logic and storage module for easy extensibility.

---

## 🎯 Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

* Python **3.10+**
* `pip` / `venv`
* Git (optional)

### Environment
* Create .env
* OMDB_API_KEY=your_omdb_key_here
* Get a key at omdbapi.com
 (free tier available).

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Get your OMDB_API_KEY from https://www.omdbapi.com/
```

### Installation

1. **Clone the repo**:

   ```bash
   ```

git clone [https://github.com/yourusername/my-movies-db.git](https://github.com/yourusername/my-movies-db.git)
cd my-movies-db



2. **Initialize storage**:
   ```bash
   JSON (storageJson): a single file keyed by title:
   example:
   {"Inception": {"year": "2010", "rating": 9.0, "poster": "https://..."} 
   ```
   ```bash
   CSV (StorageCsv): a headered CSV with:
   example:
   title,rating,year,poster
   Inception,9.0,2010,https://...
   ```

3. **🌐 Generate Website**:
    ```bash
   Menu option 9 builds static/index.html from your storage using static/index_template.html and static/style.css.
   ``` 
   
4. ```bash
   🧪 Tests
    pytest -q
   ```
   


4. **Run the application**:

   ```bash
   python -m src.movie_app
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
| `9`   | Generate website    |
| `9`   | Create and save a rating histogram     |
| `10`  | Sort movies by release year            |
| `11`  | Filter movies by rating & release year |

> **Tip:** Use blank inputs where indicated to skip optional filters.

-----
## ⚙️ Configuration & Notes

- Years: OMDb/CSV can include non-numeric years; sorting/filtering uses a safe parser.
- Ratings: If missing/unparseable, they are treated as None and skipped in stats.
- Color output: Uses colorama. You can call colorama.init(autoreset=True) in your entrypoint if desired.

------

## ⚙️ Demo GIF

- Comming Soon

------
## ⚙️ Screen shots

- Comming Soon
-----


## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature-name`)  
3. Commit your changes with clear messages (`git commit -m 'Add new feature'`)  
4. Push to the branch (`git push origin feature-name`)  
5. Open a Pull Request

Feel free to propose enhancements or report issues! ✨

---

## 📄 License

Distributed under the MIT License.
MIT © 2025 Lina Chioma Anaso

---

```
# Movie-Project--OOP-Web
# Movie-Project-OOP-Web-Extra-Features
