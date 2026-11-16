-- =====================================================================
-- Hotel Ríos del Sur - base de datos para XAMPP (phpMyAdmin)
-- Versión limpia: sin datos de prueba/broma.
-- Generado con Django 5.0.14 (compatible con MariaDB 10.4 de XAMPP)
-- Crea la base hotel_rios_del_sur (utf8mb4_unicode_ci), todas las tablas
-- y los datos: 4 tipos, 10 habitaciones, 3 huéspedes, 5 reservas,
-- 3 usuarios (admin, recepcion, cliente) y grupos/permisos.
-- Importar desde phpMyAdmin > Importar (sin seleccionar ninguna base).
-- =====================================================================

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

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hotel_rios_del_sur` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `hotel_rios_del_sur`;
DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (2,'Cliente');
INSERT INTO `auth_group` VALUES (1,'Recepcion');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry');
INSERT INTO `auth_permission` VALUES (2,'Can change log entry',1,'change_logentry');
INSERT INTO `auth_permission` VALUES (3,'Can delete log entry',1,'delete_logentry');
INSERT INTO `auth_permission` VALUES (4,'Can view log entry',1,'view_logentry');
INSERT INTO `auth_permission` VALUES (5,'Can add permission',2,'add_permission');
INSERT INTO `auth_permission` VALUES (6,'Can change permission',2,'change_permission');
INSERT INTO `auth_permission` VALUES (7,'Can delete permission',2,'delete_permission');
INSERT INTO `auth_permission` VALUES (8,'Can view permission',2,'view_permission');
INSERT INTO `auth_permission` VALUES (9,'Can add group',3,'add_group');
INSERT INTO `auth_permission` VALUES (10,'Can change group',3,'change_group');
INSERT INTO `auth_permission` VALUES (11,'Can delete group',3,'delete_group');
INSERT INTO `auth_permission` VALUES (12,'Can view group',3,'view_group');
INSERT INTO `auth_permission` VALUES (13,'Can add user',4,'add_user');
INSERT INTO `auth_permission` VALUES (14,'Can change user',4,'change_user');
INSERT INTO `auth_permission` VALUES (15,'Can delete user',4,'delete_user');
INSERT INTO `auth_permission` VALUES (16,'Can view user',4,'view_user');
INSERT INTO `auth_permission` VALUES (17,'Can add content type',5,'add_contenttype');
INSERT INTO `auth_permission` VALUES (18,'Can change content type',5,'change_contenttype');
INSERT INTO `auth_permission` VALUES (19,'Can delete content type',5,'delete_contenttype');
INSERT INTO `auth_permission` VALUES (20,'Can view content type',5,'view_contenttype');
INSERT INTO `auth_permission` VALUES (21,'Can add session',6,'add_session');
INSERT INTO `auth_permission` VALUES (22,'Can change session',6,'change_session');
INSERT INTO `auth_permission` VALUES (23,'Can delete session',6,'delete_session');
INSERT INTO `auth_permission` VALUES (24,'Can view session',6,'view_session');
INSERT INTO `auth_permission` VALUES (25,'Can add habitación',7,'add_habitacion');
INSERT INTO `auth_permission` VALUES (26,'Can change habitación',7,'change_habitacion');
INSERT INTO `auth_permission` VALUES (27,'Can delete habitación',7,'delete_habitacion');
INSERT INTO `auth_permission` VALUES (28,'Can view habitación',7,'view_habitacion');
INSERT INTO `auth_permission` VALUES (29,'Can add tipo de habitación',8,'add_tipohabitacion');
INSERT INTO `auth_permission` VALUES (30,'Can change tipo de habitación',8,'change_tipohabitacion');
INSERT INTO `auth_permission` VALUES (31,'Can delete tipo de habitación',8,'delete_tipohabitacion');
INSERT INTO `auth_permission` VALUES (32,'Can view tipo de habitación',8,'view_tipohabitacion');
INSERT INTO `auth_permission` VALUES (33,'Can add huésped',9,'add_huesped');
INSERT INTO `auth_permission` VALUES (34,'Can change huésped',9,'change_huesped');
INSERT INTO `auth_permission` VALUES (35,'Can delete huésped',9,'delete_huesped');
INSERT INTO `auth_permission` VALUES (36,'Can view huésped',9,'view_huesped');
INSERT INTO `auth_permission` VALUES (37,'Can add reserva',10,'add_reserva');
INSERT INTO `auth_permission` VALUES (38,'Can change reserva',10,'change_reserva');
INSERT INTO `auth_permission` VALUES (39,'Can delete reserva',10,'delete_reserva');
INSERT INTO `auth_permission` VALUES (40,'Can view reserva',10,'view_reserva');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$720000$OJeBkvUT9gYiLflbKErsw0$RPAfiL/ObzUC5Zvb1qH8mGyVnRvpXRhay/GbqVHO4g8=',NULL,1,'admin','Administrador','Hotel','',1,1,'2026-11-01 20:20:52.599000');
INSERT INTO `auth_user` VALUES (2,'pbkdf2_sha256$720000$XUztY6QF5SCcF2rCbmHhRg$K5VaP+u1XVVDigYyiF34LDmMTfvGSKankLje8uW796g=','2026-11-13 19:51:13.999000',0,'recepcion','Marta','Rivas','',0,1,'2026-11-01 20:20:53.347000');
INSERT INTO `auth_user` VALUES (3,'pbkdf2_sha256$720000$BbB9S1gQVHwyW4q3TmEc4U$ny1PhGpLuWisNOGtByJQJVgJ5a+hMgubTQXOaD86zCU=','2026-11-13 21:23:31.793000',0,'cliente','Juan','Pérez','',0,1,'2026-11-01 20:20:54.084000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (1,2,1);
INSERT INTO `auth_user_groups` VALUES (2,3,2);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry');
INSERT INTO `django_content_type` VALUES (3,'auth','group');
INSERT INTO `django_content_type` VALUES (2,'auth','permission');
INSERT INTO `django_content_type` VALUES (4,'auth','user');
INSERT INTO `django_content_type` VALUES (5,'contenttypes','contenttype');
INSERT INTO `django_content_type` VALUES (7,'hotel','habitacion');
INSERT INTO `django_content_type` VALUES (9,'hotel','huesped');
INSERT INTO `django_content_type` VALUES (10,'hotel','reserva');
INSERT INTO `django_content_type` VALUES (8,'hotel','tipohabitacion');
INSERT INTO `django_content_type` VALUES (6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-11-14 02:23:12.707166');
INSERT INTO `django_migrations` VALUES (2,'auth','0001_initial','2026-11-14 02:23:12.784787');
INSERT INTO `django_migrations` VALUES (3,'admin','0001_initial','2026-11-14 02:23:12.804912');
INSERT INTO `django_migrations` VALUES (4,'admin','0002_logentry_remove_auto_add','2026-11-14 02:23:12.809818');
INSERT INTO `django_migrations` VALUES (5,'admin','0003_logentry_add_action_flag_choices','2026-11-14 02:23:12.814885');
INSERT INTO `django_migrations` VALUES (6,'contenttypes','0002_remove_content_type_name','2026-11-14 02:23:12.837001');
INSERT INTO `django_migrations` VALUES (7,'auth','0002_alter_permission_name_max_length','2026-11-14 02:23:12.847811');
INSERT INTO `django_migrations` VALUES (8,'auth','0003_alter_user_email_max_length','2026-11-14 02:23:12.856547');
INSERT INTO `django_migrations` VALUES (9,'auth','0004_alter_user_username_opts','2026-11-14 02:23:12.860808');
INSERT INTO `django_migrations` VALUES (10,'auth','0005_alter_user_last_login_null','2026-11-14 02:23:12.873327');
INSERT INTO `django_migrations` VALUES (11,'auth','0006_require_contenttypes_0002','2026-11-14 02:23:12.874424');
INSERT INTO `django_migrations` VALUES (12,'auth','0007_alter_validators_add_error_messages','2026-11-14 02:23:12.878721');
INSERT INTO `django_migrations` VALUES (13,'auth','0008_alter_user_username_max_length','2026-11-14 02:23:12.889395');
INSERT INTO `django_migrations` VALUES (14,'auth','0009_alter_user_last_name_max_length','2026-11-14 02:23:12.902999');
INSERT INTO `django_migrations` VALUES (15,'auth','0010_alter_group_name_max_length','2026-11-14 02:23:12.913701');
INSERT INTO `django_migrations` VALUES (16,'auth','0011_update_proxy_permissions','2026-11-14 02:23:12.918906');
INSERT INTO `django_migrations` VALUES (17,'auth','0012_alter_user_first_name_max_length','2026-11-14 02:23:12.928195');
INSERT INTO `django_migrations` VALUES (18,'hotel','0001_initial','2026-11-14 02:23:13.001930');
INSERT INTO `django_migrations` VALUES (19,'hotel','0002_alter_huesped_nacionalidad','2026-11-14 02:23:13.015961');
INSERT INTO `django_migrations` VALUES (20,'sessions','0001_initial','2026-11-14 02:23:13.026058');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `hotel_habitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_habitacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `numero` varchar(10) NOT NULL,
  `piso` smallint(5) unsigned NOT NULL CHECK (`piso` >= 0),
  `servicios` varchar(255) NOT NULL,
  `estado` varchar(12) NOT NULL,
  `tipo_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero` (`numero`),
  KEY `hotel_habitacion_tipo_id_f61fe7bb_fk_hotel_tipohabitacion_id` (`tipo_id`),
  CONSTRAINT `hotel_habitacion_tipo_id_f61fe7bb_fk_hotel_tipohabitacion_id` FOREIGN KEY (`tipo_id`) REFERENCES `hotel_tipohabitacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `hotel_habitacion` WRITE;
/*!40000 ALTER TABLE `hotel_habitacion` DISABLE KEYS */;
INSERT INTO `hotel_habitacion` VALUES (1,'101',1,'Wi-Fi, TV, baño privado','disponible',1);
INSERT INTO `hotel_habitacion` VALUES (2,'102',1,'Wi-Fi, TV, baño privado','disponible',2);
INSERT INTO `hotel_habitacion` VALUES (3,'103',1,'Wi-Fi, TV, baño privado, acceso para silla de ruedas','disponible',2);
INSERT INTO `hotel_habitacion` VALUES (4,'104',1,'Wi-Fi, TV, baño privado','limpieza',1);
INSERT INTO `hotel_habitacion` VALUES (5,'201',2,'Wi-Fi, TV, baño privado, vista al río','ocupada',2);
INSERT INTO `hotel_habitacion` VALUES (6,'202',2,'Wi-Fi, TV, baño privado, frigobar','disponible',3);
INSERT INTO `hotel_habitacion` VALUES (7,'203',2,'Wi-Fi, TV, baño privado, frigobar','disponible',3);
INSERT INTO `hotel_habitacion` VALUES (8,'204',2,'Wi-Fi, TV, baño privado','mantencion',2);
INSERT INTO `hotel_habitacion` VALUES (9,'301',3,'Wi-Fi, Smart TV, tina, frigobar, vista al río','disponible',4);
INSERT INTO `hotel_habitacion` VALUES (10,'302',3,'Wi-Fi, Smart TV, tina, frigobar, vista al río','disponible',4);
/*!40000 ALTER TABLE `hotel_habitacion` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `hotel_huesped`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_huesped` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo_documento` varchar(10) NOT NULL,
  `numero_documento` varchar(20) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `correo` varchar(254) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `nacionalidad` varchar(30) NOT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `huesped_documento_unico` (`tipo_documento`,`numero_documento`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `hotel_huesped_usuario_id_10300eba_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `hotel_huesped` WRITE;
