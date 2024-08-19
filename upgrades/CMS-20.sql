alter table docket_status add column edit_locked tinyint(1) default 0;


alter table finance_hdr add column process_state varchar(5) default 'U';
alter table finance_hdr add column process_dt datetime default NULL;
alter table finance_hdr add constraint unique (`id`);


DELIMITER ;;
CREATE OR REPLACE TRIGGER finance_approver_check_insert BEFORE INSERT ON finance_hdr
    FOR EACH ROW
    IF NEW.approved_by IS NOT NULL AND NOT EXISTS((
        SELECT
    *
FROM
    class_assignments A,
    terms tS,
    terms tE,
    perms P,
    perm_types pT
WHERE
    user_seq = NEW.approved_by
  AND
    tS.seq = A.start_term
  AND
    tE.seq = A.end_term
  AND
    P.class_seq = A.class_seq
  AND
    P.perm_seq = pT.seq
  AND
    (perm_desc = 'fin_approve' OR perm_desc = 'fin_admin')
  AND
    P.granted = 1
  AND
    NEW.inv_date BETWEEN tS.start_date AND tE.end_date
    )) THEN
        set @message_text = CONCAT('User_seq ', NEW.approved_by,
                                  'Cannot approve finances dated, ', DATE_FORMAT(NEW.inv_date, '%b %D, %Y'));
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = @message_text;
    end if;;
DELIMITER ;

DELIMITER ;;
CREATE OR REPLACE TRIGGER finance_approver_check_update BEFORE UPDATE ON finance_hdr
    FOR EACH ROW
    IF NEW.approved_by IS NOT NULL AND NOT EXISTS((
        SELECT
    *
FROM
    class_assignments A,
    terms tS,
    terms tE,
    perms P,
    perm_types pT
WHERE
    user_seq = NEW.approved_by
  AND
    tS.seq = A.start_term
  AND
    tE.seq = A.end_term
  AND
    P.class_seq = A.class_seq
  AND
    P.perm_seq = pT.seq
  AND
    (perm_desc = 'fin_approve' OR perm_desc = 'fin_admin')
  AND
    P.granted = 1
  AND
  NEW.inv_date BETWEEN tS.start_date AND tE.end_date
    )) THEN
        set @message_text = CONCAT('User_seq ', NEW.approved_by,
                                  'Cannot approve finances dated, ', DATE_FORMAT(NEW.inv_date, '%b %D, %Y'));
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = @message_text;
    end if ;;
DELIMITER ;

