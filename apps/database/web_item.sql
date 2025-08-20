-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 20, 2025 at 09:34 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `web_item`
--

-- --------------------------------------------------------

--
-- Table structure for table `association_rule_ap`
--

CREATE TABLE `association_rule_ap` (
  `id` int(11) NOT NULL,
  `rule` varchar(255) NOT NULL,
  `support_a` decimal(10,2) DEFAULT 0.00,
  `support_b` decimal(10,2) DEFAULT 0.00,
  `support_aub` decimal(10,2) DEFAULT 0.00,
  `confidence` decimal(10,2) DEFAULT 0.00,
  `lift` decimal(10,2) DEFAULT 0.00,
  `correlation` varchar(50) DEFAULT NULL,
  `accuracy` decimal(10,2) DEFAULT 0.00,
  `precision_val` decimal(10,2) DEFAULT 0.00,
  `recall_val` decimal(10,2) DEFAULT 0.00,
  `f1_score_val` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `association_rule_fp`
--

CREATE TABLE `association_rule_fp` (
  `id` int(11) NOT NULL,
  `rule` varchar(255) NOT NULL,
  `support_a` decimal(10,2) DEFAULT 0.00,
  `support_b` decimal(10,2) DEFAULT 0.00,
  `confidence` decimal(10,2) DEFAULT 0.00,
  `lift` decimal(10,2) DEFAULT 0.00,
  `correlation` varchar(50) DEFAULT NULL,
  `accuracy` decimal(10,2) DEFAULT 0.00,
  `precision_val` decimal(10,2) DEFAULT 0.00,
  `recall_val` decimal(10,2) DEFAULT 0.00,
  `f1_score_val` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `data_transactions`
--

CREATE TABLE `data_transactions` (
  `id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  `code_transaction` varchar(100) NOT NULL,
  `year` int(11) NOT NULL,
  `item` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `detail_frequent_ap`
--

CREATE TABLE `detail_frequent_ap` (
  `id` int(11) NOT NULL,
  `item` varchar(255) NOT NULL,
  `transaction_count` int(11) NOT NULL,
  `support` decimal(10,2) DEFAULT 0.00,
  `description` varchar(255) DEFAULT NULL,
  `frequent_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `detail_frequent_fp`
--

CREATE TABLE `detail_frequent_fp` (
  `id` int(11) NOT NULL,
  `item` varchar(255) NOT NULL,
  `transaction_count` int(11) NOT NULL,
  `support` decimal(10,2) DEFAULT 0.00,
  `description` varchar(255) DEFAULT NULL,
  `frequent_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `file_infos`
--

CREATE TABLE `file_infos` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `count_transaction` int(11) DEFAULT 0,
  `count_item` int(11) DEFAULT 0,
  `year` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `frequent_ap`
--

CREATE TABLE `frequent_ap` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `frequent_fp`
--

CREATE TABLE `frequent_fp` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `item_initial_fp`
--

CREATE TABLE `item_initial_fp` (
  `id` int(11) NOT NULL,
  `item` varchar(255) NOT NULL,
  `is_initial` tinyint(1) DEFAULT 0,
  `transaction_count` int(11) DEFAULT 0,
  `support` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `metrics_ap`
--

CREATE TABLE `metrics_ap` (
  `id` int(11) NOT NULL,
  `execution_time` varchar(50) NOT NULL,
  `total_rules_found` int(11) NOT NULL,
  `avg_lift` decimal(10,2) DEFAULT 0.00,
  `avg_accuracy` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `metrics_fp`
--

CREATE TABLE `metrics_fp` (
  `id` int(11) NOT NULL,
  `execution_time` varchar(50) NOT NULL,
  `total_rules_found` int(11) NOT NULL,
  `avg_lift` decimal(10,2) DEFAULT 0.00,
  `avg_accuracy` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mining_fptree_fp`
--

CREATE TABLE `mining_fptree_fp` (
  `id` int(11) NOT NULL,
  `stage` varchar(255) DEFAULT NULL,
  `item` varchar(255) DEFAULT NULL,
  `pattern_base` varchar(255) DEFAULT NULL,
  `level` int(11) DEFAULT 0,
  `tree_item` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `process`
--

CREATE TABLE `process` (
  `id` int(11) NOT NULL,
  `preprocessing` tinyint(1) DEFAULT 0,
  `apriori` tinyint(1) DEFAULT 0,
  `fp_growth` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `setups`
--

CREATE TABLE `setups` (
  `id` int(11) NOT NULL,
  `min_support_ap` decimal(10,2) DEFAULT 0.00,
  `min_confidance_ap` decimal(10,2) DEFAULT 0.00,
  `min_support_fp` decimal(10,2) DEFAULT 0.00,
  `min_confidance_fp` decimal(10,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transaction_process_fp`
--

CREATE TABLE `transaction_process_fp` (
  `id` int(11) NOT NULL,
  `transaction_code` varchar(100) NOT NULL,
  `ordered_transaction` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `fullname` varchar(100) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `place_of_birth` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `religion` varchar(50) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `last_login_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `fullname`, `gender`, `date_of_birth`, `place_of_birth`, `phone`, `religion`, `address`, `last_login_at`, `created_at`, `updated_at`) VALUES
(1, 'admin@gmail.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-08-07 07:23:16', NULL),
(2, 'rayhan@gmail.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-08-07 07:23:16', NULL),
(3, 'fm230602@gmail.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-08-07 08:20:09', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `association_rule_ap`
--
ALTER TABLE `association_rule_ap`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `association_rule_fp`
--
ALTER TABLE `association_rule_fp`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `data_transactions`
--
ALTER TABLE `data_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_data_transactions_file_id` (`file_id`),
  ADD KEY `idx_data_transactions_year` (`year`),
  ADD KEY `idx_data_transactions_code` (`code_transaction`),
  ADD KEY `idx_data_transactions_created_at` (`created_at`);

--
-- Indexes for table `detail_frequent_ap`
--
ALTER TABLE `detail_frequent_ap`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_detail_frequent_ap_frequent_id` (`frequent_id`),
  ADD KEY `idx_detail_frequent_ap_item` (`item`),
  ADD KEY `idx_detail_frequent_ap_support` (`support`);

--
-- Indexes for table `detail_frequent_fp`
--
ALTER TABLE `detail_frequent_fp`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_detail_frequent_fp_frequent_id` (`frequent_id`),
  ADD KEY `idx_detail_frequent_fp_item` (`item`),
  ADD KEY `idx_detail_frequent_fp_support` (`support`);

--
-- Indexes for table `file_infos`
--
ALTER TABLE `file_infos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_file_infos_year` (`year`),
  ADD KEY `idx_file_infos_created_at` (`created_at`);

--
-- Indexes for table `frequent_ap`
--
ALTER TABLE `frequent_ap`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_frequent_ap_name` (`name`);

--
-- Indexes for table `frequent_fp`
--
ALTER TABLE `frequent_fp`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_frequent_fp_name` (`name`);

--
-- Indexes for table `item_initial_fp`
--
ALTER TABLE `item_initial_fp`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_item_initial_fp_item` (`item`),
  ADD KEY `idx_item_initial_fp_is_initial` (`is_initial`),
  ADD KEY `idx_item_initial_fp_support` (`support`);

--
-- Indexes for table `metrics_ap`
--
ALTER TABLE `metrics_ap`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_metrics_ap_execution_time` (`execution_time`);

--
-- Indexes for table `metrics_fp`
--
ALTER TABLE `metrics_fp`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_metrics_fp_execution_time` (`execution_time`);

--
-- Indexes for table `mining_fptree_fp`
--
ALTER TABLE `mining_fptree_fp`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_mining_fptree_fp_stage` (`stage`),
  ADD KEY `idx_mining_fptree_fp_item` (`item`),
  ADD KEY `idx_mining_fptree_fp_level` (`level`);

--
-- Indexes for table `process`
--
ALTER TABLE `process`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_process_created_at` (`created_at`);

--
-- Indexes for table `setups`
--
ALTER TABLE `setups`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_setups_created_at` (`created_at`);

--
-- Indexes for table `transaction_process_fp`
--
ALTER TABLE `transaction_process_fp`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_transaction_process_fp_code` (`transaction_code`),
  ADD KEY `idx_transaction_process_fp_created_at` (`created_at`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_users_email` (`email`),
  ADD KEY `idx_users_created_at` (`created_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `association_rule_ap`
--
ALTER TABLE `association_rule_ap`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=79;

--
-- AUTO_INCREMENT for table `association_rule_fp`
--
ALTER TABLE `association_rule_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=461;

--
-- AUTO_INCREMENT for table `data_transactions`
--
ALTER TABLE `data_transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4661;

--
-- AUTO_INCREMENT for table `detail_frequent_ap`
--
ALTER TABLE `detail_frequent_ap`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85674;

--
-- AUTO_INCREMENT for table `detail_frequent_fp`
--
ALTER TABLE `detail_frequent_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=484;

--
-- AUTO_INCREMENT for table `file_infos`
--
ALTER TABLE `file_infos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `frequent_ap`
--
ALTER TABLE `frequent_ap`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `frequent_fp`
--
ALTER TABLE `frequent_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `item_initial_fp`
--
ALTER TABLE `item_initial_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=328;

--
-- AUTO_INCREMENT for table `metrics_ap`
--
ALTER TABLE `metrics_ap`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `metrics_fp`
--
ALTER TABLE `metrics_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `mining_fptree_fp`
--
ALTER TABLE `mining_fptree_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24157962;

--
-- AUTO_INCREMENT for table `process`
--
ALTER TABLE `process`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `setups`
--
ALTER TABLE `setups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `transaction_process_fp`
--
ALTER TABLE `transaction_process_fp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21761;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `data_transactions`
--
ALTER TABLE `data_transactions`
  ADD CONSTRAINT `data_transactions_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `file_infos` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `detail_frequent_ap`
--
ALTER TABLE `detail_frequent_ap`
  ADD CONSTRAINT `detail_frequent_ap_ibfk_1` FOREIGN KEY (`frequent_id`) REFERENCES `frequent_ap` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `detail_frequent_fp`
--
ALTER TABLE `detail_frequent_fp`
  ADD CONSTRAINT `detail_frequent_fp_ibfk_1` FOREIGN KEY (`frequent_id`) REFERENCES `frequent_fp` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
