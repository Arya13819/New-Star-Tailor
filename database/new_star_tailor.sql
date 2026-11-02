-- New Star Tailor: fresh database schema + service catalogue only.
-- Import into an EMPTY MySQL 8 / MariaDB database. No customer data or passwords.
-- Alembic revision is included; do not stamp or recreate existing databases.

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
INSERT INTO `alembic_version` VALUES
('2e3b1bebff15');
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `actor_user_id` int(11) DEFAULT NULL,
  `entity_type` varchar(40) NOT NULL,
  `entity_id` int(11) NOT NULL,
  `action` varchar(60) NOT NULL,
  `from_value` varchar(255) DEFAULT NULL,
  `to_value` varchar(255) DEFAULT NULL,
  `detail` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `actor_user_id` (`actor_user_id`),
  KEY `ix_audit_logs_created_at` (`created_at`),
  KEY `ix_audit_logs_entity_id` (`entity_id`),
  KEY `ix_audit_logs_entity_type` (`entity_type`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`actor_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
INSERT INTO `audit_logs` VALUES
(NULL,'service',1,'seed',NULL,'SHIRT',NULL,'2026-10-31 08:51:11',1),
(NULL,'service',2,'seed',NULL,'PANT',NULL,'2026-10-31 08:51:11',2),
(NULL,'service',3,'seed',NULL,'SHIRT_PANT_COMBO',NULL,'2026-10-31 08:51:11',3),
(NULL,'service',4,'seed',NULL,'POLICE_KHAAKI',NULL,'2026-10-31 08:51:11',4),
(NULL,'service',5,'seed',NULL,'CRPF_KHAAKI',NULL,'2026-10-31 08:51:11',5),
(NULL,'service',6,'seed',NULL,'CRPF_CHEETAH',NULL,'2026-10-31 08:51:11',6),
(NULL,'service',7,'seed',NULL,'CRPF_KHAAKI_DANGRI',NULL,'2026-10-31 08:51:11',7),
(NULL,'service',8,'seed',NULL,'ARMY_PATTERN',NULL,'2026-10-31 08:51:11',8),
(NULL,'service',9,'seed',NULL,'CHEETAH_US_PATTERN',NULL,'2026-10-31 08:51:11',9);
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `name` varchar(120) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `address` varchar(400) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_customers_mobile` (`mobile`),
  KEY `ix_customers_user_id` (`user_id`),
  CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `enquiries` (
  `name` varchar(120) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `address` varchar(400) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` varchar(12) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `converted_order_id` int(11) DEFAULT NULL,
  `converted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_enquiries_mobile` (`mobile`),
  KEY `ix_enquiries_status` (`status`),
  KEY `ix_enquiries_converted_order_id` (`converted_order_id`),
  CONSTRAINT `fk_enquiries_converted_order_id_orders` FOREIGN KEY (`converted_order_id`) REFERENCES `orders` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `measurement_versions` (
  `measurement_id` int(11) NOT NULL,
  `version_number` int(11) NOT NULL,
  `shirt_length` decimal(5,2) DEFAULT NULL,
  `shirt_chest` decimal(5,2) DEFAULT NULL,
  `shirt_shoulder` decimal(5,2) DEFAULT NULL,
  `shirt_sleeves` decimal(5,2) DEFAULT NULL,
  `shirt_neck` decimal(5,2) DEFAULT NULL,
  `pant_length` decimal(5,2) DEFAULT NULL,
  `pant_waist` decimal(5,2) DEFAULT NULL,
  `pant_hips` decimal(5,2) DEFAULT NULL,
  `pant_mori` decimal(5,2) DEFAULT NULL,
  `unit` varchar(4) NOT NULL,
  `fitting_preference` varchar(10) DEFAULT NULL,
  `allowance` varchar(120) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `alteration_notes` text DEFAULT NULL,
  `source` varchar(10) NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_measurement_version` (`measurement_id`,`version_number`),
  KEY `created_by_id` (`created_by_id`),
  KEY `ix_measurement_versions_measurement_id` (`measurement_id`),
  CONSTRAINT `measurement_versions_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `measurement_versions_ibfk_2` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `measurements` (
  `customer_id` int(11) NOT NULL,
  `current_version_id` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_id` (`customer_id`),
  KEY `ix_measurements_current_version_id` (`current_version_id`),
  CONSTRAINT `measurements_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `customer_id` int(11) DEFAULT NULL,
  `order_id` int(11) DEFAULT NULL,
  `channel` varchar(10) NOT NULL,
  `type` varchar(24) NOT NULL,
  `status` varchar(12) NOT NULL,
  `dedupe_key` varchar(190) DEFAULT NULL,
  `to_address` varchar(190) DEFAULT NULL,
  `body` text DEFAULT NULL,
  `payload_json` text DEFAULT NULL,
  `scheduled_at` datetime DEFAULT NULL,
  `sent_at` datetime DEFAULT NULL,
  `provider_message_id` varchar(190) DEFAULT NULL,
  `error_message` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dedupe_key` (`dedupe_key`),
  KEY `ix_notifications_customer_id` (`customer_id`),
  KEY `ix_notifications_order_id` (`order_id`),
  KEY `ix_notifications_scheduled_at` (`scheduled_at`),
  KEY `ix_notifications_status` (`status`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_id` int(11) NOT NULL,
  `service_id` int(11) DEFAULT NULL,
  `service_name_snapshot` varchar(120) NOT NULL,
  `category_snapshot` varchar(12) NOT NULL,
  `stitching_price` decimal(10,2) NOT NULL,
  `material_price` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL,
  `line_total` decimal(10,2) NOT NULL,
  `measurement_version_id` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `measurement_version_id` (`measurement_version_id`),
  KEY `service_id` (`service_id`),
  KEY `ix_order_items_order_id` (`order_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`measurement_version_id`) REFERENCES `measurement_versions` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_sequences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `last_seq` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_number` varchar(20) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `source` varchar(10) NOT NULL,
  `status` varchar(12) NOT NULL,
  `priority` varchar(10) NOT NULL,
  `fabric_source` varchar(10) NOT NULL,
  `requested_delivery_date` date DEFAULT NULL,
  `confirmed_delivery_date` date DEFAULT NULL,
  `subtotal_stitching` decimal(10,2) NOT NULL,
  `subtotal_material` decimal(10,2) NOT NULL,
  `grand_total` decimal(10,2) NOT NULL,
  `required_advance` decimal(10,2) NOT NULL,
  `advance_satisfied` tinyint(1) NOT NULL,
  `self_measurement_acknowledged` tinyint(1) NOT NULL,
  `self_measurement_acknowledged_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  `delivered_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `created_by_id` (`created_by_id`),
  KEY `ix_orders_customer_id` (`customer_id`),
  KEY `ix_orders_status` (`status`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_events` (
  `provider` varchar(40) NOT NULL,
  `event_id` varchar(190) NOT NULL,
  `event_type` varchar(80) DEFAULT NULL,
  `payload_hash` varchar(64) DEFAULT NULL,
  `raw_payload` text DEFAULT NULL,
  `payment_id` int(11) DEFAULT NULL,
  `order_id` int(11) DEFAULT NULL,
  `processed_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_payment_event` (`provider`,`event_id`),
  KEY `order_id` (`order_id`),
  KEY `payment_id` (`payment_id`),
  CONSTRAINT `payment_events_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payment_events_ibfk_2` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `method` varchar(10) NOT NULL,
  `status` varchar(10) NOT NULL,
  `provider` varchar(40) DEFAULT NULL,
  `transaction_reference` varchar(190) DEFAULT NULL,
  `note` varchar(300) DEFAULT NULL,
  `recorded_by_id` int(11) DEFAULT NULL,
  `verified_by_id` int(11) DEFAULT NULL,
  `verified_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recorded_by_id` (`recorded_by_id`),
  KEY `verified_by_id` (`verified_by_id`),
  KEY `ix_payments_customer_id` (`customer_id`),
  KEY `ix_payments_order_id` (`order_id`),
  KEY `ix_payments_status` (`status`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`recorded_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payments_ibfk_4` FOREIGN KEY (`verified_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reference_images` (
  `order_id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `storage_path` varchar(500) NOT NULL,
  `mime_type` varchar(60) NOT NULL,
  `file_size` int(11) NOT NULL,
  `uploaded_by_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `uploaded_by_id` (`uploaded_by_id`),
  KEY `ix_reference_images_order_id` (`order_id`),
  CONSTRAINT `reference_images_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reference_images_ibfk_2` FOREIGN KEY (`uploaded_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `services` (
  `code` varchar(40) NOT NULL,
  `name_en` varchar(120) NOT NULL,
  `name_hi` varchar(120) DEFAULT NULL,
  `category` varchar(12) NOT NULL,
  `default_stitching_price` decimal(10,2) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `sort_order` int(11) NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
INSERT INTO `services` VALUES
('SHIRT','Shirt','शर्ट','SHIRT',NULL,1,10,NULL,1,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('PANT','Pant','पैंट','PANT',NULL,1,20,NULL,2,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('SHIRT_PANT_COMBO','Shirt + Pant Combo','शर्ट + पैंट सेट','SHIRT',550.00,1,30,NULL,3,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('POLICE_KHAAKI','Police Khaaki','पुलिस खाकी','POLICE',700.00,1,40,NULL,4,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('CRPF_KHAAKI','CRPF Khaaki','सीआरपीएफ खाकी','CRPF',700.00,1,50,NULL,5,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('CRPF_CHEETAH','CRPF Cheetah','सीआरपीएफ चीता','CRPF',700.00,1,60,NULL,6,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('CRPF_KHAAKI_DANGRI','CRPF Khaaki Dangri','सीआरपीएफ खाकी डंगरी','CRPF',NULL,1,70,NULL,7,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('ARMY_PATTERN','Army Pattern','आर्मी पैटर्न','ARMY',NULL,1,80,NULL,8,'2026-10-31 08:51:11','2026-10-31 08:51:11'),
('CHEETAH_US_PATTERN','Cheetah US Pattern','चीता यूएस पैटर्न','ARMY',850.00,1,90,NULL,9,'2026-10-31 08:51:11','2026-10-31 08:51:11');
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `key` varchar(120) NOT NULL,
  `value_json` text DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `name` varchar(120) NOT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `email` varchar(190) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `preferred_locale` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `uq_users_mobile` (`mobile`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

