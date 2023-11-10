from .models import Product

from bs4 import BeautifulSoup
import requests
import math

import smtplib
import ssl
from email.message import EmailMessage

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

# Create your views here.
# in der View wird die Logik der Anwendung geschrieben
# so werden informationen aus dem Model abgefragt
# und an ein template weitergegeben

HEADERS = ({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 44.0.2403.157 Safari / 537.36',
    'Accept': 'text/html'
})
cookies = dict(language='de')

# Define email sender and receiver
email_sender = 'x'
email_password = 'abc' # via google mail
email_receiver = 'y'

def send_email(url, price, preferred_price):
    # Set the subject and body of the email
    subject = 'Check out my new video!'
    body = "Der Preis deines Artikels ist nun unter deinem Wunschpreis!" + \
           "\nDein Wunschpreis war " + str(preferred_price) + \
           "€.\nDer aktuelle Preis liegt bei " + str(price) + \
           "€. (" + url + ")"

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

def scrape_image(soup):
    # children = soup.find('div', {'id': "img-canvas"})
    new_product_image = "NA"
    children = soup.find_all("div", {"id": "imgTagWrapperId"})
    if children == None:
        new_product_image = "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
    else:
        # children = children.findChildren('img')
        # new_product_image = children[-1].find("div", {"img", "src"})
        pass

    # children = children.find('img', recursive=False)
    if children:
        if type(children) == list:
            new_product_image = children[-1].find("img")['src']
        else:
            new_product_image = children[-1].find("img")['src']
    else: # other method
        children = soup.find_all("div", {"class": "imgTagWrapper"})
        """  tag = soup.find(id="imgTagWrapperId")
        if tag is not None:
            children = tag.find("img", recursive=False)
            for child in children:
                if child.has_attr('src'):
                    new_product_image = child['src']"""
         # "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
    return new_product_image

def scrape_title(soup):
    # am besten schon vorher in Liste einfuegen, damit nicht immer in Webseite
    # gesucht werden muss und Ladezeiten somit nicht unnoetig lang sind
    try:
        new_product_title = soup.find("span", attrs={"id": 'productTitle'}).string.strip()
        # Erscheinungsdatum: id=productSubtitle
        # product_title = product_title.string.strip().replace(',', ''
        print("-" * 50)
    except AttributeError:
        new_product_title = "NA"
    return new_product_title

def scrape_price(soup):
    # alle Daten aus Datenbank in Tabelle einfügen, bis auf Preis.
    # Preis jedes Mal bei Aufruf aus Amazon-Webseite ausfiltern und vergleichen ob
    # sich Wert veraendert hat
    try:
        new_product_price_v0 = soup.find("span", attrs={'class': 'a-color-price'})
        new_product_price_v1 = soup.find("span", attrs={'class': 'a-offscreen'})
        new_product_price_v2 = soup.find("span", attrs={'class': 'aok-offscreen'})
        new_product_price_v3 = soup.find("span", attrs={'id': "price"})  # .text  # aktueller Preis
        #new_product_price_v4 = soup.find("span", attrs={'class': "a-price-whole"})  # aktueller Preis
        new_product_price_v5 = soup.find("span", attrs={'aria-hidden': "true"})  # aktueller Preis

        # checking multiple methods to
        new_product_price_list = [new_product_price_v0,
                                  new_product_price_v1,
                                  new_product_price_v2,
                                  new_product_price_v3,
                                  #new_product_price_v4,
                                  new_product_price_v5]
        price_is_found = [True if price_found is not None else False for price_found in new_product_price_list]
        if any(price_is_found): # if price is found / product is available
            # iterate over different methods that find the price tag for the product
            prices = []
            for i, price_found in enumerate(price_is_found):
                if price_found:
                    price = new_product_price_list[i].text.replace(" ", "")
                    prices.append(price)

            # set price for the first solution that's been found and skip every other solution
            new_product_price = ""
            for price in prices:
                if "nicht verfügbar" in price:
                    new_product_price = "Derzeit nicht verfügbar."
                if "€" in price:    # get first found solution
                    new_product_price = price
                    break
        else: # if there is no price found
            new_product_price = "NA"

        """
            new_product_price = soup.find("span", attrs={'class': "a-price-whole"})  # aktueller Preis
            price_tags = new_product_price.find_next_siblings()  # get next tags which includes n digits of price
            new_product_price = new_product_price.text
            for tag in price_tags:
                new_product_price += "" + tag.text"""

        new_product_price = new_product_price.replace(",", ".")
        new_product_price = new_product_price.split("€")[0]
        if new_product_price not in ["", "NA"]:
            new_product_price = float(new_product_price)  # converting string to number

    except AttributeError:
        new_product_price = "NA"
    except ValueError:
        print("Kein Preis für das Produkt gefunden.")
        new_product_price = "NA"
    return new_product_price

