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
                `usr`.`manager`    AS `manager`,
                `usr`.`is_active`  AS `is_active`,
                `usr`.`added_by`   AS `added_by`,
                `usr`.`updated_by` AS `updated_by`,
                `usr`.`added_dt`   AS `added_dt`,
                `usr`.`update_dt`  AS `update_dt`
from `management`.`users` `usr`
         join `management`.`class_assignments` `ca`
         join `management`.`perm_types` `pt`
         join `management`.`perms` `p`
where `ca`.`user_seq` = `usr`.`seq`
  and `p`.`class_seq` = `ca`.`class_seq`
  and `p`.`perm_seq` = `pt`.`seq`
  and `pt`.`perm_desc` in ('doc_edit', 'doc_add', 'doc_admin', 'doc_view');

create or replace view finance_hdr_summary as
select `H`.`seq`                                           AS `seq`,
       `H`.`id`                                            AS `id`,
       `H`.`inv_date`                                      AS `inv_date`,
       concat_ws(' ', `UA`.`first_name`, `UA`.`last_name`) AS `CreatedBy`,
       concat_ws(' ', `UB`.`first_name`, `UB`.`last_name`) AS `ApprovedBy`,
       concat_ws(' ', `UC`.`first_name`, `UC`.`last_name`) AS `AddedBy`,
       concat_ws(' ', `UD`.`first_name`, `UD`.`last_name`) AS `UpdatedBy`,
       `S`.`stat_desc`                                     AS `Status`,
       `T`.`type_desc`                                     AS `Type`,
       (select sum((select `management`.`item_cost`.`price`
                    from `management`.`items`
                             join `management`.`item_cost`
                    where `management`.`items`.`seq` = `management`.`item_cost`.`item_seq`
                      and `management`.`items`.`displayed` = 1
                      and `management`.`item_cost`.`eff_date` = (select max(`B`.`eff_date`)
                                                                 from `management`.`item_cost` `B`
                                                                 where `B`.`item_seq` = `management`.`items`.`seq`
                                                                   and `B`.`eff_date` <= `H`.`inv_date`)) * `L`.`qty`)
        from `management`.`finance_line` `L`
        where `L`.`finance_seq` = `H`.`seq`)               AS `Total`
from ((((((`management`.`finance_hdr` `H` join `management`.`finance_status` `S`
           on (`H`.`stat_seq` = `S`.`seq`)) join `management`.`finance_type` `T`
          on (`H`.`type_seq` = `T`.`seq`)) left join `management`.`users` `UA`
         on (`H`.`created_by` = `UA`.`seq`)) left join `management`.`users` `UB`
        on (`H`.`approved_by` = `UB`.`seq`)) left join `management`.`users` `UC`
       on (`H`.`added_by` = `UC`.`seq`)) left join `management`.`users` `UD` on (`H`.`updated_by` = `UD`.`seq`));

create or replace view developer_emails as
select `A`.`email` AS `email`
from `management`.`users` `A`
         join `management`.`class_assignments` `B`
where `A`.`seq` = `B`.`user_seq`
  and `B`.`class_seq` = 6;
