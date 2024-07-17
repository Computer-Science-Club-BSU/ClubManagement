use management;

create or replace view docket_users as
select distinct `usr`.`seq`        AS `seq`,
                `usr`.`user_name`  AS `user_name`,
                `usr`.`first_name` AS `first_name`,
                `usr`.`last_name`  AS `last_name`,
                `usr`.`hash_pass`  AS `hash_pass`,
                `usr`.`email`      AS `email`,
                `usr`.`theme`      AS `theme`,
                `usr`.`title`      AS `title`,
                `usr`.`is_active`  AS `is_active`,
                `usr`.`added_by`   AS `added_by`,
                `usr`.`updated_by` AS `updated_by`,
                `usr`.`added_dt`   AS `added_dt`,
                `usr`.`update_dt`  AS `update_dt`
from `management`.`users` `usr`
         join `management`.`class_assignments` `ca`
         join `management`.`perm_types` `pt`
         join `management`.`perms` `p`
         join `management`.`terms` `tA`
         join `management`.`terms` `tB`
where `ca`.`user_seq` = `usr`.`seq`
  and `p`.`class_seq` = `ca`.`class_seq`
  and `p`.`perm_seq` = `pt`.`seq`
  AND `ca`.`start_term` = `tA`.`seq`
  AND `ca`.`end_term` = `tB`.`seq`
  AND `tA`.`start_date` <= current_date
  AND current_date <= `tB`.`end_date`
  and `pt`.`perm_desc` in ('doc_edit', 'doc_add', 'doc_admin', 'doc_view');


create or replace view developer_emails as
select `A`.`email` AS `email`
from `management`.`users` `A`
         join `management`.`class_assignments` `B`
where `A`.`seq` = `B`.`user_seq`
  and `B`.`class_seq` = 6;

create or replace view officer_lookup as
select `B`.`seq`           AS `assignment_seq`,
       `A`.`seq`           AS `user_seq`,
       `A`.`first_name`    AS `first_name`,
       `A`.`last_name`     AS `last_name`,
       `A`.`email`         AS `email`,
       `A`.`title`         AS `title`,
       `C`.`position_name` AS `position_name`,
       `dA`.`start_date`   AS `start_date`,
       `dB`.`end_date`     AS `end_date`
from ((((`management`.`users` `A` join `management`.`class_assignments` `B`) join `management`.`class` `C`) join `management`.`terms` `dA`) join `management`.`terms` `dB`)
where `A`.`seq` = `B`.`user_seq`
  and `C`.`seq` = `B`.`class_seq`
  and `B`.`start_term` = `dA`.`seq`
  and `B`.`end_term` = `dB`.`seq`;

CREATE OR REPLACE VIEW user_info_vw AS
SELECT a.seq, concat(a.first_name, ' ', a.last_name) as 'full_name',
       a.user_name, a.first_name, a.last_name, a.hash_pass, a.email,
       a.theme, b.title_desc as 'title', a.is_active, a.added_dt, a.update_dt, concat(c.first_name, ' ', c.last_name) as 'added_by',
       concat(d.first_name, ' ', d.last_name) as 'updated_by'
FROM users a LEFT JOIN users c ON (a.added_by = c.seq) LEFT JOIN users d ON (a.updated_by = d.seq), titles b WHERE a.title = b.seq;
