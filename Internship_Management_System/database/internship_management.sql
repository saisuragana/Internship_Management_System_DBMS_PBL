-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: internship_management
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application` (
  `application_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `opportunity_id` int NOT NULL,
  `application_date` date NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Applied',
  PRIMARY KEY (`application_id`),
  UNIQUE KEY `student_id` (`student_id`,`opportunity_id`),
  KEY `opportunity_id` (`opportunity_id`),
  CONSTRAINT `application_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `application_ibfk_2` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunity` (`opportunity_id`),
  CONSTRAINT `application_chk_1` CHECK ((`status` in (_utf8mb4'Applied',_utf8mb4'Shortlisted',_utf8mb4'Rejected',_utf8mb4'Approved')))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
INSERT INTO `application` VALUES (1,1,1,'2026-05-20','Approved'),(2,2,3,'2026-05-21','Shortlisted'),(3,3,4,'2026-05-22','Applied'),(4,4,5,'2026-05-23','Approved'),(5,5,2,'2026-05-24','Rejected'),(6,1,3,'2026-05-25','Shortlisted'),(7,2,5,'2026-05-26','Applied');
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `approval`
--

DROP TABLE IF EXISTS `approval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `approval` (
  `approval_id` int NOT NULL AUTO_INCREMENT,
  `application_id` int NOT NULL,
  `approval_date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`approval_id`),
  UNIQUE KEY `application_id` (`application_id`),
  CONSTRAINT `approval_ibfk_1` FOREIGN KEY (`application_id`) REFERENCES `application` (`application_id`),
  CONSTRAINT `approval_chk_1` CHECK ((`status` in (_utf8mb4'Approved',_utf8mb4'Rejected',_utf8mb4'Pending')))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `approval`
--

