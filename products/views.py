from .models import Product
from .forms import ProductForm

from bs4 import BeautifulSoup
import requests
import json
import urllib.request

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django import http

# Create your views here.
# in der View wird die Logik der Anwendung geschrieben
# so werden informationen aus dem Model abgefragt
# und an ein template weitergegeben

HEADERS = ({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 44.0.2403.157 Safari / 537.36'
})
cookies = dict(language='de')

def product_list(request):
    products = Product.objects.filter(author=User.objects.all()[0])
    return render(request, 'products/product_list.html', {'products': products})

def get_product_attributes(request):
    # alle Attribute die fuer die Tabellenspalten benoetigt wird
    attributes = Product.print_instance_attributes()
    return render(request, 'products/product_list.html', {'attributes': attributes})

def create_new_product(product_title, product_url, product_price, product_image, product_preferred_price):
    new_product = Product(img_url=product_image, title = product_title, url = product_url, price = product_price, preferred_price=product_preferred_price)
    # inserts or updates entries in database
    new_product.save()
    return new_product

def printHelloInConsole(request):
    print("aufgerufen")
    result = "kk"
    return HttpResponse(result)

def load_more(request):
    loaded_item = request.GET.get('loaded_item')
    loaded_item_int = int("3")
    limit = 2
    post_obj = list(Product.objects.values() [loaded_item_int:loaded_item_int+limit])
    data = {'posts': post_obj}
    return JsonResponse(data=data)


#@csrf_exempt
def GetInputValue(request):
  input_value = request.POST['quantity']
  return HttpResponse(input_value)


"""def approve_group(request, pk):
    print("aufgerufen fr fr")
    group = Product.objects.get()
    #group.status = Status.approved
    group.save()
    return redirect(request, 'products')"""

@csrf_exempt
def xy(request):
    products = [product for product in Product.objects.all()]
    attributes = []
    return render(request, 'products/product_list.html',
                  {'attributes': attributes,
                   'products': products
                   })
@csrf_exempt
def add_prod(request):
    attributes = []

    if request.method == 'GET':
        return redirect('xy')
    if request.method == 'POST':
        print("post", request.method)
        if request.POST.get('submit') == 'Delete':
            print("delete button")
            print("delete button")
            # remove object from database
            pass
        if request.POST[list(request.POST)[1]].strip() != '':
            # scraping data of product
            new_product_url = request.POST[list(request.POST)[1]]
            new_product_max_price = request.POST[list(request.POST)[2]]
            print(new_product_url)
            print(request.POST)
            try:
                if "https://" not in new_product_url:
                    new_product_url = "https://" + new_product_url
                print("NPU:", new_product_url)
                response = urllib.request.urlopen(new_product_url)
                print("r",response)
                status_code = response.getcode()
                print(status_code)
                if status_code == 200:
                    print('Web site exists')
                    webpage = requests.get(new_product_url, headers=HEADERS, cookies=cookies)
                    soup = BeautifulSoup(webpage.content, "html.parser")

                    #children = soup.find('div', {'id': "img-canvas"})
                    children = soup.find_all("div", {"id": "imgTagWrapperId"})
                    if children == None:
                        new_product_image = "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
                    else:
                        # children = children.findChildren('img')
                        #new_product_image = children[-1].find("div", {"img", "src"})
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
                        new_product_price = soup.find("span",
                                                  attrs={'class': 'a-offscreen'}).string.strip()  # .string.strip().replace(',', '')
                        print("Produktpreis:", new_product_price)
                    except AttributeError:
                        new_product_price = "NA"

                    price = soup.find("span", attrs={'class': "a-offscreen"})  # aktueller Preis
                    if price != None:
                        price = price.string.strip()

                    delete = False  # dummy value

                    # create new product and add it to database
                    prod = Product.objects.create(image=new_product_image,
                                           title=new_product_title,
                                           url=new_product_url,
                                           price=new_product_price,
                                           preferred_price=new_product_max_price)
                    prod.save()

                else:
                    # Textanzeige im Browser hinzufuegen
                    print('Web site does not exist')
            except Exception as e:
                print("HTTP_Error")

        return redirect('xy')

