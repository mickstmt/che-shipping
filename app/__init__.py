# Agregar esta línea con las otras importaciones de routes
from app.routes import products, stock, prices, images, categories, auth, shipping

# Agregar esta línea con los otros register_blueprint
app.register_blueprint(shipping.bp)