def scrape_product_data(soup):
    # scrape data for each property carefully to find data in most cases
    new_product_image = scrape_image(soup)
    new_product_title = scrape_title(soup)
    new_product_price = scrape_price(soup)

    return new_product_image, new_product_title, new_product_price

def website_exists(url):
    # response = urllib.request.urlopen(new_product_url) # unbedingt nochmal verändern
    # status_code = response.getcode()
    # print("Response:", response)
    # print("Code:", status_code)
    # if status_code == 200:
    return True

@csrf_exempt
def delete_prod(request):
    if request.method == 'POST':
        url = request.POST.get('current_product_link')
        Product.objects.filter(url=url).delete()
        return JsonResponse({'status': 'deleted'})

def show_webpage(request):
    return render(request, 'products/product_list.html')

@csrf_exempt
def product_list(request):
    status = ""
    for product in Product.objects.all().values():
        webpage = requests.get(product['url'], headers=HEADERS, cookies=cookies)
        soup = BeautifulSoup(webpage.text, "html.parser")

        image, title, price = scrape_product_data(soup)

        #if "NA" in [image, title, price]:
        #    status = 'data_not_found'
        if price != 'NA':
            if price <= float(product['preferred_price']):
                if not product['mail_has_been_sent']:
                    print("Send email.")
                    send_email(product['url'], price, product['preferred_price'])
                    # set parameter to True so that email is sent only once
                    Product.objects.filter(url=product['url']).update(mail_has_been_sent=True)
            Product.objects.filter(url=product['url']).update(title=price)

        if image != 'NA':
            Product.objects.filter(url=product['url']).update(image=image)
        if title != 'NA':
            Product.objects.filter(url=product['url']).update(title=title)

    products = Product.objects.all()
    return JsonResponse({'products': list(products.values()), 'status': status})

@csrf_exempt
def add_prod(request):
    if request.method == 'POST':
        url = request.POST.get('amzn_url')
        max_price = request.POST.get('desired_price')
        existing_urls = list(Product.objects.all().values_list('url', flat=True)) # flat=True for returning QuerySets instead of 1-tuples
        if url not in existing_urls:
            try:
                if (url != '') and (max_price != ''): # noch genauer werden da nur Zahlen erlaubt bei Preis
                    if "https://" not in url:
                        url = "https://" + url

                    if website_exists(url):
                        print('Web site exists', url)
                        webpage = requests.get(url, headers=HEADERS, cookies=cookies)
                        soup = BeautifulSoup(webpage.content, "html.parser")

                        image, title, price = scrape_product_data(soup)

                        max_price = max_price.replace(",", ".")
                        if price <= math.floor(float(max_price) * 100) / 100.0:
                            return JsonResponse({"url": url, "status": "already_under_limit_price"})
                        # create new product and add it to database
                        Product.objects.create(image=image,
                                               title=title,
                                               url=url,
                                               price=price,
                                               preferred_price=math.floor(float(max_price) * 100) / 100.0)
                        new_product_data = {
                            'image': image,
                            'title': title,
                            'url': url,
                            'price': price,
                            'preferred_price': math.floor(float(max_price) * 100) / 100.0,
                            'status': "new_product_created"
                        }
                        # update product list once after adding the product
                        return JsonResponse(new_product_data)
                    else:
                        # Textanzeige im Browser hinzufuegen
                        print('Web site does not exist')
                else:
                    return JsonResponse({'status': 'empty_input_field'})
            except ValueError:
                return JsonResponse({'status': 'only_numbers'})
            except Exception as e:
                print("HTTP_Error")
        else:
            return JsonResponse({'status': 'is_already_in_list'})
    return show_webpage(request)