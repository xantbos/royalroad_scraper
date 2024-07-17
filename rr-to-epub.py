import requests, pypub, json, validators
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

def array_to_epub(title, content):
	epub = pypub.epub.Epub(title)
	print("")
	for x, chapter in enumerate(content):
		print(f"Injecting Chapter {x+1} of {len(content)}", end='\r')
		thisChapter = pypub.create_chapter_from_html(bytes(content[chapter]["content"], 'utf-8'), content[chapter]["title"])
		epub.add_chapter(thisChapter)
	print("\nBuilding epub...", end=' ')
	filename = f'{sanitize_filename(title.lower())}.epub'
	epub.create(f'./{filename}')
	print(f'{filename} created.')


def get_rr_url_content(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text, "html.parser")
	res = soup.find("div", {"class": "chapter-content"})
	return str(res)

def royalroad_scrape(target_url):
	print("Scraping RR...")
	root_url = "https://www.royalroad.com"
	r = requests.get(target_url)
	soup = BeautifulSoup(r.text, "html.parser")
	fic_title = soup.find("div", {"class": "fic-header"}).h1.text
	print(f"Title found: {fic_title}")
	res = soup.find_all('script')
	scraped = {}
	for script in res:
		if hasattr(script, "text"):
			if script.text:
				if "window.chapters" in script.text:
					start_text = "window.chapters = ["
					end_text = "}];"
					s = script.text.find(start_text) + len(start_text)-1
					e = script.text.find(end_text, s) + 2
					cutlist = script.text[s:e]
					conv = json.loads(cutlist)
					chap = 1
					total_chapters = len(conv)
					internal_chapter = 1
					for chapter in conv:
						print(f"Scraping chapter {internal_chapter} of {total_chapters}...", end="\r")
						internal_chapter+=1
						gTitle = chapter["title"][8:] if "Chapter " in chapter["title"] else chapter["title"]
						if gTitle[:3].strip().isnumeric():
							chap = int(gTitle[:3].strip())
						else:
							chap = round(chap+.01,2)
						scraped[chapter["id"]] = {
							"logical": chap, 
							"title": gTitle,
							"content": get_rr_url_content(f'{root_url}{chapter["url"]}')
						}
	return fic_title, scraped


url = input("Enter the RoyalRoad series root url: ")
if validators.url(url):
	try:
		title, content_array = royalroad_scrape(url)
		array_to_epub(title, content_array)
		print("Success! Enjoy.")
	except Exception as e:
		print("Either you provided a bad url or the series has no content to scrape.")