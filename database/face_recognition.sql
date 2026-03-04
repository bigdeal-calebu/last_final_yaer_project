-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 04, 2026 at 05:38 AM
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
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `full_name`, `email`, `password`, `image_path`) VALUES
(1, 'TUSUBIRACALEBU', 'tusubiracalebu@gmail.com', '1234567', NULL);

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
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

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
(9, 'spcific person', 'r3r3rrttrrtr', 'Specific Student: 2023-08-16869', '2026-03-04 04:51:23');

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
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`id`, `reg_no`, `name`, `course`, `program`, `department`, `date`, `time_in`, `time_out`, `status`, `created_at`) VALUES
(1, '2023-08-16868', '2023-08-16868', 'Bcs', 'N/A', 'somac', '2026-03-04', '08:32:48', NULL, 'Present', '2026-03-04 05:32:48');

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
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `full_name`, `registration_no`, `email`, `password`, `confirm_password`, `department`, `year_level`, `course`, `session`, `contact_number`, `image_path`, `created_at`) VALUES
(1, 'TUSUBIRA CALEBU', '2023-08-16868', 'tusubiracalebu77@gmail.com', '1234567', '123456', 'somac', '3', 'Bcs', 'Evening', '0745907221', 'students_images\\2023_08_16868.jpeg', '2026-02-27 19:51:06'),
(2, 'TUSUBIRA CALEBU', '2023-08-16869', 'tusubiracalebu@gmail.com', '123456789', '123456789', 'somac', '3', 'BCS', 'EVNING', '0745907220', 'students_images\\2023_08_16869.jpeg', '2026-03-04 01:29:23'),
(3, 'TUSUBIRA CALEBU', '2023-08-16867', 'tusubiracalebu70@gmail.com', '12345678', '12345678', 'somac', '3', 'BCS', 'EVENING', '0745907220', 'students_images\\2023_08_16867.jpeg', '2026-03-04 01:52:27');

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
('2023-08-16868', 1, 'deleted', '2026-03-04 04:53:16');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
