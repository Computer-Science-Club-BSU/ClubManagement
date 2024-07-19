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

create view finance_hdr_summary as
select `A`.`seq`                                             AS `seq`,
       `A`.`id`                                              AS `id`,
       `A`.`inv_date`                                        AS `inv_date`,
       `C`.`stat_desc`                                       AS `stat_desc`,
       `D`.`type_desc`                                       AS `type_desc`,
       concat(`UA`.`first_name`, ' ', `UA`.`last_name`)      AS `CreatedBy`,
       concat(`UB`.`first_name`, ' ', `UB`.`last_name`)      AS `ApprovedBy`,
       concat(`UC`.`first_name`, ' ', `UC`.`last_name`)      AS `AddedBy`,
       concat(`UD`.`first_name`, ' ', `UD`.`last_name`)      AS `UpdatedBy`,
       sum(`E`.`price` * `B`.`qty`) + `A`.`fees` + `A`.`tax` AS `Total`
from ((((((((`management`.`finance_hdr` `A` left join `management`.`users` `UA`
             on (`A`.`created_by` = `UA`.`seq`)) left join `management`.`users` `UB`
            on (`A`.`approved_by` = `UB`.`seq`)) left join `management`.`users` `UC`
           on (`A`.`added_by` = `UC`.`seq`)) left join `management`.`users` `UD`
          on (`A`.`updated_by` = `UD`.`seq`)) join `management`.`finance_line` `B`
         on (`A`.`seq` = `B`.`finance_seq`)) join `management`.`finance_status` `C`
        on (`A`.`stat_seq` = `C`.`seq`)) join `management`.`finance_type` `D`
       on (`A`.`type_seq` = `D`.`seq`)) join `management`.`item_cost` `E` on (`B`.`item_id` = `E`.`seq`))
group by `A`.`seq`;

create or replace view current_position AS
    SELECT A.seq AS 'user_seq', C.position_name
    FROM user_info_vw A, class_assignments B, class C, terms tA, terms tB
    WHERE A.seq = B.user_seq AND B.class_seq = C.seq AND B.start_term = tA.seq AND B.end_term = tB.seq
AND tA.start_date <= current_date AND current_date <= tB.end_date;

