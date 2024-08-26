DROP DATABASE IF EXISTS management;
CREATE DATABASE management;
use management;
CREATE TABLE users (
    seq           INT AUTO_INCREMENT PRIMARY KEY, 
    user_name     VARCHAR(20) NOT NULL, 
    first_name    VARCHAR(20) NOT NULL, 
    last_name     VARCHAR(20) NOT NULL, 
    hash_pass     VARCHAR(200) NULL, 
    email         VARCHAR(100) NOT NULL, 
    theme         INT NOT NULL, 
    title         VARCHAR(6) NOT NULL, 
    is_active     TINYINT(1) DEFAULT 1 NOT NULL, 
    home_page_seq INT
    added_by      INT NULL, 
    updated_by    INT NULL, 
    added_dt      DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    update_dt     DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON UPDATE CURRENT_TIMESTAMP(), 
    CONSTRAINT user_name UNIQUE (user_name), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq),
    CONSTRAINT FOREIGN KEY (home_page_seq) REFERENCES home_page_defn(seq)
);

CREATE TABLE class (
    seq             INT AUTO_INCREMENT PRIMARY KEY, 
    position_name   VARCHAR(30) NOT NULL, 
    displayed       TINYINT(1) DEFAULT 1 NOT NULL, 
    ranking         INT DEFAULT 99 NOT NULL, 
    added_by        INT NULL, 
    updated_by      INT NULL, 
    added_dt        DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    update_dt       DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON UPDATE CURRENT_TIMESTAMP(), 
    reports_to      INT NULL, 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (reports_to) REFERENCES class (seq)
);

CREATE TABLE terms (
    seq               INT AUTO_INCREMENT PRIMARY KEY, 
    start_date        DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    end_date          DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    term_desc         VARCHAR(10) NOT NULL, 
    added_by          INT NULL, 
    updated_by        INT NULL, 
    added_dt          DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    update_dt         DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON UPDATE CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);

CREATE TABLE class_assignments (
    seq           INT AUTO_INCREMENT PRIMARY KEY, 
    user_seq      INT NOT NULL, 
    class_seq     INT NOT NULL, 
    start_term    INT NOT NULL, 
    end_term      INT NOT NULL, 
    added_by      INT NULL, 
    updated_by    INT NULL, 
    added_dt      DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    update_dt     DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON UPDATE CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (class_seq) REFERENCES class (seq), 
    CONSTRAINT FOREIGN KEY (start_term) REFERENCES terms (seq), 
    CONSTRAINT FOREIGN KEY (end_term) REFERENCES terms (seq)
);

CREATE TABLE del_class_assignments (
    seq           INT AUTO_INCREMENT PRIMARY KEY, 
    user_seq      INT NOT NULL, 
    class_seq     INT NOT NULL, 
    start_term    INT NOT NULL, 
    end_term      INT NOT NULL, 
    added_by      INT NULL, 
    updated_by    INT NULL, 
    added_dt      DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
    update_dt     DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON UPDATE CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (class_seq) REFERENCES class (seq), 
    CONSTRAINT FOREIGN KEY (start_term) REFERENCES terms (seq), 
    CONSTRAINT FOREIGN KEY (end_term) REFERENCES terms (seq)
);

