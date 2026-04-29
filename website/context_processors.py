def cart_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(int(item.get('quantity', 1)) for item in cart.values())
    return {'total_items': total_items}