from .models import Product

from bs4 import BeautifulSoup
import requests
import json

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
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 44.0.2403.157 Safari / 537.36'
})
cookies = dict(language='de')

# Define email sender and receiver
email_sender = 'balkanbang19@gmail.com'
email_password = 'mpec qufu kdkd zagx'
email_receiver = 'balkanbang199@gmail.com'

def send_email(url, price, preferred_price):
    # Set the subject and body of the email
    subject = 'Check out my new video!'
    body = "Der Preis deines Artikels ist nun unter deinem Wunschpreis!: " + url + \
           "\nDein Wunschpreis war " + preferred_price + \
           "€ und der aktuelle Preis ist bei " + price + \
           "€." \

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


def scrape_product_data(soup):
    # children = soup.find('div', {'id': "img-canvas"})
    children = soup.find_all("div", {"id": "imgTagWrapperId"})
    if children == None:
        new_product_image = "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
    else:
        # children = children.findChildren('img')
        # new_product_image = children[-1].find("div", {"img", "src"})
        new_product_image = children[-1].find('img').get('src')
        for child in children:
            print("Child:", child)
        print("PI:", new_product_image)

    # am besten schon vorher in Liste einfuegen, damit nicht immer in Webseite
    # gesucht werden muss und Ladezeiten somit nicht unnoetig lang sind
    try:
        new_product_title = soup.find("span", attrs={"id": 'productTitle'}).string.strip()
        # Erscheinungsdatum: id=productSubtitle
        # product_title = product_title.string.strip().replace(',', ''
        print("-" * 50)
    except AttributeError:
        new_product_title = "NA"

    # alle Daten aus Datenbank in Tabelle einfügen, bis auf Preis.
    # Preis jedes Mal bei Aufruf aus Amazon-Webseite ausfiltern und vergleichen ob
    # sich Wert veraendert hat
    try:
        new_product_price = soup.find("span", attrs={'class': 'a-offscreen'}).string.strip()  # .string.strip().replace(',', '')

        # when above method doesnt work -> there are multiple ways to do that
        if new_product_price == "":
            new_product_price = soup.find("span", attrs={'class': "a-offscreen"})
            if new_product_price.text:
                new_product_price = soup.find("span", attrs={'class': "a-price-whole"})  # aktueller Preis
                price_tags = new_product_price.find_next_siblings() # get next tags which includes n digits of price
                new_product_price = new_product_price.text
                for tag in price_tags:
                    new_product_price += "" + tag.text

        new_product_price = new_product_price.replace(",", ".")
        new_product_price = new_product_price.replace("€", "")
        new_product_price = float(new_product_price)  # converting string to number

    except AttributeError:
        new_product_price = "NA"
    except ValueError:
        print("Kein Preis für das Produkt gefunden.")
        new_product_price = "NA"
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
    products = Product.objects.all()
    return JsonResponse({'products': list(products.values())})

@csrf_exempt
def add_prod(request):
    if request.method == 'POST':
        url = request.POST.get('amzn_url')
        max_price = request.POST.get('desired_price')
        existing_urls = list(Product.objects.all().values_list('url', flat=True)) # flat=True for returning QuerySets instead of 1-tuples
        if url not in existing_urls:
            if (url != '') and (max_price != ''): # noch genauer werden da nur Zahlen erlaubt bei Preis
                try:
                    if "https://" not in url:
                        url = "https://" + url

                    if website_exists(url):
                        print('Web site exists')
                        webpage = requests.get(url, headers=HEADERS, cookies=cookies)
                        soup = BeautifulSoup(webpage.content, "html.parser")

                        image, title, price = scrape_product_data(soup)

                        max_price = max_price.replace(",", ".")
                        print(price, max_price)
                        if price <= float(max_price):
                            return JsonResponse({"url": url, "status": "already_under_limit_price"})
                        # create new product and add it to database
                        Product.objects.create(image=image,
                                               title=title,
                                               url=url,
                                               price=price,
                                               preferred_price=float(max_price))
                        new_product_data = {
                            'image': image,
                            'title': title,
                            'url': url,
                            'price': price,
                            'preferred_price': float(max_price),
                            'status': "new_product_created"
                        }
                        return JsonResponse(new_product_data)
                    else:
                        # Textanzeige im Browser hinzufuegen
                        print('Web site does not exist')
                except ValueError:
                    return JsonResponse({'status': 'only_numbers'})
                except Exception as e:
                    print("HTTP_Error")
        else:
            return JsonResponse({'status': 'is_already_in_list'})
    return show_webpage(request)

@csrf_exempt
def show_product_list(request):
    attributes = []

    if request.POST.get('added_btn'):
        # if add button is clicked
        url = request.POST.get('amzn_url')
        max_price = request.POST.get('desired_price')

        webpage = requests.get(url, headers=HEADERS, cookies=cookies)
        soup = BeautifulSoup(webpage.content, "html.parser")

        # add product to list
        image, title, price = add_prod(url, max_price, soup) #"https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png", "blabla", '3'
        Product.objects.create(image=image, title=title, url=url, price=price, preferred_price=max_price)
        products = [product for product in Product.objects.all()]

        data = serializers.serialize('json', products)

        return JsonResponse({'products': data, 'action': 'create'}, safe=False)

    for product in Product.objects.all():
        webpage = requests.get(product.url, headers=HEADERS, cookies=cookies)
        soup = BeautifulSoup(webpage.content, "html.parser")
        image, title, price = scrape_product_data(soup)

        if price <= product.preferred_price:
            if not product['mail_has_been_sent']:
                product['mail_has_been_sent'] = True # to prevent that email is sent only once for each product
                # maybe remove product from list # but then also remove coloring of text and variable 'mail_has_been_sent'
                print("Send email.")
                #send_email()

        # update whole database # not a good way to go about things, but still okay for first solution
        Product.objects.filter(url=product.url).update(image=image, title=title, price=price)


    products = [product for product in Product.objects.all().values()]
    #return JsonResponse({"products": products})
    return render(request, 'products/product_list.html',
                  {'attributes': attributes,
                   'products': products
                   })
