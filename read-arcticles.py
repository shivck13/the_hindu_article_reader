import datetime
import pyttsx3
import win32api
import requests
from bs4 import BeautifulSoup as bs, Tag

def print_and_speak(text):
	tts = pyttsx3.init()
	tts.setProperty('voice', tts.getProperty('voices')[2].id)

	print(text)
	tts.say(text)

	tts.runAndWait()
	tts.stop()

def get_articles(date, opinions_only=False):
	print_and_speak(f"\nFetching articles from TheHindu newspaper published on {date.strftime('%d %B, %Y')}")

	url = f"https://www.thehindu.com/archive/print/{date.strftime('%Y/%m/%d')}/"
	html = requests.get(url).text
	soup = bs(html, "html.parser")


	articles = soup.select_one('h2#opinion').parent.parent.parent.select('div.section-container ul.archive-list li a') if opinions_only else soup.select("ul.archive-list li a")

	print_and_speak(f'\nFound {len(articles)} articles...')
	for ind, op in enumerate(articles):
		#print_and_speak(f'[{ind+1}] {op.text}')
		print(f'[{ind+1}] {op.text}')

	return articles

def get_choice(articles):
	print_and_speak('\nSelect the article to read')
	choice = int(input('[number] : '))

	if choice in range(1, len(articles)+1):
		return articles[choice-1]['href']
	else:
		print_and_speak('\nSorry! Invalid choice.')
		get_choice(articles)

def read_article(url):
	print_and_speak("\nFetching the article...")

	article_html = requests.get(url).text
	soup = bs(article_html, "html.parser")

	article = soup.select_one('div.article')
	intro = article.select_one('h2.intro')

	title_text = article.select_one('h1.title').text
	authors_text = ', '.join([auth.text.strip() for auth in article.select('div.author-container a.auth-nm.lnk')]).replace('\n', '')
	intro_text = intro.text if intro is not None else ''
	article_paras = article.select('div[id^=content-body-] p')

	print_and_speak(title_text)
	print_and_speak("Written by "+authors_text if len(authors_text.strip()) > 0 else '')
	print_and_speak(intro_text)

	for para in article_paras:
		print_and_speak(u'\n'.join(para.findAll(text=True)) if isinstance(para, Tag) else para)

def start_reader():
	print_and_speak('This program will read you articles from TheHindu.com')

	print_and_speak('\nGet opinions only? (otherwise full newspaper)')
	op_only = True if input("[y|n] : ").lower() == 'y' else False

	print_and_speak('\nEnter the date of publication')

	try:
		date = datetime.datetime.strptime(input("[DD/MM/YYYY] : "), "%d/%m/%Y").date()
	except:
		print_and_speak(f'\nERROR : Invalid Date!')
	else:
		read_article(get_choice(get_articles(date, op_only)))
	finally:
		print_and_speak('\nProgram complete! Press any key to exit...')
		x = input()

# ___________________________________________________

if __name__ == "__main__":
	start_reader()