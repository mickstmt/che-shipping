-- Script de inicialización de base de datos
-- Che Shipping Service

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS shipping_chile CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE shipping_chile;

-- Tabla de zonas de envío
CREATE TABLE IF NOT EXISTS shipping_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    min_km DECIMAL(10,2) NOT NULL,
    max_km DECIMAL(10,2) NOT NULL,
    price_clp INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_range (min_km, max_km),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de métodos de envío
CREATE TABLE IF NOT EXISTS shipping_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_km DECIMAL(10,2) DEFAULT 8.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de cotizaciones
CREATE TABLE IF NOT EXISTS shipping_quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100),
    origin_address TEXT,
    destination_address TEXT NOT NULL,
    origin_lat DECIMAL(10,8),
    origin_lng DECIMAL(11,8),
    destination_lat DECIMAL(10,8),
    destination_lng DECIMAL(11,8),
    distance_km DECIMAL(10,2) NOT NULL,
    duration_minutes INT,
    shipping_method_id INT,
    zone_id INT,
    price_clp INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    router_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipping_method_id) REFERENCES shipping_methods(id),
    FOREIGN KEY (zone_id) REFERENCES shipping_zones(id),
    INDEX idx_session (session_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar datos por defecto

-- Métodos de envío por defecto
INSERT INTO shipping_methods (name, code, description, start_time, end_time, max_km) VALUES
('Envío Hoy', 'envio_hoy', 'Entrega el mismo día (disponible hasta las 18:00)', '00:01:00', '18:00:00', 8.0),
('Envío Programado', 'envio_programado', 'Entrega programada para el día siguiente', '00:00:00', '23:59:00', 8.0);

-- Zonas de envío por defecto
INSERT INTO shipping_zones (min_km, max_km, price_clp) VALUES
(0.0, 3.0, 3500),
(3.0, 4.0, 4500),
(4.0, 5.0, 5000),
(5.0, 6.0, 5500),
(6.0, 8.0, 6500);

-- Verificar inserción
SELECT 'Métodos de envío creados:' as info;
SELECT id, name, code, max_km FROM shipping_methods;

SELECT 'Zonas de envío creadas:' as info;
SELECT id, min_km, max_km, price_clp FROM shipping_zones ORDER BY min_km;
