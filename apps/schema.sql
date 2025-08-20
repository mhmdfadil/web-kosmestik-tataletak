CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  fullname VARCHAR(100) NULL,
  gender VARCHAR(10) NULL,
  date_of_birth DATE NULL,
  place_of_birth VARCHAR(100) NULL,
  phone VARCHAR(20) NULL,
  religion VARCHAR(50) NULL,
  address TEXT NULL,
  last_login_at TIMESTAMP DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NULL
);

CREATE TABLE file_infos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename VARCHAR(255) NOT NULL,
  count_transaction INTEGER DEFAULT 0,
  count_item INTEGER DEFAULT 0,
  year INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE data_transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_id INTEGER NOT NULL,
  code_transaction VARCHAR(100) NOT NULL,
  year INTEGER NOT NULL,
  item TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (file_id) REFERENCES file_infos(id) ON DELETE CASCADE
);

CREATE TABLE process (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  preprocessing BOOLEAN DEFAULT FALSE,
  apriori BOOLEAN DEFAULT FALSE,
  fp_growth BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NULL
);

CREATE TABLE setups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  min_support_ap DECIMAL(10,2) DEFAULT 0.00,
  min_confidance_ap DECIMAL(10,2) DEFAULT 0.00,
  min_support_fp DECIMAL(10,2) DEFAULT 0.00,
  min_confidance_fp DECIMAL(10,2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NULL
);

-- Table: frequent_ap
CREATE TABLE frequent_ap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL
);

-- Table: detail_frequent_ap
CREATE TABLE detail_frequent_ap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item VARCHAR(255) NOT NULL,
    transaction_count INTEGER NOT NULL,
    support DECIMAL(10,2) DEFAULT 0.00,
    description VARCHAR(255),
    frequent_id INTEGER NOT NULL,
    FOREIGN KEY (frequent_id) REFERENCES frequent_ap(id) ON DELETE CASCADE
);

-- Table: association_rule_ap
CREATE TABLE association_rule_ap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule VARCHAR(255) NOT NULL,
    support_a DECIMAL(10,2) DEFAULT 0.00,
    support_b DECIMAL(10,2) DEFAULT 0.00,
    support_aub DECIMAL(10,2) DEFAULT 0.00,
    confidence DECIMAL(10,2) DEFAULT 0.00,
    lift DECIMAL(10,2) DEFAULT 0.00,
    correlation VARCHAR(50),
    accuracy DECIMAL(10,2) DEFAULT 0.00,
    precision DECIMAL(10,2) DEFAULT 0.00,
    recall DECIMAL(10,2) DEFAULT 0.00,
    f1_score DECIMAL(10,2) DEFAULT 0.00
);

-- Table: metrics_ap
CREATE TABLE metrics_ap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_time VARCHAR(50) NOT NULL,
    total_rules_found INTEGER NOT NULL,
    avg_lift DECIMAL(10,2) DEFAULT 0.00,
    avg_accuracy DECIMAL(10,2) DEFAULT 0.00
);





-- Table: frequent_fp
CREATE TABLE frequent_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL
);

-- Table: detail_frequent_fp
CREATE TABLE detail_frequent_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item VARCHAR(255) NOT NULL,
    transaction_count INTEGER NOT NULL,
    support DECIMAL(10,2) DEFAULT 0.00,
    description VARCHAR(255),
    frequent_id INTEGER NOT NULL,
    FOREIGN KEY (frequent_id) REFERENCES frequent_fp(id) ON DELETE CASCADE
);

-- Table: item_initial_fp
CREATE TABLE item_initial_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item VARCHAR(255) NOT NULL,
    is_initial BOOLEAN DEFAULT FALSE,          -- interpreted "initial" as a boolean flag
    transaction_count INTEGER DEFAULT 0,
    support DECIMAL(10,2) DEFAULT 0.00
);

-- Table: transaction_process_fp
CREATE TABLE transaction_process_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_code VARCHAR(100) NOT NULL,
    ordered_transaction VARCHAR(255),           -- stored ordered items as a string, e.g. "bread,milk,egg"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: mining_fptree_fp
CREATE TABLE mining_fptree_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage VARCHAR(255),                         -- tahap
    item VARCHAR(255),                          -- item at this stage/node
    pattern_base VARCHAR(255),                  -- basis pola (pattern base)
    level INTEGER DEFAULT 0,                    -- level in the FP-tree
    tree_item VARCHAR(255)                      -- item representation in the tree (node label)
);

-- Table: association_rule_fp
CREATE TABLE association_rule_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule VARCHAR(255) NOT NULL,                 -- e.g. "A -> B"
    support_a DECIMAL(10,2) DEFAULT 0.00,
    support_b DECIMAL(10,2) DEFAULT 0.00,
    confidence DECIMAL(10,2) DEFAULT 0.00,
    lift DECIMAL(10,2) DEFAULT 0.00,
    correlation VARCHAR(50),
    accuracy DECIMAL(10,2) DEFAULT 0.00,
    precision DECIMAL(10,2) DEFAULT 0.00,
    recall DECIMAL(10,2) DEFAULT 0.00,
    f1_score DECIMAL(10,2) DEFAULT 0.00
);

-- Table: metrics_fp
CREATE TABLE metrics_fp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_time VARCHAR(50) NOT NULL,
    total_rules_found INTEGER NOT NULL,
    avg_lift DECIMAL(10,2) DEFAULT 0.00,
    avg_accuracy DECIMAL(10,2) DEFAULT 0.00
);

-- Insert data into users
INSERT INTO users (password, email) VALUES 
    ('ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', 'dosen@gmail.com'),
    ('ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', 'student@gmail.com');

INSERT INTO process (preprocessing, apriori, fp_growth) VALUES 
  (FALSE, FALSE, FALSE);

INSERT INTO setups (
  min_support_ap,
  min_confidance_ap,
  min_support_fp,
  min_confidance_fp
) VALUES (
  0.30,  -- min_support_ap
  0.60,  -- min_confidance_ap
  0.30,  -- min_support_fp
  0.60  -- min_confidance_fp
);