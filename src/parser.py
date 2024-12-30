import requests
from sqlalchemy.orm import Session

from database import get_db
from models import Product, Category, ProductCategory

# url api с категориями
categories_url = "https://api-ecomm.sdvor.com/occ/v2/sd/catalogs/sdvrProductCatalog/Online/"


# кидаем запрос на категории
def fetch_categories():
    response = requests.get(categories_url)
    return response.json().get('categories', [])


# рекурсивный проход по всем категориям
def select_category(categories):
    for category in categories:
        print(f'Parsed category: {category['name']}')

        if 'subcategories' in category and category['subcategories']:
            merge_entities([Category(id=x['id'], name=x['name'], parent_id=category['id']) for x in
                            category['subcategories']])
            select_category(category['subcategories'])
        else:
            product_to_merge = fetch_products(category['id'])
            merge_entities([Product(id=x['code'], name=x['name'], price=x['price']['value']) for x in
                            product_to_merge])
            merge_entities([ProductCategory(product_id=x['code'], category_id=category['id']) for x in
                            product_to_merge])
            return


# получение продуктов категории
def fetch_products(category_id):
    products_url = f"https://api-ecomm.sdvor.com/occ/v2/sd/products/search?fields=algorithmsForAddingRelatedProducts%2CcategoryCode%2Cproducts(code%2Cbonus%2Cslug%2CdealType%2Cname%2Cunit%2Cunits(FULL)%2CunitPrices(FULL)%2CavailableInStores(FULL)%2Cbadges(DEFAULT)%2Cmultiunit%2Cprice(FULL)%2CcrossedPrice(FULL)%2CtransitPrice(FULL)%2CpersonalPrice(FULL)%2Cimages(DEFAULT)%2Cstock(FULL)%2CmarketingAttributes%2CisArchive%2Ccategories(FULL)%2CcategoryNamesForAnalytics)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2Cbanners(FULL)%2CfreeTextSearch%2CcurrentQuery%2CkeywordRedirectUrl&currentPage=0&pageSize=100008&facets=allCategories%3A{category_id}&lang=ru&curr=RUB&deviceType=desktop&baseStore=ekb"

    try:
        response = requests.get(products_url)
        return response.json().get('products', [])
    except:
        response = requests.get(products_url)
        return response.json().get('products', [])


# запуск парсера
def run():
    categories = fetch_categories()
    catalog_node = list(filter(lambda x: x['id'] == 'catalog', categories))[0]
    merge_entities([Category(id=x['id'], name=x['name'], parent_id=catalog_node['id']) for x in
                    catalog_node['subcategories']])
    select_category(catalog_node['subcategories'])


# merge сущностей в бд
def merge_entities(to_merge):
    db: Session = next(get_db())
    for x in to_merge:
        db.merge(x)
    db.commit()
    db.close()


# точка входа в приложение
if __name__ == "__main__":
    run()
