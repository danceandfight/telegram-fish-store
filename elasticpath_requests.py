import requests

def get_elasticpath_token(client_id, client_secret):

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    token = response.json()['access_token']
    return token


def get_products_names_ids(token):

    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    products = requests.get('https://api.moltin.com/pcm/products', headers=headers)
    products.raise_for_status()
    
    names_and_ids = [(item['attributes']['name'], item['id']) for item in products.json()['data']]
    
    return names_and_ids

def get_products_prices(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    pricebooks = requests.get('https://api.moltin.com/pcm/pricebooks', headers=headers)
    pricebooks.raise_for_status()
    pricebook_id = pricebooks.json()['data'][0]['id']
    pricebook = requests.get(f'https://api.moltin.com/pcm/pricebooks/{pricebook_id}?include=prices', headers=headers)
    pricebook.raise_for_status()
    prod_prices = pricebook.json()['included']
    prices = {}
    for prod_price in prod_prices: 
        price_in_cents = prod_price['attributes']['currencies']['USD']['amount']
        price_in_usd = price_in_cents // 100
        prod_sku = prod_price['attributes']['sku']
        prices[prod_sku] = price_in_usd
    return prices
        

def get_product_by_id(token, id, prices):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    product = requests.get(f'https://api.moltin.com/pcm/products/{id}', headers=headers)
    product.raise_for_status()
    product_json = product.json()
    product_name = product_json['data']['attributes']['name']
    product_sku = product_json['data']['attributes']['sku']
    product_description = product_json['data']['attributes']['description']
    inventory = requests.get(f'https://api.moltin.com/v2/inventories/{id}', headers=headers)
    inventory.raise_for_status()
    amount_in_stock = inventory.json()['data']['available']
    price = prices[product_sku]
    image_id = product.json()['data']['relationships']['main_image']['data']['id']
    image_file = requests.get(f'https://api.moltin.com/v2/files/{image_id}', headers=headers)
    image_file.raise_for_status()
    image_link = image_file.json()['data']['link']['href']
    return product_name, product_description, amount_in_stock, price, image_link


def add_product_to_cart(token, user_id, prod_id, quantity):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    json_data = {'data': {
        "id": prod_id, 
        "type": "cart_item", 
        "quantity": quantity,
        }
    }
    response = requests.post(f'https://api.moltin.com/v2/carts/{user_id}/items', headers=headers, json=json_data)
    response.raise_for_status()


def get_cart(token, user_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    cart = requests.get(f'https://api.moltin.com/v2/carts/{user_id}/items', headers=headers)
    cart.raise_for_status()
    cart_items = cart.json()['data']
    message_with_cart_content = ''
    for item in cart_items:
        item_name = item['name']
        item_description = item['description']
        item_price = item['meta']['display_price']['with_tax']['unit']['formatted']
        combined_price = item['meta']['display_price']['with_tax']['value']['formatted']
        quantity = item['quantity']
        item_in_cart = f"{item_name}\n{item_description}\n{item_price}\n{quantity}kg in cart for {combined_price}\n\n"
        message_with_cart_content += item_in_cart
    cart_value = cart.json()['meta']['display_price']['with_tax']['formatted']
    message_with_cart_content += f'Total: {cart_value}'
    return message_with_cart_content


def get_cart_item_names_and_ids(token, user_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    cart = requests.get(f'https://api.moltin.com/v2/carts/{user_id}/items', headers=headers)
    cart.raise_for_status()
    cart_items = cart.json()['data']
    prod_ids_with_names = [(item['id'], item['name']) for item in cart_items]
    return prod_ids_with_names


def remove_cart_item(token, user_id, prod_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{user_id}/items/{prod_id}', headers=headers)
    response.raise_for_status()


def save_client(token, user_id, email):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    json_data = {
        'data': {
            'type': 'customer',
            'name': str(user_id),
            'email': email,
        },
    }
    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=json_data)
    response.raise_for_status()




