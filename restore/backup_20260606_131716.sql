-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: warehouse_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `agents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_agen` varchar(50) DEFAULT NULL,
  `nama_agen` varchar(200) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `telepon` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_agen` (`kode_agen`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agents`
--

LOCK TABLES `agents` WRITE;
/*!40000 ALTER TABLE `agents` DISABLE KEYS */;
INSERT INTO `agents` VALUES (1,'AG001','Agen Cirebon','Cirebon','08123456789'),(3,'AG002','Toko Makmur',NULL,'08573456789'),(4,'AG003','Indo Jaya',NULL,'08567891236');
/*!40000 ALTER TABLE `agents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `aktivitas` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,1,'Login ke sistem','2026-06-04 13:56:48'),(2,2,'Login ke sistem','2026-06-04 14:06:35'),(3,4,'Login ke sistem','2026-06-04 14:07:03'),(4,1,'Login ke sistem','2026-06-04 14:09:03'),(5,1,'Login ke sistem','2026-06-04 14:14:05'),(6,1,'Membuat DO DO-20260605-001','2026-06-05 17:39:06'),(7,1,'Kirim DO ID 1','2026-06-05 17:51:51'),(8,1,'Membuat DO DO-20260605-002','2026-06-05 19:03:14'),(9,1,'Kirim DO ID 4','2026-06-05 19:03:52'),(10,1,'Submit PO ID 7','2026-06-05 19:12:36'),(11,1,'Receive PO ID 7','2026-06-05 19:12:37'),(12,1,'Membuat PO PO-20260605-2790','2026-06-05 19:48:40'),(13,1,'Submit PO ID 8','2026-06-05 19:49:34'),(14,1,'Approve PO ID 8','2026-06-05 19:55:39'),(15,1,'Membuat PO PO-20260605-2791','2026-06-05 20:03:48'),(16,1,'Submit PO ID 9','2026-06-05 20:04:16'),(17,1,'Approve PO ID 9','2026-06-05 20:04:18'),(18,1,'Login ke sistem','2026-06-06 09:58:12'),(19,1,'Receive PO ID 9','2026-06-06 09:58:20'),(20,1,'Receive PO ID 8','2026-06-06 09:58:37'),(21,1,'Membuat DO DO-20260606-001','2026-06-06 10:18:39'),(22,1,'Submit DO ID 5','2026-06-06 10:19:16'),(23,1,'Approve DO ID 5','2026-06-06 10:19:24'),(24,1,'Kirim DO ID 5','2026-06-06 10:19:31'),(25,3,'Login ke sistem','2026-06-06 10:34:24'),(26,1,'Login ke sistem','2026-06-06 12:48:42'),(27,1,'Menambah user kasir2','2026-06-06 12:50:54'),(28,5,'Login ke sistem','2026-06-06 12:51:14'),(29,1,'Login ke sistem','2026-06-06 12:51:36'),(30,1,'Hapus User kasir2','2026-06-06 12:51:53'),(31,1,'Login ke sistem','2026-06-06 12:56:58'),(32,1,'Mengubah password','2026-06-06 12:57:23'),(33,1,'Login ke sistem','2026-06-06 12:57:36'),(34,1,'Reset Password User kasir','2026-06-06 13:01:18'),(35,3,'Login ke sistem','2026-06-06 13:01:33'),(36,3,'Mengubah password','2026-06-06 13:02:00'),(37,3,'Login ke sistem','2026-06-06 13:02:11'),(38,1,'Login ke sistem','2026-06-06 13:02:33');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_order_details`
--

DROP TABLE IF EXISTS `delivery_order_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `delivery_order_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `delivery_order_id` int(11) DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `qty` int(11) DEFAULT NULL,
  `harga_jual` decimal(15,2) DEFAULT NULL,
  `subtotal` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `delivery_order_id` (`delivery_order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `delivery_order_details_ibfk_1` FOREIGN KEY (`delivery_order_id`) REFERENCES `delivery_orders` (`id`),
  CONSTRAINT `delivery_order_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_order_details`
--

LOCK TABLES `delivery_order_details` WRITE;
/*!40000 ALTER TABLE `delivery_order_details` DISABLE KEYS */;
INSERT INTO `delivery_order_details` VALUES (1,1,1,20,270000.00,5400000.00),(2,2,1,5,270000.00,1350000.00),(3,2,3,5,45000.00,225000.00),(4,3,4,50,14000.00,700000.00),(5,4,4,5,14000.00,70000.00),(6,5,1,3,270000.00,810000.00),(7,5,4,4,14000.00,56000.00),(8,5,3,7,45000.00,315000.00);
/*!40000 ALTER TABLE `delivery_order_details` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ZERO_IN_DATE,NO_ZERO_DATE,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_stock_out
AFTER INSERT ON delivery_order_details
FOR EACH ROW
UPDATE products
SET stok = stok - NEW.qty
WHERE id = NEW.product_id */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `delivery_orders`
--

