# выполнил Азанов Никита Александрович РИ-320913

import requests
import json

# url api с категориями
categories_url = "https://api-ecomm.sdvor.com/occ/v2/sd/catalogs/sdvrProductCatalog/Online/"


# кидаем запрос на категории
def fetch_categories():
    response = requests.get(categories_url)
    return response.json().get('categories', [])


# отобразить категории
def display_categories(categories, level=0):
    for i, category in enumerate(categories):
        print("  " * level + f"{i + 1}. {category['name']} ({category['id']})")

        if 'subcategories' in category and category['subcategories']:
            display_categories(category['subcategories'], level + 1)


# метод выбора категорий и подкатегорий
def select_category(categories, first_choice=True):
    if first_choice:
        selected_category = categories[1]

        if 'subcategories' in selected_category and selected_category['subcategories']:
            return select_category(selected_category['subcategories'], False)
        else:
            return selected_category
    else:
        while True:
            for i, category in enumerate(categories):
                print(f"{i + 1}. {category['name']}")

            choice = input("Выберите категорию, или введите 'выход', чтобы закончить: ")

            if choice.lower() == 'выход':
                return None

            try:
                index = int(choice) - 1

                if 0 <= index < len(categories):
                    selected_category = categories[index]

                    if 'subcategories' in selected_category and selected_category['subcategories']:
                        print(f"Выбрана категория: {selected_category['name']}")
                        print()

                        return select_category(selected_category['subcategories'], False)
                    else:
                        return selected_category
                else:
                    print("Выбрана некорректная категория.")
                    print()
            except ValueError:
                print("Ввод некорректен. Введите число, или напишите 'выход'.")
                print()


# получение продуктов категории
def fetch_products(category_id):
    products_url = f"https://api-ecomm.sdvor.com/occ/v2/sd/products/search?fields=algorithmsForAddingRelatedProducts%2CcategoryCode%2Cproducts(code%2Cbonus%2Cslug%2CdealType%2Cname%2Cunit%2Cunits(FULL)%2CunitPrices(FULL)%2CavailableInStores(FULL)%2Cbadges(DEFAULT)%2Cmultiunit%2Cprice(FULL)%2CcrossedPrice(FULL)%2CtransitPrice(FULL)%2CpersonalPrice(FULL)%2Cimages(DEFAULT)%2Cstock(FULL)%2CmarketingAttributes%2CisArchive%2Ccategories(FULL)%2CcategoryNamesForAnalytics)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2Cbanners(FULL)%2CfreeTextSearch%2CcurrentQuery%2CkeywordRedirectUrl&currentPage=0&pageSize=100008&facets=allCategories%3A{category_id}&lang=ru&curr=RUB&deviceType=desktop&baseStore=ekb"
    response = requests.get(products_url)

    return response.json().get('products', [])


# обработка категорий
def process_categories(categories):
    print("Категории:")
    selected_category = select_category(categories)

    if selected_category:
        print(f"Выбрана категория: {selected_category['name']}")
        products = fetch_products(selected_category['id'])

        if products:
            process_products(products)
        else:
            print("Программа окончена.")
    else:
        print("Программа окончена.")


# обработка продуктов
def process_products(products):
    print()
    print("Продукты:")

    for product in products:
        price = product.get('price', {}).get('value', 'цена не указана')
        print(f"- {product['name']} ({price} рублей)")


# основной метод
def main():
    categories = fetch_categories()

    if categories:
        process_categories(categories)
    else:
        print("Программа окончена.")


# точка входа в приложение
if __name__ == "__main__":
    main()