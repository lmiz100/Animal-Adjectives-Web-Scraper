import asyncio
import os
from contextlib import asynccontextmanager

from downloader.animal_image_downloader import download_images_concurrently
from generator.html_generator import generate_html, OUTPUT_HTML
from logging_utils.logger import console
from scraper.wikipedia_parser import get_animal_entries
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FALLBACK_OUTPUT_HTML = os.path.join("output", "animals_fallback.html")


async def background_scrape_and_generate(log_prefix='Update'):
    console.log(f"[{log_prefix}] Scraping and generating report...")
    loop = asyncio.get_running_loop()

    animal_entries = await loop.run_in_executor(None, get_animal_entries)
    await loop.run_in_executor(None, download_images_concurrently, animal_entries)
    await loop.run_in_executor(None, generate_html, animal_entries)

    console.log(f"[{log_prefix}] Report ready at: {OUTPUT_HTML}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(background_scrape_and_generate(log_prefix='Startup'))  # schedule task, don't await
    yield
    print("[Shutdown] Server is shutting down...")

app = FastAPI(lifespan=lifespan)

# Serve the /tmp directory for image access
app.mount("/tmp", StaticFiles(directory="/tmp"), name="tmp")


# Serve the HTML file
@app.get("/", response_class=FileResponse)
async def serve_report():
    report_path = OUTPUT_HTML if os.path.exists(OUTPUT_HTML) else FALLBACK_OUTPUT_HTML
    console.log(f"Report path is: {report_path}")
    return FileResponse(report_path, media_type="text/html")

update_lock = asyncio.Lock()


@app.post("/update-report")
async def update_report(background_tasks: BackgroundTasks):
    if update_lock.locked():
        # If lock is acquired, means update is running, reject concurrent requests
        raise HTTPException(status_code=409, detail="Update already in progress")

    async def locked_scrape():
        async with update_lock:
            await background_scrape_and_generate()

    background_tasks.add_task(locked_scrape)
    return {"message": "Report update started in background"}


def print_first_items(animals, item_count=5):
    for animal in animals[:item_count]:
        print(animal)

if __name__ == "__main__":
    animals = get_animal_entries()
    print_first_items(animals)
    animals_with_images = download_images_concurrently(animals)
    print_first_items(animals_with_images)
    generate_html(animals)
