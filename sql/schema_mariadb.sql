CREATE TABLE IF NOT EXISTS races (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    location VARCHAR(255) NOT NULL,
    distance_text VARCHAR(50) NULL,
    distance_m INT NULL,
    UNIQUE KEY uq_races_year_location (year, location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS runners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    sex VARCHAR(10) NOT NULL,
    UNIQUE KEY uq_runner_identity (first_name, last_name, sex)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT NOT NULL,
    runner_id INT NOT NULL,
    position INT NOT NULL,
    bib_number INT NULL,
    category_code VARCHAR(20) NULL,
    time_text VARCHAR(20) NULL,
    time_seconds INT NULL,
    distance_text VARCHAR(50) NULL,
    distance_m INT NULL,
    UNIQUE KEY uq_results_race_position (race_id, position),
    KEY idx_results_bib (bib_number),
    CONSTRAINT fk_results_race
        FOREIGN KEY (race_id) REFERENCES races (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_results_runner
        FOREIGN KEY (runner_id) REFERENCES runners (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
