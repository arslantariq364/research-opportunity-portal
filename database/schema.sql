-- ========================================================
-- University Research Opportunity Portal
-- Database Schema Definition (Phase 1)
-- Database Name: research_portal
-- ========================================================

-- Create database if it does not already exist
CREATE DATABASE IF NOT EXISTS research_portal
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE research_portal;

-- Drop table if it exists to allow idempotent initialization
DROP TABLE IF EXISTS research_opportunities;

-- Create research_opportunities table
CREATE TABLE research_opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    research_area VARCHAR(255) NOT NULL,
    faculty_name VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    required_skills TEXT NOT NULL,
    available_positions INT NOT NULL CHECK (available_positions > 0),
    application_deadline DATE NOT NULL,
    status ENUM('Open', 'Closed') NOT NULL DEFAULT 'Open',
    CONSTRAINT chk_status_valid CHECK (status IN ('Open', 'Closed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
