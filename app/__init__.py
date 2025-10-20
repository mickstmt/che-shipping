# BUSCAR esta línea en tu app/__init__.py:
from app.routes import products, stock, prices, images, categories, auth

# CAMBIARLA por:
from app.routes import products, stock, prices, images, categories, auth, shipping

# BUSCAR estas líneas:
app.register_blueprint(products.bp)
app.register_blueprint(stock.bp)
app.register_blueprint(prices.bp)
app.register_blueprint(images.bp)
app.register_blueprint(categories.bp)
app.register_blueprint(auth.bp)

# AGREGAR esta línea al final:
app.register_blueprint(shipping.bp)