ALTER TABLE finance_line ADD CONSTRAINT `finance_line_ibfk_4` FOREIGN KEY (`finance_seq`) REFERENCES `finance_hdr` (`seq`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE items DROP COLUMN eff_date;
ALTER TABLE items DROP COLUMN eff_status;
ALTER TABLE items MODIFY vendor_seq INT AFTER item_vendor;


CREATE TABLE `themes` (
  `seq` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` char(36) DEFAULT NULL,
  `theme_desc` varchar(40) DEFAULT NULL,
  `added_by` int(11) DEFAULT NULL,
  `added_dt` datetime DEFAULT current_timestamp(),
  `updated_by` int(11) DEFAULT NULL,
  `update_dt` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`seq`),
  KEY `added_by` (`added_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `themes_ibfk_1` FOREIGN KEY (`added_by`) REFERENCES `users` (`seq`),
  CONSTRAINT `themes_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`seq`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

alter table users add CONSTRAINT `users_ibfk_4` FOREIGN KEY (`theme`) REFERENCES `themes` (`seq`);

DELIMITER ;;
CREATE OR REPLACE TRIGGER `check_new_title_seq` BEFORE UPDATE ON users
    for each row
    if NEW.title < 0 then
        set NEW.title = OLD.title;
    end if ;;
DELIMITER ;

ALTER TABLE vendors DROP COLUMN eff_status;
ALTER TABLE vendors DROP COLUMN eff_date;
ALTER TABLE vendors ADD COLUMN vend_status ENUM ('R', 'A', 'I') DEFAULT 'R';

CREATE VIEW `docket_users` AS
select distinct `usr`.`seq` AS `seq`,
`usr`.`user_name` AS `user_name`,
`usr`.`first_name` AS `first_name`,
`usr`.`last_name` AS `last_name`,
`usr`.`hash_pass` AS `hash_pass`,
`usr`.`email` AS `email`,
`usr`.`theme` AS `theme`,
`t`.`title_desc` AS `title`,
`usr`.`is_active` AS `is_active`,
`usr`.`added_by` AS `added_by`,
`usr`.`updated_by` AS `updated_by`,
`usr`.`added_dt` AS `added_dt`,
`usr`.`update_dt` AS `update_dt` from ((((((`users` `usr` join `class_assignments` `ca`) join `perm_types` `pt`) join `perms` `p`) join `terms` `tA`) join `terms` `tB`) join `titles` `t`) where `ca`.`user_seq` = `usr`.`seq` and `p`.`class_seq` = `ca`.`class_seq` and `p`.`perm_seq` = `pt`.`seq` and `ca`.`start_term` = `tA`.`seq` and `ca`.`end_term` = `tB`.`seq` and CURRENT_TIMESTAMP BETWEEN tA.start_date AND tB.end_date and `p`.`granted` = 1 and `pt`.`perm_desc` in ('doc_edit','doc_add','doc_admin','doc_view') and `usr`.`title` = `t`.`seq`;

CREATE OR REPLACE VIEW `finance_hdr_summary` AS select `A`.`seq` AS `seq`,`A`.`id` AS `id`,`A`.`inv_date` AS `inv_date`,`C`.`stat_desc` AS `stat_desc`,`D`.`type_desc` AS `type_desc`,concat(`UA`.`first_name`,' ',`UA`.`last_name`) AS `CreatedBy`,oracle_schema.decode(`A`.`is_approved`,1,concat(`UB`.`first_name`,' ',`UB`.`last_name`),0,NULL) AS `ApprovedBy`,concat(`UC`.`first_name`,' ',`UC`.`last_name`) AS `AddedBy`,concat(`UD`.`first_name`,' ',`UD`.`last_name`) AS `UpdatedBy`,ifnull(sum(`E`.`price` * `B`.`qty`),0) + `A`.`fees` + `A`.`tax` AS `Total` from ((((((((`finance_hdr` `A` left join `users` `UA` on(`A`.`created_by` = `UA`.`seq`)) left join `users` `UB` on(`A`.`approved_by` = `UB`.`seq`)) left join `users` `UC` on(`A`.`added_by` = `UC`.`seq`)) left join `users` `UD` on(`A`.`updated_by` = `UD`.`seq`)) left join `finance_line` `B` on(`A`.`seq` = `B`.`finance_seq`)) join `finance_status` `C` on(`A`.`stat_seq` = `C`.`seq`)) join `finance_type` `D` on(`A`.`type_seq` = `D`.`seq`)) left join `item_cost` `E` on(`B`.`item_id` = `E`.`seq`)) group by `A`.`seq` ;


CREATE OR REPLACE VIEW `user_info_vw` AS select `a`.`seq` AS `seq`,concat(`a`.`first_name`,' ',`a`.`last_name`) AS `full_name`,`a`.`user_name` AS `user_name`,`a`.`first_name` AS `first_name`,`a`.`last_name` AS `last_name`,`a`.`hash_pass` AS `hash_pass`,`a`.`email` AS `email`,`t`.`file_name` AS `theme`,`b`.`title_desc` AS `title`,`a`.`is_active` AS `is_active`,`a`.`added_dt` AS `added_dt`,`a`.`update_dt` AS `update_dt`,concat(`c`.`first_name`,' ',`c`.`last_name`) AS `added_by`,concat(`d`.`first_name`,' ',`d`.`last_name`) AS `updated_by` from ((((`users` `a` left join `users` `c` on(`a`.`added_by` = `c`.`seq`)) left join `users` `d` on(`a`.`updated_by` = `d`.`seq`)) join `titles` `b`) join `themes` `t` on(`a`.`theme` = `t`.`seq`)) where `a`.`title` = `b`.`seq` ;


CREATE OR REPLACE VIEW `finance_admin` AS select `A`.`seq` AS `seq`,`A`.`id` AS `id`,date_format(`A`.`inv_date`,'%b %D, %Y') AS `inv_date`,`E`.`full_name` AS `created_by`,`F`.`full_name` AS `approved_by`,`A`.`is_approved` AS `is_approved`,oracle_schema.decode(`A`.`process_state`,'U','Unrouted','R','Routed','S','Alerted','A','Approved','D','Denied',`A`.`process_state`) AS `process_state`,date_format(`A`.`process_dt`,'%b %D, %Y') AS `process_dt`,`G`.`full_name` AS `added_by`,date_format(`A`.`added_dt`,'%b %D, %Y') AS `added_dt`,`H`.`full_name` AS `updated_by`,date_format(`A`.`update_dt`,'%b %D, %Y') AS `update_dt`,`B`.`stat_desc` AS `status`,`C`.`type_desc` AS `type`,`D`.`Total` AS `balance` from (((((((`finance_hdr` `A` join `finance_status` `B` on(`A`.`stat_seq` = `B`.`seq`)) join `finance_type` `C` on(`A`.`type_seq` = `C`.`seq`)) join `finance_hdr_summary` `D` on(`A`.`seq` = `D`.`seq`)) left join `user_info_vw` `E` on(`A`.`created_by` = `E`.`seq`)) left join `user_info_vw` `F` on(`A`.`approved_by` = `F`.`seq`)) left join `user_info_vw` `G` on(`A`.`added_by` = `G`.`seq`)) left join `user_info_vw` `H` on(`A`.`updated_by` = `H`.`seq`));

create or replace trigger update_approver_flag before update on finance_hdr
    for each row
    IF OLD.approved_by != NEW.approved_by OR OLD.tax != NEW.tax OR OLD.fees != NEW.fees THEN
       SET NEW.is_approved = 0;
       SET NEW.process_state = 'R';
   end if;


ALTER TABLE items drop column item_vendor