-- Tabla de zonas de envío por kilometraje
CREATE TABLE IF NOT EXISTS `shipping_zones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `min_km` decimal(5,2) NOT NULL,
  `max_km` decimal(5,2) NOT NULL,
  `price_clp` int(11) NOT NULL COMMENT 'Precio en pesos chilenos',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_km_range` (`min_km`, `max_km`),
  INDEX `idx_active_zones` (`is_active`, `min_km`, `max_km`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de métodos de envío
CREATE TABLE IF NOT EXISTS `shipping_methods` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) NOT NULL UNIQUE,
  `description` text,
  `is_active` tinyint(1) DEFAULT 1,
  `start_time` time NOT NULL COMMENT 'Hora de inicio de disponibilidad',
  `end_time` time NOT NULL COMMENT 'Hora de fin de disponibilidad',
  `max_km` decimal(5,2) DEFAULT 7.00 COMMENT 'Distancia máxima en km',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_method_code` (`code`),
  INDEX `idx_active_methods` (`is_active`, `start_time`, `end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de cotizaciones de envío
CREATE TABLE IF NOT EXISTS `shipping_quotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) DEFAULT NULL COMMENT 'ID de sesión de Jumpseller',
  `origin_address` text,
  `destination_address` text NOT NULL,
  `origin_lat` decimal(10,8) DEFAULT NULL COMMENT 'Latitud origen',
  `origin_lng` decimal(11,8) DEFAULT NULL COMMENT 'Longitud origen',
  `destination_lat` decimal(10,8) DEFAULT NULL COMMENT 'Latitud destino',
  `destination_lng` decimal(11,8) DEFAULT NULL COMMENT 'Longitud destino',
  `distance_km` decimal(6,2) NOT NULL COMMENT 'Distancia en kilómetros',
  `duration_minutes` int(11) DEFAULT NULL COMMENT 'Tiempo estimado en minutos',
  `shipping_method_id` int(11) DEFAULT NULL,
  `zone_id` int(11) DEFAULT NULL,
  `price_clp` int(11) NOT NULL COMMENT 'Precio cotizado en pesos chilenos',
  `is_available` tinyint(1) DEFAULT 1,
  `router_response` longtext COMMENT 'Respuesta completa de RouterService en JSON',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_distance` (`distance_km`),
  KEY `fk_shipping_method` (`shipping_method_id`),
  KEY `fk_shipping_zone` (`zone_id`),
  CONSTRAINT `fk_shipping_method` FOREIGN KEY (`shipping_method_id`) REFERENCES `shipping_methods` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_shipping_zone` FOREIGN KEY (`zone_id`) REFERENCES `shipping_zones` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar datos por defecto
INSERT INTO `shipping_methods` (`name`, `code`, `description`, `start_time`, `end_time`, `max_km`) VALUES
('Envío Hoy', 'envio_hoy', 'Entrega el mismo día (disponible hasta las 18:00)', '00:01:00', '18:00:00', 7.00),
('Envío Programado', 'envio_programado', 'Entrega programada para el día siguiente', '00:00:00', '23:59:00', 7.00);

INSERT INTO `shipping_zones` (`min_km`, `max_km`, `price_clp`) VALUES
(0.0, 3.0, 3500),
(3.0, 4.0, 4500),
(4.0, 5.0, 5000),
(5.0, 6.0, 5500),
(6.0, 7.0, 6500);