LOCK TABLES `approval` WRITE;
/*!40000 ALTER TABLE `approval` DISABLE KEYS */;
INSERT INTO `approval` VALUES (1,1,'2026-05-22','Approved','Application approved for internship.'),(2,4,'2026-05-25','Approved','Selected for AI/ML internship.'),(3,5,'2026-05-27','Rejected','Position requirements not matched.'),(4,2,'2026-05-28','Pending','Awaiting final review.');
/*!40000 ALTER TABLE `approval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assignment`
--

DROP TABLE IF EXISTS `assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment` (
  `assignment_id` int NOT NULL AUTO_INCREMENT,
  `application_id` int NOT NULL,
  `mentor_id` int NOT NULL,
  `supervisor_id` int NOT NULL,
  `assigned_date` date NOT NULL,
  PRIMARY KEY (`assignment_id`),
  UNIQUE KEY `application_id` (`application_id`),
  KEY `mentor_id` (`mentor_id`),
  KEY `supervisor_id` (`supervisor_id`),
  CONSTRAINT `assignment_ibfk_1` FOREIGN KEY (`application_id`) REFERENCES `application` (`application_id`),
  CONSTRAINT `assignment_ibfk_2` FOREIGN KEY (`mentor_id`) REFERENCES `faculty_mentor` (`mentor_id`),
  CONSTRAINT `assignment_ibfk_3` FOREIGN KEY (`supervisor_id`) REFERENCES `company_supervisor` (`supervisor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assignment`
--

LOCK TABLES `assignment` WRITE;
/*!40000 ALTER TABLE `assignment` DISABLE KEYS */;
INSERT INTO `assignment` VALUES (1,1,1,1,'2026-05-25'),(2,4,2,4,'2026-05-28');
/*!40000 ALTER TABLE `assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificate`
--

DROP TABLE IF EXISTS `certificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificate` (
  `certificate_id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int NOT NULL,
  `certificate_no` varchar(50) NOT NULL,
  `issue_date` date NOT NULL,
  PRIMARY KEY (`certificate_id`),
  UNIQUE KEY `assignment_id` (`assignment_id`),
  UNIQUE KEY `certificate_no` (`certificate_no`),
  CONSTRAINT `certificate_ibfk_1` FOREIGN KEY (`assignment_id`) REFERENCES `assignment` (`assignment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificate`
--

LOCK TABLES `certificate` WRITE;
/*!40000 ALTER TABLE `certificate` DISABLE KEYS */;
INSERT INTO `certificate` VALUES (1,1,'CERT-2026-001','2026-08-05'),(2,2,'CERT-2026-002','2026-08-10');
/*!40000 ALTER TABLE `certificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company_supervisor`
--

DROP TABLE IF EXISTS `company_supervisor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_supervisor` (
  `supervisor_id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`supervisor_id`),
  UNIQUE KEY `email` (`email`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `company_supervisor_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organization` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_supervisor`
--

LOCK TABLES `company_supervisor` WRITE;
/*!40000 ALTER TABLE `company_supervisor` DISABLE KEYS */;
INSERT INTO `company_supervisor` VALUES (1,1,'Vikram Singh','vikram@technova.com','9100000001'),(2,2,'Neha Kapoor','neha@datasphere.com','9100000002'),(3,3,'Rohit Mehta','rohit@cloudmatrix.com','9100000003'),(4,4,'Ananya Iyer','ananya@innovatex.com','9100000004');
/*!40000 ALTER TABLE `company_supervisor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluation`
--

DROP TABLE IF EXISTS `evaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluation` (
  `evaluation_id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int NOT NULL,
  `evaluator_type` varchar(20) NOT NULL,
  `score` decimal(5,2) NOT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`evaluation_id`),
  KEY `assignment_id` (`assignment_id`),
  CONSTRAINT `evaluation_ibfk_1` FOREIGN KEY (`assignment_id`) REFERENCES `assignment` (`assignment_id`),
  CONSTRAINT `evaluation_chk_1` CHECK ((`evaluator_type` in (_utf8mb4'Faculty',_utf8mb4'Company'))),
  CONSTRAINT `evaluation_chk_2` CHECK ((`score` between 0 and 100))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluation`
--

LOCK TABLES `evaluation` WRITE;
/*!40000 ALTER TABLE `evaluation` DISABLE KEYS */;
INSERT INTO `evaluation` VALUES (1,1,'Faculty',88.00,'Good technical progress and documentation.'),(2,1,'Company',92.00,'Strong development skills and consistent performance.'),(3,2,'Faculty',85.00,'Good understanding of machine learning concepts.'),(4,2,'Company',89.00,'Completed assigned tasks effectively.');
/*!40000 ALTER TABLE `evaluation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty_mentor`
--

DROP TABLE IF EXISTS `faculty_mentor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty_mentor` (
  `mentor_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `department` varchar(100) NOT NULL,
  PRIMARY KEY (`mentor_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty_mentor`
--

LOCK TABLES `faculty_mentor` WRITE;
/*!40000 ALTER TABLE `faculty_mentor` DISABLE KEYS */;
INSERT INTO `faculty_mentor` VALUES (1,'Dr. Anil Kumar','anil.kumar@university.edu','CSE'),(2,'Dr. Meena Rao','meena.rao@university.edu','AIML'),(3,'Dr. Ravi Teja','ravi.teja@university.edu','CSE');
/*!40000 ALTER TABLE `faculty_mentor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `feedback_id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int NOT NULL,
  `rating` int NOT NULL,
  `comments` varchar(500) DEFAULT NULL,
  `feedback_date` date NOT NULL,
  PRIMARY KEY (`feedback_id`),
  KEY `assignment_id` (`assignment_id`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`assignment_id`) REFERENCES `assignment` (`assignment_id`),
  CONSTRAINT `feedback_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,1,5,'Excellent internship experience with strong technical exposure.','2026-08-05'),(2,2,4,'Good learning experience and supportive supervision.','2026-08-10'),(3,1,5,'Excellent internship experience with strong technical exposure.','2026-08-05'),(4,2,4,'Good learning experience and supportive supervision.','2026-08-10'),(5,1,5,'Excellent internship experience with strong technical exposure.','2026-08-05'),(6,2,4,'Good learning experience and supportive supervision.','2026-08-10');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opportunity`
--

DROP TABLE IF EXISTS `opportunity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunity` (
  `opportunity_id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `title` varchar(150) NOT NULL,
  `description` text,
  `location` varchar(150) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `available_slots` int NOT NULL,
  PRIMARY KEY (`opportunity_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `opportunity_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organization` (`organization_id`),
  CONSTRAINT `opportunity_chk_1` CHECK ((`end_date` >= `start_date`)),
  CONSTRAINT `opportunity_chk_2` CHECK ((`available_slots` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opportunity`
--

LOCK TABLES `opportunity` WRITE;
/*!40000 ALTER TABLE `opportunity` DISABLE KEYS */;
INSERT INTO `opportunity` VALUES (1,1,'Python Developer Intern','Work on Python-based application development.','Hyderabad','2026-06-01','2026-07-31',5),(2,1,'Web Development Intern','Develop and maintain web applications.','Hyderabad','2026-06-15','2026-08-15',4),(3,2,'Data Analyst Intern','Analyze datasets and create business insights.','Bengaluru','2026-06-01','2026-07-31',3),(4,3,'Cloud Engineering Intern','Work with cloud infrastructure and deployment.','Pune','2026-06-15','2026-08-15',4),(5,4,'AI/ML Intern','Build and evaluate machine learning models.','Chennai','2026-07-01','2026-08-31',3);
/*!40000 ALTER TABLE `opportunity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organization`
--

DROP TABLE IF EXISTS `organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organization` (
  `organization_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`organization_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organization`
--

LOCK TABLES `organization` WRITE;
/*!40000 ALTER TABLE `organization` DISABLE KEYS */;
INSERT INTO `organization` VALUES (1,'TechNova Solutions','Hyderabad, Telangana','hr@technova.com','9000000001'),(2,'DataSphere Analytics','Bengaluru, Karnataka','careers@datasphere.com','9000000002'),(3,'CloudMatrix Technologies','Pune, Maharashtra','hr@cloudmatrix.com','9000000003'),(4,'InnovateX Labs','Chennai, Tamil Nadu','careers@innovatex.com','9000000004');
/*!40000 ALTER TABLE `organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `year` int NOT NULL,
  `password` varchar(100) NOT NULL DEFAULT 'student123',
  `password_hash` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `student_chk_1` CHECK ((`year` between 1 and 4))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (1,'Rahul Sharma','rahul.sharma@university.edu','9876543210','CSE',3,'student123',NULL),(2,'Priya Reddy','priya.reddy@university.edu','9876543211','AIML',3,'student123',NULL),(3,'Arjun Kumar','arjun.kumar@university.edu','9876543212','CSE',4,'student123',NULL),(4,'Sneha Rao','sneha.rao@university.edu','9876543213','AIML',2,'student123',NULL),(5,'Kiran Varma','kiran.varma@university.edu','9876543214','CSE',3,'student123',NULL),(6,'dattu suragana','suraganadattu073@gmail.com','9553407407','CSE',1,'student123','scrypt:32768:8:1$UVdl9GoB5zShu9pz$3d35c140d2d63c7eff9bf4e72a3b7155b40fde22ec9f337d261988352f5e31280e07442107e70999cc9b16df08a2c753955a3fdd50bfef83020974e848eb3058');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weekly_log`
--

DROP TABLE IF EXISTS `weekly_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weekly_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int NOT NULL,
  `week_no` int NOT NULL,
  `log_date` date NOT NULL,
  `activities` text NOT NULL,
  `hours` decimal(5,2) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Submitted',
  PRIMARY KEY (`log_id`),
  UNIQUE KEY `assignment_id` (`assignment_id`,`week_no`),
  CONSTRAINT `weekly_log_ibfk_1` FOREIGN KEY (`assignment_id`) REFERENCES `assignment` (`assignment_id`),
  CONSTRAINT `weekly_log_chk_1` CHECK ((`week_no` > 0)),
  CONSTRAINT `weekly_log_chk_2` CHECK ((`hours` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weekly_log`
--

LOCK TABLES `weekly_log` WRITE;
/*!40000 ALTER TABLE `weekly_log` DISABLE KEYS */;
INSERT INTO `weekly_log` VALUES (1,1,1,'2026-06-05','Completed Python environment setup and studied project requirements.',35.00,'Submitted'),(2,1,2,'2026-06-12','Implemented backend modules and completed database integration.',38.00,'Submitted'),(3,1,3,'2026-06-19','Developed REST APIs and performed unit testing.',40.00,'Submitted'),(4,2,1,'2026-06-05','Studied machine learning dataset and performed preprocessing.',32.00,'Submitted'),(5,2,2,'2026-06-12','Implemented initial ML model and evaluated results.',36.00,'Submitted');
/*!40000 ALTER TABLE `weekly_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-20 11:09:16