DROP TABLE IF EXISTS `delivery_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `delivery_orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nomor_do` varchar(50) DEFAULT NULL,
  `agent_id` int(11) DEFAULT NULL,
  `tanggal` date DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `status` enum('draft','open','approved','sent') DEFAULT 'draft',
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `delivery_orders_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`),
  CONSTRAINT `delivery_orders_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_orders`
--

LOCK TABLES `delivery_orders` WRITE;
/*!40000 ALTER TABLE `delivery_orders` DISABLE KEYS */;
INSERT INTO `delivery_orders` VALUES (1,'DO-001',1,'2026-05-30',1,'sent'),(2,'DO-20260603-001',4,'2026-06-03',1,'sent'),(3,'DO-20260605-001',3,'2026-06-05',1,'draft'),(4,'DO-20260605-002',1,'2026-06-05',1,'sent'),(5,'DO-20260606-001',3,'2026-06-06',1,'sent');
/*!40000 ALTER TABLE `delivery_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goods_receipt_details`
--

DROP TABLE IF EXISTS `goods_receipt_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `goods_receipt_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `receipt_id` int(11) DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `qty` int(11) DEFAULT NULL,
  `harga_beli` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `receipt_id` (`receipt_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `goods_receipt_details_ibfk_1` FOREIGN KEY (`receipt_id`) REFERENCES `goods_receipts` (`id`),
  CONSTRAINT `goods_receipt_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goods_receipt_details`
--

LOCK TABLES `goods_receipt_details` WRITE;
/*!40000 ALTER TABLE `goods_receipt_details` DISABLE KEYS */;
INSERT INTO `goods_receipt_details` VALUES (1,1,1,100,250000.00);
/*!40000 ALTER TABLE `goods_receipt_details` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ZERO_IN_DATE,NO_ZERO_DATE,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_stock_in
AFTER INSERT ON goods_receipt_details
FOR EACH ROW
UPDATE products
SET stok = stok + NEW.qty
WHERE id = NEW.product_id */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `goods_receipts`
--

DROP TABLE IF EXISTS `goods_receipts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `goods_receipts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nomor_penerimaan` varchar(50) DEFAULT NULL,
  `supplier_id` int(11) DEFAULT NULL,
  `tanggal` date DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `goods_receipts_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  CONSTRAINT `goods_receipts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goods_receipts`
--

