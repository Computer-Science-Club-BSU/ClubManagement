CREATE OR REPLACE VIEW user_info_vw AS
    select `a`.`seq`                                      AS `seq`,
       concat(`a`.`first_name`, ' ', `a`.`last_name`) AS `full_name`,
       `a`.`user_name`                                AS `user_name`,
       `a`.`first_name`                               AS `first_name`,
       `a`.`last_name`                                AS `last_name`,
       `a`.`hash_pass`                                AS `hash_pass`,
       `a`.`email`                                    AS `email`,
       `t`.`file_name`                                AS `theme`,
       `t`.`theme_desc`                               AS `theme_desc`,
       `b`.`title_desc`                               AS `title`,
       `a`.`is_active`                                AS `is_active`,
       `a`.`added_dt`                                 AS `added_dt`,
       `a`.`update_dt`                                AS `update_dt`,
       concat(`c`.`first_name`, ' ', `c`.`last_name`) AS `added_by`,
       concat(`d`.`first_name`, ' ', `d`.`last_name`) AS `updated_by`
from ((((`management`.`users` `a` left join `management`.`users` `c`
         on (`a`.`added_by` = `c`.`seq`)) left join `management`.`users` `d`
        on (`a`.`updated_by` = `d`.`seq`)) join `management`.`titles` `b`) join `management`.`themes` `t`
      on (`a`.`theme` = `t`.`seq`))
where `a`.`title` = `b`.`seq`;

create OR REPLACE view user_audit as
select `a`.`seq`                                                                                        AS `seq`,
       `a`.`added_by`                                                                                   AS `added_by`,
       `a`.`updated_by`                                                                                 AS `updated_by`,
       `a`.`added_dt`                                                                                   AS `added_dt`,
       `a`.`update_dt`                                                                                  AS `updated_dt`,
       (select count(`f`.`seq`)
        from (`management`.`api_tokens` `b` join `management`.`api_keys` `f`)
        where `a`.`seq` = `f`.`granted_to`
          and `b`.`api_key_seq` = `f`.`seq`)                                                            AS `active_keys`,
       (select count(`c`.`seq`)
        from `management`.`finance_hdr` `c`
        where `c`.`created_by` = `a`.`seq`)                                                             AS `created_finances`,
       (select count(`d`.`seq`)
        from `management`.`finance_hdr` `d`
        where `d`.`approved_by` = `a`.`seq`
          and `d`.`is_approved` = 1)                                                                    AS `approved_records`,
       (select count(`e`.`seq`)
        from `management`.`docket_hdr` `e`
        where `e`.`added_by` = `a`.`seq`)                                                               AS `docket_count`,
       concat_ws('/', `c`.`continent`, `c`.`region`, `c`.`sub_region`)                                  AS `timezone`,
       date_format(current_timestamp(), `d`.`date_format`)                                              AS `date_format`,
       date_format(current_timestamp(), `d`.`time_format`)                                              AS `time_format`,
       date_format(current_timestamp(), `d`.`datetime_format`)                                          AS `datetime_format`,
       d.seq                                                                                            AS 'format_seq'
from (((`management`.`user_info_vw` `a` join `management`.`users` `b`) join `management`.`timezones` `c`) join `management`.`datetime_formats` `d`)
where `a`.`seq` = `b`.`seq`
  and `b`.`timezone` = `c`.`seq`
  and `b`.`date_format` = `d`.`seq`
order by `a`.`seq`;


CREATE TABLE timezones(
    seq int not null primary key auto_increment,
    continent varchar(20) not null,
    region varchar(20),
    sub_region varchar(20)
);
ALTER TABLE timezones ADD UNIQUE (continent, region, sub_region);


ALTER TABLE users ADD COLUMN date_format INT AFTER timezone;

ALTER TABLE users ADD CONSTRAINT FOREIGN KEY (date_format) REFERENCES datetime_formats(seq);

ALTER TABLE users ADD COLUMN timezone int AFTER theme;

ALTER TABLE users ADD CONSTRAINT FOREIGN KEY (timezone) references timezones(seq);

CREATE TABLE datetime_formats (
    seq int not null primary key auto_increment,
    date_format varchar(30),
    time_format varchar(30),
    datetime_format varchar(30)
);

select `A`.`seq`                                           AS `seq`,
       `A`.`id`                                            AS `id`,
`A`.`inv_date`AS `inv_date`,
       `E`.`full_name`                                     AS `created_by`,
       `F`.`full_name`                                     AS `approved_by`,
       `A`.`is_approved`                                   AS `is_approved`,
       oracle_schema.decode(`A`.`process_state`, 'U', 'Unrouted', 'R', 'Routed', 'S', 'Alerted', 'A', 'Approved', 'D',
                            'Denied', `A`.`process_state`) AS `process_state`,
       date_format(`A`.`process_dt`, '%b %D, %Y')          AS `process_dt`,
       `G`.`full_name`                                     AS `added_by`,
       date_format(`A`.`added_dt`, '%b %D, %Y')            AS `added_dt`,
       `H`.`full_name`                                     AS `updated_by`,
       date_format(`A`.`update_dt`, '%b %D, %Y')           AS `update_dt`,
       `B`.`stat_desc`                                     AS `status`,
       `C`.`type_desc`                                     AS `type`,
       `D`.`Total`                                         AS `balance`
from (((((((`management`.`finance_hdr` `A` join `management`.`finance_status` `B`
            on (`A`.`stat_seq` = `B`.`seq`)) join `management`.`finance_type` `C`
           on (`A`.`type_seq` = `C`.`seq`)) join `management`.`finance_hdr_summary` `D`
          on (`A`.`seq` = `D`.`seq`)) left join `management`.`user_info_vw` `E`
         on (`A`.`created_by` = `E`.`seq`)) left join `management`.`user_info_vw` `F`
        on (`A`.`approved_by` = `F`.`seq`)) left join `management`.`user_info_vw` `G`
       on (`A`.`added_by` = `G`.`seq`)) left join `management`.`user_info_vw` `H` on (`A`.`updated_by` = `H`.`seq`))


ALTER TABLE users DROP CONSTRAINT user_full_name_unq;