CREATE TABLE dashboards (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  sp_name VARCHAR(30) NOT NULL, 
  dash_type VARCHAR(30) NOT NULL, 
  dash_name VARCHAR(30) NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE dash_assign (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  dash_seq INT NOT NULL, 
  class_seq INT NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (dash_seq) REFERENCES dashboards (seq), 
    CONSTRAINT FOREIGN KEY (class_seq) REFERENCES class (seq)
);
CREATE TABLE docket_status (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  stat_desc VARCHAR(30) NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE contacts (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  email_address VARCHAR(100) NOT NULL, 
  first_name VARCHAR(20) NOT NULL, 
  last_name VARCHAR(20) NOT NULL, 
  is_active TINYINT(1) NOT NULL
);
CREATE TABLE emails (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  email_subject text NOT NULL, 
  email_body text NOT NULL, 
  added_by INT NULL, 
  added_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  state ENUM ('d', 's', 'x', 'p') NOT NULL, 
  CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq)
);
CREATE TABLE email_recp (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  email_seq INT NOT NULL, 
  contact_seq INT NOT NULL, 
  recp_type ENUM ('t', 'c', 'b') NOT NULL, 
  CONSTRAINT FOREIGN KEY (email_seq) REFERENCES emails (seq), 
  CONSTRAINT FOREIGN KEY (contact_seq) REFERENCES contacts(seq)
);
CREATE TABLE finance_status (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  stat_desc VARCHAR(30) NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE finance_type (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  type_desc VARCHAR(30) NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE finance_hdr (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  id VARCHAR(20) NOT NULL, 
  created_by INT NOT NULL, 
  approved_by INT NULL, 
  is_approved TINYINT(1) DEFAULT 0 NOT NULL, 
  inv_date DATE NOT NULL, 
  stat_seq INT NOT NULL, 
  type_seq INT NOT NULL, 
  tax DECIMAL(7, 2) NOT NULL, 
  fees DECIMAL(7, 2) NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (created_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (approved_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (stat_seq) REFERENCES finance_status (seq), 
    CONSTRAINT FOREIGN KEY (type_seq) REFERENCES finance_type (seq)
);
CREATE TABLE items (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  item_vendor VARCHAR(20) NOT NULL, 
  item_name VARCHAR(50) NOT NULL, 
  displayed TINYINT(1) NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE item_cost (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  item_seq INT NOT NULL, 
  eff_date DATE NOT NULL, 
  price DECIMAL(9, 4) NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (item_seq) REFERENCES items (seq)
);
CREATE TABLE finance_line (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  finance_seq INT NOT NULL, 
  line_id INT NOT NULL, 
  item_id INT NOT NULL, 
  qty INT NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (item_id) REFERENCES item_cost (seq)
);
CREATE TABLE perm_types (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  perm_desc VARCHAR(40) NOT NULL, 
  name_short VARCHAR(30) NOT NULL, 
  grantable TINYINT(1) DEFAULT 1 NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE perms (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  class_seq INT NOT NULL, 
  perm_seq INT NOT NULL, 
  granted TINYINT(1) DEFAULT 0 NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (class_seq) REFERENCES class (seq), 
    CONSTRAINT FOREIGN KEY (perm_seq) REFERENCES perm_types (seq)
);
CREATE TABLE plugin_defn (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  plugin_name VARCHAR(30) NOT NULL, 
  author VARCHAR(20) NOT NULL, 
  support_email VARCHAR(30) NOT NULL, 
  is_active TINYINT DEFAULT 0 NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  admin_perm INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    menu_path VARCHAR(50) NOT NULL, 
    CONSTRAINT FOREIGN KEY (admin_perm) REFERENCES perm_types (seq), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE plugin_permissions (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  plugin_seq INT NOT NULL, 
  path_func_name VARCHAR(50) NOT NULL, 
  perm_seq INT NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (plugin_seq) REFERENCES plugin_defn (seq), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE vote_types (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  vote_desc VARCHAR(20) NOT NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq)
);
CREATE TABLE docket_hdr (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  docket_title VARCHAR(30) NOT NULL, 
  docket_desc text NOT NULL, 
  stat_seq INT NOT NULL, 
  vote_type INT NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (stat_seq) REFERENCES docket_status (seq), 
    CONSTRAINT FOREIGN KEY (vote_type) REFERENCES vote_types (seq)
);
CREATE TABLE docket_assignees (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  docket_seq INT NOT NULL, 
  user_seq INT NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (user_seq) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (docket_seq) REFERENCES docket_hdr (seq)
);
CREATE TABLE docket_attachments (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  docket_seq INT NOT NULL, 
  file_name VARCHAR(100) NOT NULL, 
  file_data BLOB NOT NULL, 
  added_by INT NOT NULL, 
  updated_by INT NOT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (docket_seq) REFERENCES docket_hdr (seq)
);
CREATE TABLE docket_conversations (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  docket_seq INT NOT NULL, 
  creator INT NOT NULL, 
  body text NULL, 
  dt_added DATETIME DEFAULT CURRENT_TIMESTAMP() NULL, 
  CONSTRAINT FOREIGN KEY (docket_seq) REFERENCES docket_hdr (seq), 
  CONSTRAINT FOREIGN KEY (creator) REFERENCES users (seq)
);
CREATE TABLE vote_perms (
  seq INT AUTO_INCREMENT PRIMARY KEY, 
  class INT NOT NULL, 
  vote_seq INT NOT NULL, 
  granted TINYINT(1) NULL, 
  added_by INT NULL, 
  updated_by INT NULL, 
  added_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NULL, 
  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON 
  UPDATE 
    CURRENT_TIMESTAMP(), 
    CONSTRAINT FOREIGN KEY (added_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users (seq), 
    CONSTRAINT FOREIGN KEY (class) REFERENCES class (seq), 
    CONSTRAINT FOREIGN KEY (vote_seq) REFERENCES vote_types (seq)
);
CREATE TABLE home_widgets(
  seq INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
  plugin_seq INT NOT NULL, 
  widget_name VARCHAR(30) DEFAULT 'blank', 
  widget_path VARCHAR(30) DEFAULT 'widgets/blank.liquid', 
  CONSTRAINT FOREIGN KEY (plugin_seq) REFERENCES plugin_defn(seq)
);
CREATE TABLE home_page_defn(
  seq INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
  top_left_widget INT NOT NULL, 
  top_rght_widget INT NOT NULL, 
  bot_left_widget INT NOT NULL, 
  bot_rght_widget INT NOT NULL, 
  CONSTRAINT FOREIGN KEY (top_left_widget) REFERENCES home_widgets(seq), 
  CONSTRAINT FOREIGN KEY (top_rght_widget) REFERENCES home_widgets(seq), 
  CONSTRAINT FOREIGN KEY (bot_left_widget) REFERENCES home_widgets(seq), 
  CONSTRAINT FOREIGN KEY (bot_rght_widget) REFERENCES home_widgets(seq)
);
CREATE TABLE access_requests(
  seq INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
  user_name VARCHAR(20) NOT NULL, 
  first_name VARCHAR(20) NOT NULL, 
  last_name VARCHAR(20) NOT NULL, 
  email VARCHAR(100) NOT NULL, 
  title VARCHAR(6) NOT NULL
);

