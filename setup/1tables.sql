start transaction;

drop database if exists management;

create database management;
use management;

create table users(
    seq int primary key auto_increment,
    user_name varchar(20) unique,
    first_name varchar(20),
    last_name varchar(20),
    hash_pass varchar(200),
    email varchar(100),
    theme int,
    title varchar(6),
    manager int,
    is_active tinyint(1) default 1,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table class(
    seq int primary key auto_increment,
    position_name varchar(30),
    displayed tinyint(1) default 1,
    ranking int default 99,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,
    reports_to int,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (reports_to) references class(seq)
);

create table perm_types(
    seq int primary key auto_increment,
    perm_desc varchar(20),
    name_short varchar(30),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table perms(
    seq int primary key auto_increment,
    class_seq int,
    perm_seq int,
    granted tinyint(1) default 0,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (class_seq) references class(seq),
    constraint foreign key (perm_seq) references perm_types(seq)
);

create table class_assignments(
    seq int primary key auto_increment,
    user_seq int not null,
    class_seq int not null,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (class_seq) references class(seq)
);

create table vote_types(
    seq int primary key auto_increment,
    vote_desc varchar(20),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table vote_perms(
    seq int primary key auto_increment,
    class int not null,
    vote_seq int not null,
    granted tinyint(1),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (class) references class(seq),
    constraint foreign key (vote_seq) references vote_types(seq)
);

create table finance_status(
    seq int primary key auto_increment,
    stat_desc varchar(30),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);


create table finance_type(
    seq int primary key auto_increment,
    type_desc varchar(30),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table finance_hdr(
    seq int primary key auto_increment,
    id varchar(20),
    created_by int,
    approved_by int,
    inv_date date,
    stat_seq int not null,
    type_seq int not null,
    tax decimal(7,2),
    fees decimal(7,2),

    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (created_by) references users(seq),
    constraint foreign key (approved_by) references users(seq),

    constraint foreign key (stat_seq) references finance_status(seq),
    constraint foreign key (type_seq) references finance_type(seq)
);

/*
To improve the search results of the database by finance ID, we should add
an index.
*/
# CREATE INDEX IF NOT EXISTS finance_id_idx ON finance_hdr(id);

create table finance_line(
    seq int primary key auto_increment,
    finance_seq int,
    line_id int,
    line_desc varchar(30),
    price decimal(7,2),
    qty int,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table docket_status(
    seq int primary key auto_increment,
    stat_desc varchar(30),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table docket_hdr(
    seq int primary key auto_increment,
    docket_title varchar(30),
    docket_desc text,
    stat_seq int not null,
    vote_type int not null,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (stat_seq) references docket_status(seq),
    constraint foreign key (vote_type) references vote_types(seq)
);

CREATE TABLE docket_conversations(
    seq int primary key auto_increment,
    docket_seq int not null,
    creator int not null,
    body text,
    dt_added datetime default current_timestamp,
    CONSTRAINT foreign key (docket_seq) references docket_hdr(seq),
    CONSTRAINT foreign key (creator) references users(seq)
);

create table docket_assignees(
    seq int primary key auto_increment,
    docket_seq int,
    user_seq int,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (user_seq) references users(seq),
    constraint foreign key (docket_seq) references docket_hdr(seq)
);

create table docket_attachments(
    seq int primary key auto_increment,
    docket_seq int,
    file_name varchar(20),
    file_data blob,
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (docket_seq) references docket_hdr(seq)
);


create table dashboards(
    seq int primary key auto_increment,
    sp_name varchar(30),
    dash_type varchar(30),
    dash_name varchar(30),
    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq)
);

create table dash_assign(
    seq int primary key auto_increment,
    dash_seq int not null,
    class_seq int not null,

    added_by int,
    updated_by int,
    added_dt datetime default current_timestamp,
    update_dt datetime default current_timestamp on update current_timestamp,

    constraint foreign key (added_by) references users(seq),
    constraint foreign key (updated_by) references users(seq),
    constraint foreign key (dash_seq) references dashboards(seq),
    constraint foreign key (class_seq) references class(seq)

);

create table emails(
    seq int primary key auto_increment,
    email_subject text,
    email_body text,
    added_by int,
    added_dt timestamp default current_timestamp,
    state enum('d','s','x','p'),

    constraint foreign key (added_by) references users(seq)
);

create table email_recp(
    seq int primary key auto_increment,
    email_seq int not null,
    email_id varchar(40),
    recp_type enum('t','c','b'),
    constraint foreign key (email_seq) references emails(seq)
);

CREATE TABLE plugins (
  seq int primary key auto_increment,
  name varchar(30),
  active tinyint(1)
);

CREATE TABLE plugin_paths(
  seq int primary key auto_increment,
  plugin_seq int not null,
  path varchar(255),
  method enum('POST', 'GET', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'PUT'),
  CONSTRAINT FOREIGN KEY (plugin_seq) REFERENCES plugins(seq)
);

CREATE TABLE plugin_path_perms(
  seq int primary key auto_increment,
  plugin_path_seq int not null,
  perm_seq int,
  CONSTRAINT FOREIGN KEY (plugin_path_seq) REFERENCES plugin_paths(seq),
  CONSTRAINT FOREIGN KEY (perm_seq) REFERENCES perm_types(seq)
);

commit;