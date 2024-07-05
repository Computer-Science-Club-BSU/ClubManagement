DROP DATABASE IF EXISTS management;
CREATE DATABASE management;
USE management;

create or replace table users
(
    seq        int auto_increment
        primary key,
    user_name  varchar(20)                            not null,
    first_name varchar(20)                            not null,
    last_name  varchar(20)                            not null,
    hash_pass  varchar(200)                           null,
    email      varchar(100)                           not null,
    theme      int                                    not null,
    title      varchar(6)                             not null,
    is_active  tinyint(1) default 1                   not null,
    added_by   int                                    null,
    updated_by int                                    null,
    added_dt   datetime   default current_timestamp() not null,
    update_dt  datetime   default current_timestamp() not null on update current_timestamp(),
    constraint user_name
        unique (user_name),
    constraint users_ibfk_1
        foreign key (added_by) references users (seq),
    constraint users_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace table class
(
    seq           int auto_increment
        primary key,
    position_name varchar(30)                            not null,
    displayed     tinyint(1) default 1                   not null,
    ranking       int        default 99                  not null,
    added_by      int                                    null,
    updated_by    int                                    null,
    added_dt      datetime   default current_timestamp() not null,
    update_dt     datetime   default current_timestamp() not null on update current_timestamp(),
    reports_to    int                                    null,
    constraint class_ibfk_1
        foreign key (added_by) references users (seq),
    constraint class_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint class_ibfk_3
        foreign key (reports_to) references class (seq)
);

create or replace index added_by
    on class (added_by);

create or replace index reports_to
    on class (reports_to);

create or replace index updated_by
    on class (updated_by);

create or replace table terms
(
    seq         int auto_increment primary key,
    start_date  datetime default current_timestamp() not null,
    end_date    datetime default current_timestamp() not null,
    term_desc   varchar(10)                          not null,
    added_by   int                                    null,
    updated_by int                                    null,
    added_dt   datetime   default current_timestamp() not null,
    update_dt  datetime   default current_timestamp() not null on update current_timestamp(),
    constraint terms_ibfk_1
        foreign key (added_by) references users (seq),
    constraint terms_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace table class_assignments
(
    seq        int auto_increment
        primary key,
    user_seq   int                                    not null,
    class_seq  int                                    not null,
    start_term int                                    not null,
    end_term   int                                    not null,
    added_by   int                                    null,
    updated_by int                                    null,
    added_dt   datetime   default current_timestamp() not null,
    update_dt  datetime   default current_timestamp() not null on update current_timestamp(),
    constraint class_assignments_ibfk_1
        foreign key (added_by) references users (seq),
    constraint class_assignments_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint class_assignments_ibfk_3
        foreign key (class_seq) references class (seq),
    constraint class_assignments_ibfk_4
        foreign key (start_term) references terms (seq),
    constraint class_assignments_ibfk_5
        foreign key (end_term) references terms (seq)
);

create or replace index added_by
    on class_assignments (added_by);

create or replace index class_seq
    on class_assignments (class_seq);

create or replace index updated_by
    on class_assignments (updated_by);

create or replace table dashboards
(
    seq        int auto_increment
        primary key,
    sp_name    varchar(30)                          not null,
    dash_type  varchar(30)                          not null,
    dash_name  varchar(30)                          not null,
    added_by   int                                  null,
    updated_by int                                  null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint dashboards_ibfk_1
        foreign key (added_by) references users (seq),
    constraint dashboards_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace table dash_assign
(
    seq        int auto_increment
        primary key,
    dash_seq   int                                  not null,
    class_seq  int                                  not null,
    added_by   int                                  not null,
    updated_by int                                  not null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint dash_assign_ibfk_1
        foreign key (added_by) references users (seq),
    constraint dash_assign_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint dash_assign_ibfk_3
        foreign key (dash_seq) references dashboards (seq),
    constraint dash_assign_ibfk_4
        foreign key (class_seq) references class (seq)
);

create or replace index added_by
    on dash_assign (added_by);

create or replace index class_seq
    on dash_assign (class_seq);

create or replace index dash_seq
    on dash_assign (dash_seq);

create or replace index updated_by
    on dash_assign (updated_by);

create or replace index added_by
    on dashboards (added_by);

create or replace index updated_by
    on dashboards (updated_by);

create or replace table docket_status
(
    seq        int auto_increment
        primary key,
    stat_desc  varchar(30)                          not null,
    added_by   int                                  null,
    updated_by int                                  null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint docket_status_ibfk_1
        foreign key (added_by) references users (seq),
    constraint docket_status_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace index added_by
    on docket_status (added_by);

create or replace index updated_by
    on docket_status (updated_by);

create or replace table contacts
(
    seq             int auto_increment primary key,
    email_address   varchar(100)                        not null,
    first_name      varchar(20)                         not null,
    last_name       varchar(20)                         not null,
    is_active       tinyint(1)                          not null
);

create or replace table emails
(
    seq           int auto_increment
        primary key,
    email_subject text                                  not null,
    email_body    text                                  not null,
    added_by      int                                   null,
    added_dt      timestamp default current_timestamp() not null,
    state         enum ('d', 's', 'x', 'p')             not null,
    constraint emails_ibfk_1
        foreign key (added_by) references users (seq)
);

create or replace table email_recp
(
    seq       int auto_increment
        primary key,
    email_seq int                  not null,
    contact_seq  int               not null,
    recp_type enum ('t', 'c', 'b') not null,
    constraint email_recp_ibfk_1
        foreign key (email_seq) references emails (seq),
    constraint email_recp_ibfk_2
        foreign key (contact_seq) references contacts(seq)
);

create or replace index email_seq
    on email_recp (email_seq);

create or replace index added_by
    on emails (added_by);

create or replace table finance_status
(
    seq        int auto_increment
        primary key,
    stat_desc  varchar(30)                          not null,
    added_by   int                                  null,
    updated_by int                                  null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint finance_status_ibfk_1
        foreign key (added_by) references users (seq),
    constraint finance_status_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace index added_by
    on finance_status (added_by);

create or replace index updated_by
    on finance_status (updated_by);

create or replace table finance_type
(
    seq        int auto_increment
        primary key,
    type_desc  varchar(30)                          not null,
    added_by   int                                  null,
    updated_by int                                  null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint finance_type_ibfk_1
        foreign key (added_by) references users (seq),
    constraint finance_type_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace table finance_hdr
(
    seq         int auto_increment
        primary key,
    id          varchar(20)                          not null,
    created_by  int                                  not null,
    approved_by int                                  null,
    is_approved tinyint(1) default 0                 not null,
    inv_date    date                                 not null,
    stat_seq    int                                  not null,
    type_seq    int                                  not null,
    tax         decimal(7, 2)                        not null,
    fees        decimal(7, 2)                        not null,
    added_by    int                                  null,
    updated_by  int                                  null,
    added_dt    datetime default current_timestamp() not null,
    update_dt   datetime default current_timestamp() not null on update current_timestamp(),
    constraint finance_hdr_ibfk_1
        foreign key (added_by) references users (seq),
    constraint finance_hdr_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint finance_hdr_ibfk_3
        foreign key (created_by) references users (seq),
    constraint finance_hdr_ibfk_4
        foreign key (approved_by) references users (seq),
    constraint finance_hdr_ibfk_5
        foreign key (stat_seq) references finance_status (seq),
    constraint finance_hdr_ibfk_6
        foreign key (type_seq) references finance_type (seq)
);

create or replace index added_by
    on finance_hdr (added_by);

create or replace index approved_by
    on finance_hdr (approved_by);

create or replace index created_by
    on finance_hdr (created_by);

create or replace index finance_id_idx
    on finance_hdr (id);

create or replace index stat_seq
    on finance_hdr (stat_seq);

create or replace index type_seq
    on finance_hdr (type_seq);

create or replace index updated_by
    on finance_hdr (updated_by);

create or replace index added_by
    on finance_type (added_by);

create or replace index updated_by
    on finance_type (updated_by);

create or replace table items
(
    seq         int auto_increment
        primary key,
    item_vendor varchar(20)                          not null,
    item_name   varchar(50)                          not null,
    displayed   tinyint(1)                           not null,
    added_by    int                                  not null,
    updated_by  int                                  not null,
    added_dt    datetime default current_timestamp() not null,
    update_dt   datetime default current_timestamp() not null on update current_timestamp(),
    constraint items_ibfk_1
        foreign key (added_by) references users (seq),
    constraint items_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace table item_cost
(
    seq        int auto_increment
        primary key,
    item_seq   int                                  not null,
    eff_date   date                                 not null,
    price      decimal(9, 4)                        not null,
    added_by   int                                  not null,
    updated_by int                                  not null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint item_cost_ibfk_1
        foreign key (added_by) references users (seq),
    constraint item_cost_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint item_cost_ibfk_3
        foreign key (item_seq) references items (seq)
);

create or replace table finance_line
(
    seq         int auto_increment
        primary key,
    finance_seq int                                  not null,
    line_id     int                                  not null,
    item_id     int                                  not null,
    qty         int                                  not null,
    added_by    int                                  not null,
    updated_by  int                                  not null,
    added_dt    datetime default current_timestamp() not null,
    update_dt   datetime default current_timestamp() not null on update current_timestamp(),
    constraint finance_line_ibfk_1
        foreign key (added_by) references users (seq),
    constraint finance_line_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint finance_line_ibfk_3
        foreign key (item_id) references item_cost (seq)
);

create or replace index added_by
    on finance_line (added_by);

create or replace index item_id
    on finance_line (item_id);

create or replace index updated_by
    on finance_line (updated_by);

create or replace index added_by
    on item_cost (added_by);

create or replace index item_seq
    on item_cost (item_seq);

create or replace index updated_by
    on item_cost (updated_by);

create or replace index added_by
    on items (added_by);

create or replace index updated_by
    on items (updated_by);

create or replace table perm_types
(
    seq        int auto_increment
        primary key,
    perm_desc  varchar(40)                            not null,
    name_short varchar(30)                            not null,
    grantable  tinyint(1) default 1                   not null,
    added_by   int                                    null,
    updated_by int                                    null,
    added_dt   datetime   default current_timestamp() not null,
    update_dt  datetime   default current_timestamp() not null on update current_timestamp(),
    constraint perm_types_ibfk_1
        foreign key (added_by) references users (seq),
    constraint perm_types_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace index added_by
    on perm_types (added_by);

create or replace index updated_by
    on perm_types (updated_by);

create or replace table perms
(
    seq        int auto_increment
        primary key,
    class_seq  int                                    not null,
    perm_seq   int                                    not null,
    granted    tinyint(1) default 0                   not null,
    added_by   int                                    null,
    updated_by int                                    null,
    added_dt   datetime   default current_timestamp() not null,
    update_dt  datetime   default current_timestamp() not null on update current_timestamp(),
    constraint perms_ibfk_1
        foreign key (added_by) references users (seq),
    constraint perms_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint perms_ibfk_3
        foreign key (class_seq) references class (seq),
    constraint perms_ibfk_4
        foreign key (perm_seq) references perm_types (seq)
);

create or replace index added_by
    on perms (added_by);

create or replace index class_seq
    on perms (class_seq);

create or replace index perm_seq
    on perms (perm_seq);

create or replace index updated_by
    on perms (updated_by);

create or replace table plugin_defn
(
    seq           int auto_increment
        primary key,
    plugin_name   varchar(30)                          not null,
    author        varchar(20)                          not null,
    support_email varchar(30)                          not null,
    is_active     tinyint  default 0                   not null,
    added_by      int                                  null,
    updated_by    int                                  null,
    admin_perm    int                                  not null,
    added_dt      datetime default current_timestamp() not null,
    update_dt     datetime default current_timestamp() not null on update current_timestamp(),
    menu_path     varchar(50)                          not null,
    constraint plugin_defn_ibfk_1
        foreign key (admin_perm) references perm_types (seq),
    constraint plugin_defn_ibfk_2
        foreign key (added_by) references users (seq),
    constraint plugin_defn_ibfk_3
        foreign key (updated_by) references users (seq)
);

create or replace index added_by
    on plugin_defn (added_by);

create or replace index admin_perm
    on plugin_defn (admin_perm);

create or replace index updated_by
    on plugin_defn (updated_by);

create or replace table plugin_permissions
(
    seq            int auto_increment
        primary key,
    plugin_seq     int                                  not null,
    path_func_name varchar(50)                          not null,
    perm_seq       int                                  not null,
    added_by       int                                  null,
    updated_by     int                                  null,
    added_dt       datetime default current_timestamp() not null,
    update_dt      datetime default current_timestamp() not null on update current_timestamp(),
    constraint plugin_permissions_ibfk_1
        foreign key (plugin_seq) references plugin_defn (seq),
    constraint plugin_permissions_ibfk_2
        foreign key (added_by) references users (seq),
    constraint plugin_permissions_ibfk_3
        foreign key (updated_by) references users (seq)
);

create or replace index added_by
    on plugin_permissions (added_by);

create or replace index plugin_seq
    on plugin_permissions (plugin_seq);

create or replace index updated_by
    on plugin_permissions (updated_by);

create or replace index added_by
    on users (added_by);

create or replace index updated_by
    on users (updated_by);

create or replace table vote_types
(
    seq        int auto_increment
        primary key,
    vote_desc  varchar(20)                          not null,
    added_by   int                                      null,
    updated_by int                                      null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint vote_types_ibfk_1
        foreign key (added_by) references users (seq),
    constraint vote_types_ibfk_2
        foreign key (updated_by) references users (seq)
);

create or replace table docket_hdr
(
    seq          int auto_increment
        primary key,
    docket_title varchar(30)                          not null,
    docket_desc  text                                 not null,
    stat_seq     int                                  not null,
    vote_type    int                                  not null,
    added_by     int                                  not null,
    updated_by   int                                  not null,
    added_dt     datetime default current_timestamp() not null,
    update_dt    datetime default current_timestamp() not null on update current_timestamp(),
    constraint docket_hdr_ibfk_1
        foreign key (added_by) references users (seq),
    constraint docket_hdr_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint docket_hdr_ibfk_3
        foreign key (stat_seq) references docket_status (seq),
    constraint docket_hdr_ibfk_4
        foreign key (vote_type) references vote_types (seq)
);

create or replace table docket_assignees
(
    seq        int auto_increment
        primary key,
    docket_seq int                                  not null,
    user_seq   int                                  not null,
    added_by   int                                  not null,
    updated_by int                                  not null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint docket_assignees_ibfk_1
        foreign key (added_by) references users (seq),
    constraint docket_assignees_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint docket_assignees_ibfk_3
        foreign key (user_seq) references users (seq),
    constraint docket_assignees_ibfk_4
        foreign key (docket_seq) references docket_hdr (seq)
);

create or replace index added_by
    on docket_assignees (added_by);

create or replace index docket_seq
    on docket_assignees (docket_seq);

create or replace index updated_by
    on docket_assignees (updated_by);

create or replace index user_seq
    on docket_assignees (user_seq);

create or replace table docket_attachments
(
    seq        int auto_increment
        primary key,
    docket_seq int                                  not null,
    file_name  varchar(100)                         not null,
    file_data  blob                                 not null,
    added_by   int                                  not null,
    updated_by int                                  not null,
    added_dt   datetime default current_timestamp() not null,
    update_dt  datetime default current_timestamp() not null on update current_timestamp(),
    constraint docket_attachments_ibfk_1
        foreign key (added_by) references users (seq),
    constraint docket_attachments_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint docket_attachments_ibfk_3
        foreign key (docket_seq) references docket_hdr (seq)
);

create or replace index added_by
    on docket_attachments (added_by);

create or replace index docket_seq
    on docket_attachments (docket_seq);

create or replace index updated_by
    on docket_attachments (updated_by);

create or replace table docket_conversations
(
    seq        int auto_increment
        primary key,
    docket_seq int                                  not null,
    creator    int                                  not null,
    body       text                                 null,
    dt_added   datetime default current_timestamp() null,
    constraint docket_conversations_ibfk_1
        foreign key (docket_seq) references docket_hdr (seq),
    constraint docket_conversations_ibfk_2
        foreign key (creator) references users (seq)
);

create or replace index creator
    on docket_conversations (creator);

create or replace index docket_seq
    on docket_conversations (docket_seq);

create or replace index added_by
    on docket_hdr (added_by);

create or replace index stat_seq
    on docket_hdr (stat_seq);

create or replace index updated_by
    on docket_hdr (updated_by);

create or replace index vote_type
    on docket_hdr (vote_type);

create or replace table vote_perms
(
    seq        int auto_increment
        primary key,
    class      int                                  not null,
    vote_seq   int                                  not null,
    granted    tinyint(1)                           null,
    added_by   int                                  null,
    updated_by int                                  null,
    added_dt   datetime default current_timestamp() null,
    update_dt  datetime default current_timestamp() null on update current_timestamp(),
    constraint vote_perms_ibfk_1
        foreign key (added_by) references users (seq),
    constraint vote_perms_ibfk_2
        foreign key (updated_by) references users (seq),
    constraint vote_perms_ibfk_3
        foreign key (class) references class (seq),
    constraint vote_perms_ibfk_4
        foreign key (vote_seq) references vote_types (seq)
);

create or replace index added_by
    on vote_perms (added_by);

create or replace index class
    on vote_perms (class);

create or replace index updated_by
    on vote_perms (updated_by);

create or replace index vote_seq
    on vote_perms (vote_seq);

create or replace index added_by
    on vote_types (added_by);

create or replace index updated_by
    on vote_types (updated_by);




CREATE TABLE home_widgets(
    seq int not null primary key auto_increment,
    plugin_seq int not null,
    widget_name varchar(30) default 'blank',
    widget_path varchar(30) default 'widgets/blank.liquid',
    CONSTRAINT FOREIGN KEY (plugin_seq) REFERENCES plugin_defn(seq)
);

CREATE TABLE home_page_defn(
    seq int not null primary key auto_increment,
    top_left_widget int                 not null,
    top_rght_widget int                 not null,
    bot_left_widget int                 not null,
    bot_rght_widget int                 not null,
    CONSTRAINT FOREIGN KEY (top_left_widget) REFERENCES home_widgets(seq),
    CONSTRAINT FOREIGN KEY (top_rght_widget) REFERENCES home_widgets(seq),
    CONSTRAINT FOREIGN KEY (bot_left_widget) REFERENCES home_widgets(seq),
    CONSTRAINT FOREIGN KEY (bot_rght_widget) REFERENCES home_widgets(seq)
);

CREATE TABLE access_requests(
    seq int not null primary key auto_increment,
    user_name  varchar(20)                            not null,
    first_name varchar(20)                            not null,
    last_name  varchar(20)                            not null,
    email      varchar(100)                           not null,
    title      varchar(6)                             not null
);

ALTER TABLE users ADD COLUMN home_page_seq INT;
ALTER TABLE users ADD CONSTRAINT FOREIGN KEY (home_page_seq) REFERENCES home_page_defn(seq);

COMMIT;