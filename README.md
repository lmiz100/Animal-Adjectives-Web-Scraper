# 🐾 Animal Adjectives Scraper

A FastAPI-based web application that scrapes Wikipedia's [List of animal names](https://en.wikipedia.org/wiki/List_of_animal_names), extracts **collateral adjectives** and the **animals** that belong to them, 
downloads representative images for each animal, and generates a beautiful HTML report showcasing animals and their collateral adjectives.

---

## 🚀 Features
- **Web Scraping**: Automatically scrapes animal data from Wikipedia's "List of animal names"
- **Image Download**: Downloads animal images concurrently for better performance
- **HTML Report Generation**: Creates a styled HTML report with animal information
- **FastAPI Server**: Serves the report through a web interface
- **Background Processing**: Handles data scraping and report generation asynchronously
- **Auto-refresh**: Supports manual report updates via API endpoint


## Setup Instructions
### 1. Clone the Repository

```bash
git clone https://github.com/lmiz100/Animal-Adjectives-Web-Scraper.git
cd Animal-Adjectives-Web-Scraper
```

### 2. Create a Virtual Environment
#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
<br>

## ▶️ Running the Program

### Start the FastAPI Server
```bash
uvicorn main:app --port 8000
```

This will:
* Start the FastAPI server on http://localhost:8000
* Automatically begin scraping data from Wikipedia in the background.
* Download animal images to `/tmp/`.
* Generate a styled HTML report at `output/animals.html`.

### Available Endpoints
- **`GET /`** - View the generated animal report
- **`POST /update-report`** - Trigger a manual report update

### Usage
1. Start the server with the command above.
2. Open your browser and navigate to http://localhost:8000
3. The animal report will be displayed.
4. To refresh the data, send a POST request to `/update-report` or restart the server.

### Note
- The initial report generation happens automatically on startup.
- Images are served from `/tmp/` directory.
- If the main report isn't ready, a fallback version will be served.
- The HTML output groups animals by their collateral adjective in a card-style layout with images. You can filter results by the collateral adjective.
<br>

## 🧪 Running Tests
```bash
pytest -v
```
Unit tests are located in the `tests/` folder.