/*!40000 ALTER TABLE `hotel_huesped` DISABLE KEYS */;
INSERT INTO `hotel_huesped` VALUES (1,'rut','12345678-5','Juan','Pérez Soto','juan.perez@example.com','+56 9 1234 5678','Chilena','2026-11-01 20:20:54.819000',3);
INSERT INTO `hotel_huesped` VALUES (2,'rut','11111111-1','María','González Rojas','maria.gonzalez@example.com','+56 9 8765 4321','Chilena','2026-11-01 20:20:54.820000',NULL);
INSERT INTO `hotel_huesped` VALUES (3,'pasaporte','X1234567','John','Smith','john.smith@example.com','','Estadounidense','2026-11-01 20:20:54.821000',NULL);
/*!40000 ALTER TABLE `hotel_huesped` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `hotel_reserva`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_reserva` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(12) NOT NULL,
  `fecha_entrada` date NOT NULL,
  `fecha_salida` date NOT NULL,
  `cantidad_personas` smallint(5) unsigned NOT NULL CHECK (`cantidad_personas` >= 0),
  `estado` varchar(12) NOT NULL,
  `precio_noche` int(10) unsigned NOT NULL CHECK (`precio_noche` >= 0),
  `observaciones` longtext NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `checkin_en` datetime(6) DEFAULT NULL,
  `checkout_en` datetime(6) DEFAULT NULL,
  `cancelada_en` datetime(6) DEFAULT NULL,
  `creada_por_id` int(11) DEFAULT NULL,
  `habitacion_id` bigint(20) NOT NULL,
  `huesped_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `hotel_reserva_creada_por_id_fff00ccb_fk_auth_user_id` (`creada_por_id`),
  KEY `hotel_reserva_habitacion_id_57d35d0a_fk_hotel_habitacion_id` (`habitacion_id`),
  KEY `hotel_reserva_huesped_id_52c9ba75_fk_hotel_huesped_id` (`huesped_id`),
  CONSTRAINT `hotel_reserva_creada_por_id_fff00ccb_fk_auth_user_id` FOREIGN KEY (`creada_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `hotel_reserva_habitacion_id_57d35d0a_fk_hotel_habitacion_id` FOREIGN KEY (`habitacion_id`) REFERENCES `hotel_habitacion` (`id`),
  CONSTRAINT `hotel_reserva_huesped_id_52c9ba75_fk_hotel_huesped_id` FOREIGN KEY (`huesped_id`) REFERENCES `hotel_huesped` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `hotel_reserva` WRITE;
/*!40000 ALTER TABLE `hotel_reserva` DISABLE KEYS */;
INSERT INTO `hotel_reserva` VALUES (1,'RS-A78D766E','2026-10-31','2026-11-03',2,'en_curso',65000,'','2026-11-01 20:20:54.843000','2026-10-31 20:20:54.843000',NULL,NULL,NULL,5,2);
INSERT INTO `hotel_reserva` VALUES (2,'RS-314E50FD','2026-11-01','2026-11-04',2,'confirmada',65000,'','2026-11-01 20:20:54.844000',NULL,NULL,NULL,NULL,2,3);
INSERT INTO `hotel_reserva` VALUES (3,'RS-69D6D157','2026-11-08','2026-11-11',2,'pendiente',120000,'','2026-11-01 20:20:54.844000',NULL,NULL,NULL,NULL,9,1);
INSERT INTO `hotel_reserva` VALUES (4,'RS-EBA95CBB','2026-10-02','2026-10-05',3,'finalizada',95000,'','2026-11-01 20:20:54.845000',NULL,NULL,NULL,NULL,6,1);
INSERT INTO `hotel_reserva` VALUES (5,'RS-60A58700','2026-11-15','2026-11-17',1,'cancelada',120000,'','2026-11-01 20:20:54.845000',NULL,NULL,NULL,NULL,10,2);
/*!40000 ALTER TABLE `hotel_reserva` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `hotel_tipohabitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_tipohabitacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` longtext NOT NULL,
  `capacidad` smallint(5) unsigned NOT NULL CHECK (`capacidad` >= 0),
  `precio_noche` int(10) unsigned NOT NULL CHECK (`precio_noche` >= 0),
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `hotel_tipohabitacion` WRITE;
/*!40000 ALTER TABLE `hotel_tipohabitacion` DISABLE KEYS */;
INSERT INTO `hotel_tipohabitacion` VALUES (1,'Simple','Cama de 1 plaza y media, ideal para viajes de trabajo.',1,45000);
INSERT INTO `hotel_tipohabitacion` VALUES (2,'Doble','Cama de 2 plazas o dos camas de 1 plaza.',2,65000);
INSERT INTO `hotel_tipohabitacion` VALUES (3,'Familiar','Cama de 2 plazas y dos camas de 1 plaza.',4,95000);
INSERT INTO `hotel_tipohabitacion` VALUES (4,'Suite','Cama King, living y tina, con vista al río.',2,120000);
/*!40000 ALTER TABLE `hotel_tipohabitacion` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