LOCK TABLES `goods_receipts` WRITE;
/*!40000 ALTER TABLE `goods_receipts` DISABLE KEYS */;
INSERT INTO `goods_receipts` VALUES (1,'GR-001',1,'2026-05-30',1);
/*!40000 ALTER TABLE `goods_receipts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `barcode` varchar(50) DEFAULT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `nama_barang` varchar(200) DEFAULT NULL,
  `kategori` varchar(100) DEFAULT NULL,
  `satuan` varchar(50) DEFAULT NULL,
  `stok` int(11) DEFAULT 0,
  `stok_minimum` int(11) DEFAULT 0,
  `lokasi_rak` varchar(50) DEFAULT NULL,
  `harga_beli` decimal(15,2) DEFAULT NULL,
  `harga_jual` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `barcode` (`barcode`),
  UNIQUE KEY `sku` (`sku`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'BR001','BR001','Beras Ramos 25Kg','Beras','Sak',110,10,'A1',250000.00,270000.00),(3,'MY001','MY001','Minyak Goreng 1 Liter','Minyak','Dus',60,10,'A2',43000.00,45000.00),(4,'G001','G001','Gula Pasir 1Kg','Gula','pcs',24,10,'A1',12000.00,14000.00);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_order_details`
--

DROP TABLE IF EXISTS `purchase_order_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchase_order_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `purchase_order_id` int(11) DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `qty` int(11) DEFAULT NULL,
  `harga` decimal(15,2) DEFAULT NULL,
  `subtotal` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `purchase_order_id` (`purchase_order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `purchase_order_details_ibfk_1` FOREIGN KEY (`purchase_order_id`) REFERENCES `purchase_orders` (`id`),
  CONSTRAINT `purchase_order_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_order_details`
--

LOCK TABLES `purchase_order_details` WRITE;
/*!40000 ALTER TABLE `purchase_order_details` DISABLE KEYS */;
INSERT INTO `purchase_order_details` VALUES (1,1,1,10,250000.00,2500000.00),(2,1,3,10,43000.00,430000.00),(3,2,4,8,12000.00,96000.00),(4,2,1,10,250000.00,2500000.00),(5,4,4,10,12000.00,120000.00),(6,4,3,15,43000.00,645000.00),(7,7,4,15,12000.00,180000.00),(8,8,1,5,250000.00,1250000.00),(9,8,3,6,43000.00,258000.00),(10,8,4,3,12000.00,36000.00),(11,9,1,3,250000.00,750000.00),(12,9,3,5,43000.00,215000.00),(13,9,4,6,12000.00,72000.00);
/*!40000 ALTER TABLE `purchase_order_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_orders`
--

DROP TABLE IF EXISTS `purchase_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchase_orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nomor_po` varchar(50) DEFAULT NULL,
  `supplier_id` int(11) DEFAULT NULL,
  `tanggal` date DEFAULT NULL,
  `status` enum('draft','open','approved','received') DEFAULT 'draft',
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nomor_po` (`nomor_po`),
  KEY `supplier_id` (`supplier_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `purchase_orders_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  CONSTRAINT `purchase_orders_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_orders`
--

LOCK TABLES `purchase_orders` WRITE;
/*!40000 ALTER TABLE `purchase_orders` DISABLE KEYS */;
INSERT INTO `purchase_orders` VALUES (1,'PO-20260531',1,'2026-05-31','received',NULL),(2,'PO-20260601',3,'2026-06-01','received',NULL),(4,'PO-20260603-001',1,'2026-06-03','received',1),(5,'PO-20260605-5447',1,'2026-06-05','draft',1),(6,'PO-20260605-1981',1,'2026-06-05','draft',1),(7,'PO-20260605-2789',1,'2026-06-05','received',1),(8,'PO-20260605-2790',4,'2026-06-05','received',1),(9,'PO-20260605-2791',3,'2026-06-05','received',1);
/*!40000 ALTER TABLE `purchase_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_movements`
--

DROP TABLE IF EXISTS `stock_movements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_movements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tanggal` datetime DEFAULT current_timestamp(),
  `product_id` int(11) DEFAULT NULL,
  `jenis` enum('IN','OUT','OPNAME') DEFAULT NULL,
  `qty` int(11) DEFAULT NULL,
  `referensi` varchar(50) DEFAULT NULL,
  `keterangan` text DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `stock_movements_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `stock_movements_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_movements`
--

LOCK TABLES `stock_movements` WRITE;
/*!40000 ALTER TABLE `stock_movements` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_movements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_opname`
--

DROP TABLE IF EXISTS `stock_opname`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_opname` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tanggal` datetime DEFAULT current_timestamp(),
  `product_id` int(11) DEFAULT NULL,
  `stok_sistem` int(11) DEFAULT NULL,
  `stok_fisik` int(11) DEFAULT NULL,
  `selisih` int(11) DEFAULT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_opname`
--

LOCK TABLES `stock_opname` WRITE;
/*!40000 ALTER TABLE `stock_opname` DISABLE KEYS */;
INSERT INTO `stock_opname` VALUES (1,'2026-06-05 11:00:05',1,128,128,0,NULL,1);
/*!40000 ALTER TABLE `stock_opname` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suppliers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_supplier` varchar(200) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `telepon` varchar(30) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,'PT Sembako Jaya','Jakarta','08123456789','supplier@test.com'),(3,'PT Dunia Jaya',NULL,'08112345678','dunia_jaya1@gmail.com'),(4,'PT Argania',NULL,'08571234678','argania123@gmail.com');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction_history`
--

DROP TABLE IF EXISTS `transaction_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tanggal` datetime DEFAULT current_timestamp(),
  `jenis` enum('MASUK','KELUAR') DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `qty` int(11) DEFAULT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `transaction_history_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `transaction_history_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction_history`
--

LOCK TABLES `transaction_history` WRITE;
/*!40000 ALTER TABLE `transaction_history` DISABLE KEYS */;
INSERT INTO `transaction_history` VALUES (1,'2026-05-31 09:56:46','KELUAR',1,10,'Pengiriman Agen',1),(2,'2026-05-31 09:56:46','MASUK',1,30,'Barang Masuk',1),(3,'2026-05-31 10:36:10','KELUAR',1,42,'Pengiriman Agen',1),(4,'2026-05-31 10:36:48','KELUAR',3,42,'Pengiriman Agen',1),(5,'2026-05-31 10:37:16','MASUK',1,40,'Barang Masuk',1),(6,'2026-05-31 10:37:30','MASUK',3,40,'Barang Masuk',1),(7,'2026-06-01 16:13:35','MASUK',1,10,'Receive PO',1),(8,'2026-06-01 16:13:35','MASUK',3,10,'Receive PO',1),(9,'2026-06-01 16:14:26','MASUK',4,8,'Receive PO',1),(10,'2026-06-01 16:14:26','MASUK',1,10,'Receive PO',1),(11,'2026-06-03 14:26:44','MASUK',4,10,'Receive PO',1),(12,'2026-06-03 14:26:44','MASUK',3,15,'Receive PO',1),(13,'2026-06-04 10:38:00','KELUAR',1,5,'DO #2',1),(14,'2026-06-04 10:38:00','KELUAR',3,5,'DO #2',1),(15,'2026-06-05 11:00:05','',1,0,'Stock Opname',1),(16,'2026-06-05 17:51:51','KELUAR',1,20,'DO #1',1),(17,'2026-06-05 19:03:52','KELUAR',4,5,'DO #4',1),(18,'2026-06-05 19:12:37','MASUK',4,15,'Receive PO',1),(19,'2026-06-06 09:58:20','MASUK',1,3,'Receive PO',1),(20,'2026-06-06 09:58:20','MASUK',3,5,'Receive PO',1),(21,'2026-06-06 09:58:20','MASUK',4,6,'Receive PO',1),(22,'2026-06-06 09:58:37','MASUK',1,5,'Receive PO',1),(23,'2026-06-06 09:58:37','MASUK',3,6,'Receive PO',1),(24,'2026-06-06 09:58:37','MASUK',4,3,'Receive PO',1),(25,'2026-06-06 10:19:31','KELUAR',1,3,'DO #5',1),(26,'2026-06-06 10:19:31','KELUAR',4,4,'DO #5',1),(27,'2026-06-06 10:19:31','KELUAR',3,7,'DO #5',1);
/*!40000 ALTER TABLE `transaction_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `nama` varchar(100) DEFAULT NULL,
  `role` enum('admin','gudang','kasir','owner') DEFAULT NULL,
  `status` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','test123','Administrator','admin',1,'2026-05-30 10:25:38'),(2,'gudang','gudang123','Petugas Gudang','gudang',1,'2026-05-31 04:44:48'),(3,'kasir','kasir123','Kasir','kasir',1,'2026-05-31 04:44:48'),(4,'owner','owner123','Pemilik','owner',1,'2026-05-31 04:44:48');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-06 13:17:17
