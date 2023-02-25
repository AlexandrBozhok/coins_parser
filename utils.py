from schemas import Product


def build_new_product_message(product: Product) -> str:
    msg = f'З`явився новий товар на сайті!\n' \
          f'Назва: {product.name}\n' \
          f'Ціна: {product.price} грн.\n' \
          f'{product.url}'
    return msg
