USE management;

CREATE TABLE db_tables (
    seq int not null primary key auto_increment,
    name varchar(30) unique not null,
    type enum('table', 'view') not null,
    self_introspect tinyint(1) not null default 1,
    maintained tinyint(1) not null default 1
);

CREATE TABLE db_cols (
    seq int not null primary key auto_increment,
    table_seq int not null,
    name varchar(30) not null,
    type varchar(30) not null,
    maintained tinyint(1) not null default 1,
    CONSTRAINT FOREIGN KEY (table_seq) REFERENCES db_tables(seq) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE db_rels (
    seq int not null primary key auto_increment,
    col int not null,
    target_col int not null,
    maintained tinyint(1) not null default 1,
    CONSTRAINT FOREIGN KEY (col) REFERENCES db_cols(seq) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FOREIGN KEY (target_col) REFERENCES db_cols(seq) ON DELETE CASCADE ON UPDATE CASCADE
);

