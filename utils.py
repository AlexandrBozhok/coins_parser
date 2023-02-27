from schemas import Product


def build_new_product_message(product: Product) -> str:
    msg = f'<b>З`явився новий товар на сайті!</b>\n\n' \
          f'<b>Назва:</b> {product.name}\n' \
          f'<b>Ціна:</b> {product.price} грн.\n' \
          f'{product.url}'
    return msg


def get_known_product_message(product: Product) -> str:
    msg = f'<b>Товар знову у продажі!</b>\n\n' \
          f'<b>Назва:</b> {product.name}\n' \
          f'<b>Ціна:</b> {product.price} грн.\n' \
          f'{product.url}'
    return msg
