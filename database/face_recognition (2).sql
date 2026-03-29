-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 27, 2026 at 11:38 PM
-- Server version: 5.7.36
-- PHP Version: 7.4.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `face_recognition`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
CREATE TABLE IF NOT EXISTS `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `full_name`, `email`, `password`, `image_path`) VALUES
(1, 'TUSUBIRACALEBU', 'tusubiracalebu@gmail.com', '1234567', 'admin_images\\admin_profile_1.jpeg'),
(2, 'cal evan', 'cal3@gmail.com', '1234567', 'admin_images\\admin_profile_2.jpeg'),
(3, 'skylar deal', 'sky@gmail.com', '1234567', 'admin_images\\admin_sky.jpeg');

-- --------------------------------------------------------

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
CREATE TABLE IF NOT EXISTS `announcements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `audience` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `announcements`
--

INSERT INTO `announcements` (`id`, `title`, `message`, `audience`, `created_at`) VALUES
(1, 'change exammination date', 'this is to inform you that there is a chang in th examination schedule', 'Students Only', '2026-03-04 03:53:17'),
(2, 'change the exam date', 'this is to inform you that there is a change in the exa,m starting time and we shall start next week', 'Students Only', '2026-03-04 03:58:03'),
(3, 'chanignnndhdjhfj', 'aaaaaaaaaaaaaaaaaaaaaaaaagggggggggggggggggggggggcccccccccccccccccc', 'Students Only', '2026-03-04 03:58:46'),
(4, 'calebu message', 'test mest test message', 'Students Only', '2026-03-04 04:27:38'),
(5, 'enock message', 'am tired this morning', 'Students Only', '2026-03-04 04:30:02'),
(6, 'calebu morning message', 'padlock', 'Students Only', '2026-03-04 04:34:40'),
(7, 'calebu message 111', 'testing testing', 'All Users', '2026-03-04 04:37:48'),
(8, 'val', 'val msasgdgd', 'All Users', '2026-03-04 04:49:59'),
(9, 'spcific person', 'r3r3rrttrrtr', 'Specific Student: 2023-08-16869', '2026-03-04 04:51:23'),
(10, 'calebu todat', 'this is nmy masseg', 'Students Only', '2026-03-05 00:59:11'),
(11, 'new', 'trrrthth', 'Students Only', '2026-03-05 01:13:29'),
(12, 'change exam date', 'thwdjhdjfgfj   wghwejdjdjdj', 'Students Only', '2026-03-05 02:44:59'),
(13, 'meeting', 'thsi  v dnwjj thstsbdnf fff', 'Students Only', '2026-03-06 11:41:00'),
(14, 'OUR MEETING', 'It is there tommoro', 'Students Only', '2026-03-25 12:06:16');

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
CREATE TABLE IF NOT EXISTS `attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reg_no` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `course` varchar(150) DEFAULT NULL,
  `program` varchar(100) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `date` date NOT NULL,
  `time_in` time NOT NULL,
  `time_out` time DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`id`, `reg_no`, `name`, `course`, `program`, `department`, `date`, `time_in`, `time_out`, `status`, `created_at`) VALUES
(1, '2023-08-16868', '2023-08-16868', 'Bcs', 'N/A', 'somac', '2026-03-04', '08:32:48', NULL, 'Present', '2026-03-04 05:32:48'),
(2, '2023-08-16868', '2023-08-16868', 'Bcs', 'N/A', 'somac', '2026-03-17', '21:59:05', NULL, 'Present', '2026-03-17 18:59:05'),
(3, '2023-08-16868', 'TUSUBIRA CALEBU', 'Bcs', 'N/A', 'somac', '2026-03-18', '12:17:26', NULL, 'Present', '2026-03-18 09:17:26'),
(4, '2024-08-28288', 'SSEBATA ENOCK', 'LLB', 'N/A', 'law', '2026-03-18', '12:24:32', NULL, 'Present', '2026-03-18 09:24:32'),
(5, '2023-08-16868', 'TUSUBIRA CALEBU', 'Bcs', 'Evening', 'somac', '2026-03-25', '11:44:34', NULL, 'Present', '2026-03-25 08:44:34'),
(6, '2024-08-16867', 'sky deal ', 'BBA', 'Day', 'BBA', '2026-03-25', '12:27:56', NULL, 'Present', '2026-03-25 09:27:56'),
(7, '2023-08-18840', 'KAYESU PHIONAH', 'BCS', 'EVENING', 'somac', '2026-03-25', '13:03:49', NULL, 'Present', '2026-03-25 10:03:49'),
(8, '2023-08-17666', 'TUMUSIIME ALEX', 'BCS', 'EVENING', 'SOMAC', '2026-03-25', '14:01:33', NULL, 'Present', '2026-03-25 11:01:33'),
(9, '2023-08-16868', 'TUSUBIRA CALEBU', 'Bcs', 'Day', 'somac', '2026-03-26', '10:34:23', NULL, 'Present', '2026-03-26 07:34:23'),
(10, '2024-08-16867', 'sky deal ', 'BBA', 'Day', 'BBA', '2026-03-26', '13:34:34', NULL, 'Present', '2026-03-26 10:34:34'),
(11, '2023-08-16868', 'TUSUBIRA CALEBU', 'Bcs', 'Day', 'somac', '2026-03-27', '16:57:32', NULL, 'Present', '2026-03-27 13:57:32'),
(12, '2024-08-28288', 'Ssebata Enock', 'Law', 'Day', 'Law', '2026-03-27', '23:47:59', NULL, 'Present', '2026-03-27 20:47:59'),
(13, '2024-08-28288', 'Ssebata Enock', 'Law', 'Day', 'Law', '2026-03-28', '00:00:47', NULL, 'Present', '2026-03-27 21:00:47'),
(14, '2023-08-16868', 'TUSUBIRA CALEBU', 'Bcs', 'Day', 'somac', '2026-03-28', '00:01:24', NULL, 'Present', '2026-03-27 21:01:24');

