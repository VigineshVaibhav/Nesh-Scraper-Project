from bs4 import BeautifulSoup
import urllib.request as ur
from IPython.display import IFrame
import nltk
import re
import heapq


query = 'PXD'
page_url={}
page_url['pxd'] = 'https://www.fool.com/quote/nyse/pioneer-natural-resources/pxd'
page_url['oxy'] = 'https://www.fool.com/quote/nyse/occidental-petroleum/oxy'
page_url['eog'] = 'https://www.fool.com/quote/nyse/eog-resources/eog'
page_url['apc'] = 'https://www.fool.com/quote/nyse/anadarko-petroleum/apc'
page_url['apa'] = 'https://www.fool.com/quote/nyse/apache/apa'
page_url['cop'] = 'https://www.fool.com/quote/nyse/conocophillips/cop'
iframe_link = 'https://www.motleyfoolp.idmanagedsolutions.com/stocks/chart?symbol='+query
# news_link=[]
# earnings_call_link = ""

def get_company(company=None):
	if company is None:
		company = 'PXD'
	global query
	query = company

def about_company():
	soup = get_soup()
	name = soup.find('span',attrs={'class':'company-name'}).text.strip()
	ticker = soup.find('span',attrs={'class':'company-ticker'}).text.strip()
	about = soup.find('div',attrs={'class':'free-desc free-only'}).text.strip()
	print("Company Name:",name)
	print("Company Ticker:",ticker)
	print("About The Company:",about)


def get_soup(link=None):
	if link is None:
		link=page_url[query.lower()]
	response = ur.urlopen(link)
	soup = BeautifulSoup(response, 'html.parser')
	return soup


def get_company_data():
	# about_company()
	soup = get_soup()
	price = soup.find('h2', attrs={'class': 'current-price'})

	price_change_pos = soup.find('h2',attrs={'class':'price-change-amount price-pos'})
	price_change_neg = soup.find('h2',attrs={'class':'price-change-amount price-neg'})
	price_percent_change_pos = soup.find('h2',attrs={'class':'price-change-percent price-pos'})
	price_percent_change_neg = soup.find('h2',attrs={'class':'price-change-percent price-neg'})

	if price_change_pos is None:
		price_change = price_change_neg
		price_percent_change = price_percent_change_neg
	else:
		price_change = price_change_pos
		price_percent_change = price_percent_change_pos
	# print(soup)
	current_price = price.text.strip()
	current_price_change = price_change.text.strip()
	current_price_percent_change = price_percent_change.text.strip()
	trend_flag = soup.find('h2', attrs={'class': 'price-change-arrow price-pos'})
	if(trend_flag):
	    print("The stock price is currently at ",current_price,", demonstrating an increase of about",
	    	current_price_change, current_price_percent_change)
	else:
	    print("The stock price is currently at ",current_price,", demonstrating a decrease of about ",
	    	current_price_change, current_price_percent_change)

	print("\nOther Data Points:\n")

	data_points = soup.find('table',attrs={'class', 'key-data-points data-table key-data-table1'}).text.strip()
	data_points = data_points[data_points.find("Prev Close:"):]
	print(data_points)

def get_stock_trend():
	return IFrame(iframe_link, width=500, height=250)

def get_news_articles(count=5):
	# global earnings_call_link
	soup = get_soup()
	articles = soup.find('div',attrs={'id':'article-list'})
	news_list = articles.find_all('a',href=True)
	print("-----")
	count_copy = count
	for news in news_list:
		count_copy = count_copy - 1
		title = news.text.strip()
		# if "Earnings Conference Call" in title and "Q4" in title:
		#     earnings_call_link = news['href']
		# else:
		# 	global news_link
		# 	news_link.append(news['href'])
		print("Article Number ", (count-count_copy),"\n\n")
		summarize_news(news['href'])
		print("Link:",news['href'])
		print("-----")
		if(count_copy<=0):
			break

def get_earnings_call_link():
	soup = get_soup()
	articles = soup.find('div',attrs={'id':'article-list'})
	news_list = articles.find_all('a',href=True)
	for news in news_list:
		title = news.text.strip()
		if "Earnings Conference Call" in title and "Q4" in title:
			return news['href']
			

def earnings_call_report():
	link = get_earnings_call_link()
	earnings_soup = get_soup(link)
	article = earnings_soup.find('span',attrs={'class':'article-content'})
	# Find Date of Earnings Call
	date = article.find('span',attrs={'id':'date'}).text.strip()
	participants = article.find_all('h2')
	print("Date of earnings call:",date)
	# print(participants)
	text = article.text.strip()
	# Find call duration
	start = text.find("Duration:")
	end = text.find("Call participants")
	print("\n",text[start:end])
	# Find Call Participants
	start = text.find("Call participants")
	end = text.find("More")
	print(text[start:end])

def summarize_news(link=None):

	if link is None:
		link = page_url[query.lower()]

	news_headline = ""
	news_subheadline = ""
	summary = ""
	summary_sentences = ""
	news_text = ""
	formatted_text=""

	news_soup = get_soup(link)
	news_article = news_soup.find('span',attrs={'class':'article-content'})
	news_headline = news_soup.find('h1').text.strip()
	news_subheadline = news_soup.find('h2').text.strip()
	news_text = news_article.text.strip()
	formatted_text = re.sub('[^a-zA-Z]', ' ', news_text )  
	formatted_text = re.sub(r'\s+', ' ', formatted_text)

	stopwords = nltk.corpus.stopwords.words('english')

	word_frequencies = {}  
	for word in nltk.word_tokenize(formatted_text):  
	    if word not in stopwords:
	        if word not in word_frequencies.keys():
	            word_frequencies[word] = 1
	        else:
	            word_frequencies[word] += 1

	maximum_frequency = max(word_frequencies.values())

	for word in word_frequencies.keys():  
	    word_frequencies[word] = (word_frequencies[word]/maximum_frequency) # Compute weighted word frequency

	sentence_list = nltk.sent_tokenize(news_text)
	sentence_scores = {}  
	for sent in sentence_list:  
	    for word in nltk.word_tokenize(sent.lower()):
	        if word in word_frequencies.keys():
	            if len(sent.split(' ')) < 25: # Remove sentences longer than 25 words to keep summary brief
	                if sent in sentence_scores.keys():
	                    sentence_scores[sent] += word_frequencies[word]
	                else:
	                    sentence_scores[sent] = word_frequencies[word]

	summary_sentences = heapq.nlargest(8, sentence_scores, key=sentence_scores.get)

	summary = ' '.join(summary_sentences)
	print("Article Title:",news_headline)
	print("Article Sub-Title:",news_subheadline)
	print("\n\t\t\t\t----------ARTICLE SUMMARY----------\n\n")
	print(summary)


