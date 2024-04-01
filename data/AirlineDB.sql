-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Mar 16, 2024 at 11:53 AM
-- Server version: 5.7.39
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `AirlineDB`
--

-- --------------------------------------------------------

--
-- Table structure for table `aircrafts`
--

CREATE TABLE `aircrafts` (
  `aircraft_id` varchar(3) NOT NULL,
  `model` int(11) NOT NULL,
  `max_range` int(11) NOT NULL,
  `avg_speed` int(11) NOT NULL,
  `turnaround_time` int(11) NOT NULL,
  `first_class_seats` int(11) NOT NULL,
  `business_class_seats` int(11) NOT NULL,
  `economy_seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `destinations`
--

CREATE TABLE `destinations` (
  `destination_icao` varchar(4) NOT NULL,
  `name` varchar(100) NOT NULL,
  `location` varchar(45) NOT NULL,
  `country` varchar(45) NOT NULL,
  `time_zone` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `fleet`
--

CREATE TABLE `fleet` (
  `registration` varchar(6) NOT NULL,
  `aircraft_id` varchar(3) NOT NULL,
  `acquisition_date` date NOT NULL,
  `last_maintenance` date DEFAULT NULL,
  `is_operational` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `hubs`
--

CREATE TABLE `hubs` (
  `hub_icao` varchar(4) NOT NULL,
  `name` varchar(100) NOT NULL,
  `location` varchar(45) NOT NULL,
  `country` varchar(45) NOT NULL,
  `time_zone` int(11) NOT NULL,
  `gates` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `routes`
--

CREATE TABLE `routes` (
  `route_id` int(11) NOT NULL,
  `hub_id` varchar(4) NOT NULL,
  `destination_id` varchar(4) NOT NULL,
  `distance` int(11) NOT NULL,
  `flight_time` int(11) NOT NULL,
  `first_class_demand` int(11) NOT NULL,
  `business_demand` int(11) NOT NULL,
  `economy_demand` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `aircrafts`
--
ALTER TABLE `aircrafts`
  ADD PRIMARY KEY (`aircraft_id`);

--
-- Indexes for table `destinations`
--
ALTER TABLE `destinations`
  ADD PRIMARY KEY (`destination_icao`);

--
-- Indexes for table `fleet`
--
ALTER TABLE `fleet`
  ADD PRIMARY KEY (`registration`),
  ADD KEY `aircraft_id` (`aircraft_id`);

--
-- Indexes for table `hubs`
--
ALTER TABLE `hubs`
  ADD PRIMARY KEY (`hub_icao`);

--
-- Indexes for table `routes`
--
ALTER TABLE `routes`
  ADD PRIMARY KEY (`route_id`),
  ADD KEY `hub_id` (`hub_id`,`destination_id`),
  ADD KEY `routes_did` (`destination_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `routes`
--
ALTER TABLE `routes`
  MODIFY `route_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `fleet`
--
ALTER TABLE `fleet`
  ADD CONSTRAINT `fleet_aid` FOREIGN KEY (`aircraft_id`) REFERENCES `aircrafts` (`aircraft_id`);

--
-- Constraints for table `routes`
--
ALTER TABLE `routes`
  ADD CONSTRAINT `routes_did` FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`destination_icao`),
  ADD CONSTRAINT `routes_hid` FOREIGN KEY (`hub_id`) REFERENCES `hubs` (`hub_icao`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