def product_data(request):
    #print("***"*5000)
    print("okay")

    # eigentlich keine Datenbank notwendig,
    # bzw. einfach direkt den Wert mit BeautifulSoup auslesen, der jetzt gerade auf der Webseite steht
    # und z.B. jede Minute die Werte aktualisieren
    # Liste an URL's aus Textdatei herauslesen und dann einfach die dazugehörigen Daten (Bild, Preis usw.)
    # aus der Webseite scrapen

    # sortieren damit neuestes Bild immer oben ist in der Liste
    #products = Product.objects.all().order_by('published_date')
    product_urls = [[prod.title, prod.url, prod.price, prod.img_url] for prod in Product.objects.all()[:5]]
    print("PURL:", product_urls)

    ## WICHTIG: Bevor Daten aus Datenbank gelesen und gescraped werden, vorher Objekt aus json-Datei laden und scrapen

    """
    # kein Teil des Programms. War nur voruebergehende Loesung
    # vllt. noch Titel hinzufuegen, vielleicht auch nicht, da sich diese aendern koennen
    with open('products/products.json', 'w', encoding='utf-8') as output_file:
        output_file.write('[')
        for index, product in enumerate(product_urls):
            prod_title = product[0]
            prod_url = product[1] # hier dann url durch Textfield auf Webseite eintragen
            prod_preferred_price = product[2] # hier dann input durch Textfield auf Webseite
            prod_img_url = product[3]

            json_string = {"title": prod_title, "url": prod_url, "preferred_price": prod_preferred_price, "img_url": prod_img_url}
            # nicht verwechseln mit Preis und Preferred Price

            json.dump(json_string, output_file)

            if index + 1 != len(product_urls): # not adding the last comma in the json file
                output_file.write(',')
            print("IMAGE-URL:", product[0], product[2])

        output_file.write(']') # ending json
    """

    product_url = "https://www.amazon.de/Dont-Toy-Me-Miss-Nagatoro/dp/1647291658/ref=d_bmx_dp_rf7uzdqo_sccl_1_3/262-7541205-9327927?pd_rd_w=XfG4P&content-id=amzn1.sym.f58a5e44-b983-4f04-8310-d4f7fbbc8e54&pf_rd_p=f58a5e44-b983-4f04-8310-d4f7fbbc8e54&pf_rd_r=EFYJSVWFMNVWFGVH3TQF&pd_rd_wg=YVCHy&pd_rd_r=c6c87111-f238-447a-bcfc-2e649f705323&pd_rd_i=1647291658&psc=1"
    HEADERS = ({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 44.0.2403.157 Safari / 537.36'
    })
    cookies = dict(language='de')

    preferred_price = "1.2"

    # save all the data in the data base
    # create new product only if button "add" is clicked --> see later


    product_url = "https://www.amazon.de/Classroom-Elite-Year-Two-Band/dp/1638583374/ref=sr_1_1?keywords=classroom+of+the+elite+light+novel&qid=1666686887&qu=eyJxc2MiOiI0LjEwIiwicXNhIjoiMy44OCIsInFzcCI6IjQuMTMifQ%3D%3D&sprefix=classroom+of%2Caps%2C157&sr=8-1"
    #product_url = "https://www.amazon.de/Classroom-Elite-Light-Novel-Vol/dp/1645054373/ref=d_zg-te-pba_sccl_1_4/259-5321129-9342857?pd_rd_w=fKlS6&content-id=amzn1.sym.01b1d604-dbb9-4627-a9a0-2dd65ec3700f&pf_rd_p=01b1d604-dbb9-4627-a9a0-2dd65ec3700f&pf_rd_r=C85TK78EQMAQRX408N54&pd_rd_wg=1VQh4&pd_rd_r=49384ac0-0c9b-49df-aa1e-3ef9e81e87e3&pd_rd_i=1645054373&psc=1"
    #product_url = "https://www.amazon.de/Apple-AirPods-Ladecase-Neuestes-Modell/dp/B07PZR3PVB/ref=sr_1_2?m=A8KICS1PHF7ZO&pd_rd_r=04e683ff-0bc1-4ebc-b86a-e87b51ce3c6a&pd_rd_w=4Q7CE&pd_rd_wg=8XLKM&pf_rd_p=de99245d-fc66-413a-bdb1-143fd2a1e4d2&pf_rd_r=VV0W7WWW629Q5QN4GZA4&qid=1680211985&s=warehouse-deals&sr=1-2"
    product_url = "https://www.amazon.de/Beats-Wireless-Over%E2%80%91Ear-Kopfhörer-Mattschwarz/dp/B08529DT8N/ref=sr_1_23?m=A8KICS1PHF7ZO&pd_rd_r=04e683ff-0bc1-4ebc-b86a-e87b51ce3c6a&pd_rd_w=4Q7CE&pd_rd_wg=8XLKM&pf_rd_p=de99245d-fc66-413a-bdb1-143fd2a1e4d2&pf_rd_r=VV0W7WWW629Q5QN4GZA4&qid=1680211985&s=warehouse-deals&sr=1-23"
    #product_url = "https://www.amazon.de/Certain-Scientific-Railgun-Vol-15/dp/1645052311/ref=sr_1_9?__mk_de_DE=ÅMÅŽÕÑ&crid=ROM3ZN0C61T3&keywords=railgun+manga&qid=1680213089&sprefix=railgun+mang%2Caps%2C97&sr=8-9"


    """
    webpage = requests.get(product_url, headers=HEADERS, cookies=cookies)
    soup = BeautifulSoup(webpage.content, "lxml")

    find_img_canvas = soup.find('div', {'id': "img-canvas"})
    print("findimgvanvas:", find_img_canvas)
    if find_img_canvas == None:
        # get image url through id=imgTagWrapper
        imgurl = soup.find('div', {'id': 'imgTagWrapperId'}).findChildren('img')[-1]['src']
        # was wenn beides nicht vorhanden?
    else:
        imgurl = find_img_canvas.findChildren('img')[-1]['src']
    #imgurl = None # ???????
    title = soup.find("span", attrs={"id": 'productTitle'}).string.strip()
    url = product_url
    price = soup.find("span", attrs={'class': "a-offscreen"}).string.strip()
    """

    # get all relevant products
    # all(): all created products
    # filter(condition): all products under a certain condition, e.g. title='xy'

    # Auslesen aus Datenbank
    ## products = Product.objects.all()



    # see better solution later
    attributes = Product.print_instance_attributes()
    attributes = ['img_url', 'title', 'url', 'price', 'preferred_price', 'delete']

    # wofuer ist dieser Code nochmal da?
    #if request.method == 'GET': # ????
        #description = request.GET.get('amzn_url')
        #print("Description", description)
        #inputO = request.POST.get('inputO')

    # wenn Daten aus Datenbank gelesen werden sollen
    products = []
    for product in Product.objects.all():
        img_url = product.img_url
        title = product.title
        url = product.url
        #price = product.price
        preferred_price = product.preferred_price
        print("URL:", url)

        webpage = requests.get(url, headers=HEADERS, cookies=cookies)
        soup = BeautifulSoup(webpage.content, "html.parser")

        price = soup.find("span", attrs={'class': "a-offscreen"})   # aktueller Preis
        if price != None:
            price = price.string.strip()

        delete = False # dummy value

        # nicht vergessen, dass product_preferred_url irgendwo hin muss
        products.append({"img_url": img_url,
                         "title": title,
                         "url": url,
                         "price": price,
                         "delete": delete,
                         #"preferred_price": preferred_price,
                         })

    return render(request, 'products/product_list.html',
                  {'attributes': attributes,
                   'products': products,
                   #'images': media,    # unnoetig da bereits in products enthalten
                   'variable': 'Drekovic'})

    # hier fuer den Fall dass man die Daten nicht aus der Datenbank ausliest sondern automatisch scraped

    print()
    print("***"*5000)
    products = []
    with open('products/products.json', encoding='utf-8') as json_file:
        prod_data = json.loads(json_file.read())
        for index, product in enumerate(prod_data):
            if index == 3: # voruebergehend, um nicht alle json-Objekte durchzuiterieren
                break
            print("URL:", product['url'])
            if product['url'] != '': # eigentlich komplett unnoetige Zeile
                webpage = requests.get(product['url'], headers=HEADERS, cookies=cookies)
                soup = BeautifulSoup(webpage.content, "html.parser")

                # image urls
                product_images = []

                children = soup.find('div', {'id': "img-canvas"})

                if children == None:
                    product_image = "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
                else:
                    #children = children.findChildren('img')
                    product_image = children[-1]['src']
                    for child in children:
                        print("Child:", child)
                    print("PI:", product_image)

                # am besten schon vorher in Liste einfuegen, damit nicht immer in Webseite
                # gesucht werden muss und Ladezeiten somit nicht unnoetig lang sind
                try:
                    product_title = soup.find("span", attrs={"id": 'productTitle'}).string.strip()
                    # Erscheinungsdatum: id=productSubtitle
                    # product_title = product_title.string.strip().replace(',', ''
                    print("-"*50)
                except AttributeError:
                    product_title = "NA"

                # alle Daten aus Datenbank in Tabelle einfügen, bis auf Preis.
                # Preis jedes Mal bei Aufruf aus Amazon-Webseite ausfiltern und vergleichen ob
                # sich Wert veraendert hat
                try:
                    product_price = soup.find("span", attrs={'class': 'a-offscreen'}).string.strip() # .string.strip().replace(',', '')
                    print("Produktpreis:", product_price)
                except AttributeError:
                    product_price = "NA"

                delete = False

                # this is probably needed (not sure) when more than one image is found
                for row in soup.findAll('div', {'id': "img-canvas"}):
                    print("R:", row.findNext)

                print("Produkttitel:", product_title)

                # nicht vergessen, dass product_preferred_url irgendwo hin muss
                products.append({"title": product_title,
                                 "url": product['url'],
                                 "price": product_price,
                                 "img_url": product_image,
                                 "delete": delete,}) #, "price": product_price})
    """

    # ab hier dann den aktuellen Preis, die image_url usw. ermitteln und dann in list products eintragen,
    # damit diese in Tabelle angezeigt werden koennen


#        for i in json.loads(prod_data):
#            print(i)

    if True:
        lines = prods.readlines()
        for product in lines:
            print("Zeile:", product)
            product_details = re.split(r',(?=")', product) # product.split('\'') # falsch. NOchmal anschauen wie splitten
            print("PRodDetails:", product_details)
            current_price = ""
            print(len(product_details))
            if product_details[2] != "''":
                # update if url is not empty
                product_details[2] = product_details[2][1:-1]
                print("proddd", product_details[2])
                current_price = BeautifulSoup(requests.get(product_details[2], headers=HEADERS, cookies=cookies).content, 'lxml').find("span", attrs={"class": 'a-offscreen'})

            print("Aktueller Preis:", current_price)
            products.append([product_details[0], product_details[1], product_details[2], current_price])

    """

    print("Products:", products)

    # ab hier weiter
    print("request-method:", request.POST.get('sms'))

    return render(request, 'products/product_list.html',
                  {'attributes': attributes,
                   'products': products,
                   #'images': media,    # unnoetig da bereits in products enthalten
                   'variable': 'Drekovic'})


def YOUR_VIEW_DEF(request, pk):
    Product.objects.filter(pk=pk).update(views=('views')+1)
    return HttpResponseRedirect(request.GET.get('next'))

def my_view(request):
    print("request-method:", request.method)
    print("Methode wurde aufgerufen.")
    if request.method == 'POST':
        if request.POST.get('sms'):
            # do something with text area data since SMS was checked
            print("erfolgreich aufgerufen")
            print(request.POST.get('my_textarea'))

        # process form as usual.

def excel_formatting(request):
    pass

from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

def product_edit(request, pk):
    post = get_object_or_404(Product, pk=pk)
    if request.method == "GET":
        form = ProductForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            #post.author = request.user
            #post.published_date = timezone.now()
            post.save()
            return redirect('products_detail', pk=post.pk)
    else:
        form = ProductForm(instance=post)
    return render(request, 'products/products_edit.html', {'form': form})

def product_new(request):
    if request.method == "GET":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            #product.title = request.
            #product.published_date = timezone.now()
            product.save()
            print("ok ok ok")
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/products_edit.html', {'form': form})


def username_exists(request):
    print("kkk")
    return JsonResponse({'msg': 'Drekoviccc'})