-- --------------------------------------------------------

--
-- Table structure for table `attendance_archives`
--

DROP TABLE IF EXISTS `attendance_archives`;
CREATE TABLE IF NOT EXISTS `attendance_archives` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `category` varchar(50) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `attendance_archives`
--

INSERT INTO `attendance_archives` (`id`, `filename`, `date`, `category`, `file_path`, `created_at`) VALUES
(1, 'Present_2026-03-27.xlsx', '2026-03-27', 'Present', 'attendance_history\\Present_2026-03-27.xlsx', '2026-03-27 19:32:23'),
(2, 'Absent_2026-03-27.xlsx', '2026-03-27', 'Absent', 'attendance_history\\Absent_2026-03-27.xlsx', '2026-03-27 19:32:25'),
(3, 'Present_2026-03-28.xlsx', '2026-03-28', 'Present', 'attendance_history\\Present_2026-03-28.xlsx', '2026-03-27 21:00:00'),
(4, 'Absent_2026-03-28.xlsx', '2026-03-28', 'Absent', 'attendance_history\\Absent_2026-03-28.xlsx', '2026-03-27 21:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
CREATE TABLE IF NOT EXISTS `students` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) NOT NULL,
  `registration_no` varchar(50) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `confirm_password` varchar(255) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `year_level` varchar(50) DEFAULT NULL,
  `course` varchar(150) DEFAULT NULL,
  `session` varchar(100) DEFAULT NULL,
  `contact_number` varchar(25) DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_no` (`registration_no`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `full_name`, `registration_no`, `email`, `password`, `confirm_password`, `department`, `year_level`, `course`, `session`, `contact_number`, `image_path`, `created_at`) VALUES
(1, 'TUSUBIRA CALEBU', '2023-08-16868', 'tusubiracalebu77@gmail.com', '1234567', '123456', 'somac', '3', 'Bcs', 'Day', '0745907221', 'students_images\\2023_08_16868.jpeg', '2026-02-27 19:51:06'),
(2, 'TUSUBIRA CALEBU', '2023-08-16869', 'tusubiracalebu@gmail.com', '123456789', '123456789', 'somac', '3', 'BCS', 'EVNING', '0745907220', 'students_images\\2023_08_16869.jpeg', '2026-03-04 01:29:23'),
(3, 'TUSUBIRA CALEBU', '2023-08-16867', 'tusubiracalebu70@gmail.com', '12345678', '12345678', 'somac', '3', 'BCS', 'EVENING', '0745907220', 'students_images\\2023_08_16867.jpeg', '2026-03-04 01:52:27'),
(4, 'emma muwa', '2023-08-16860', 'emma12@gmail.com', '123456', '123456', 'somac', '2', 'BCS', 'evening', '0734568965', 'students_images\\2023_08_16860.png', '2026-03-05 01:49:19'),
(10, 'Ssebata Enock', '2024-08-28288', 'enock@gmail.com', '1234567', '1234567', 'Law', '2', 'Law', 'Day', '0785007007', 'students_images\\2024_08_28288.jpeg', '2026-03-27 20:46:11'),
(6, 'sky deal ', '2024-08-16867', 'skylar@gmail.com', '1234567', '1234567', 'BBA', '2', 'BBA', 'Day', '0785007007', 'students_images\\2024_08_16867.jpeg', '2026-03-25 08:53:14'),
(7, 'KAYESU PHIONAH', '2023-08-18840', 'kayesuphionah@gmail.com', '1234567', '1234567', 'somac', '3', 'BCS', 'EVENING', '0745907220', 'students_images\\2023_08_18840.jpeg', '2026-03-25 09:59:15'),
(8, 'TUMUSIIME ALEX', '2023-08-17666', 'tumusiime@gmail.com', '1234567', '1234567', 'SOMAC', '3', 'BCS', 'EVENING', '0745907220', 'students_images\\2023_08_17666.jpeg', '2026-03-25 11:00:00'),
(9, 'NAGUDHI MARIAM', '2023-08-12345', 'mariam@gmail.com', '1234567', '1234567', 'SOMAC', '3', 'BIT', 'EVENING', '0745907221', 'students_images\\2023_08_12345.jpeg', '2026-03-25 12:04:45');

-- --------------------------------------------------------

--
-- Table structure for table `student_read_announcements`
--

DROP TABLE IF EXISTS `student_read_announcements`;
CREATE TABLE IF NOT EXISTS `student_read_announcements` (
  `student_reg_no` varchar(50) NOT NULL,
  `announcement_id` int(11) NOT NULL,
  `action` varchar(20) DEFAULT 'deleted',
  `action_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`student_reg_no`,`announcement_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `student_read_announcements`
--

INSERT INTO `student_read_announcements` (`student_reg_no`, `announcement_id`, `action`, `action_time`) VALUES
('2023-08-16868', 8, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 7, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 6, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 5, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 4, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 3, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 2, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 1, 'deleted', '2026-03-04 04:53:16'),
('2023-08-16868', 10, 'deleted', '2026-03-05 01:14:15'),
('2023-08-16868', 11, 'deleted', '2026-03-05 02:45:51'),
('2023-08-16868', 12, 'deleted', '2026-03-06 11:38:50'),
('2023-08-12345', 14, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 13, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 12, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 11, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 10, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 8, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 7, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 6, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 5, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 4, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 3, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 2, 'deleted', '2026-03-25 12:07:37'),
('2023-08-12345', 1, 'deleted', '2026-03-25 12:07:37');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
