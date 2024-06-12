CREATE VIEW finance_hdr_summary AS
    SELECT
        H.seq,
        H.id,
        H.inv_date,
        concat_ws(' ', UA.first_name, UA.last_name) as 'CreatedBy',
        concat_ws(' ', UB.first_name, UB.last_name) as 'ApprovedBy',
        concat_ws(' ', UC.first_name, UC.last_name) as 'AddedBy',
        concat_ws(' ', UD.first_name, UD.last_name) as 'UpdatedBy',
        S.stat_desc as 'Status',
        T.type_desc as 'Type',
        (SELECT SUM( (
            SELECT item_cost.price FROM items,item_cost WHERE
        items.seq = item_cost.item_seq AND items.displayed = 1 AND
    eff_date = (
        SELECT MAX(eff_date) FROM item_cost B
        WHERE B.item_seq = items.seq AND B.eff_date <= H.inv_date )

                         ) * L.qty)
            FROM finance_line L WHERE L.finance_seq = H.seq) as 'Total'
    FROM
    finance_hdr H
        INNER JOIN finance_status S on H.stat_seq = S.seq
        INNER JOIN finance_type T on H.type_seq = T.seq
        LEFT JOIN users UA on H.created_by = UA.seq
        LEFT JOIN users UB on H.approved_by = UB.seq
        LEFT JOIN users UC on H.added_by = UC.seq
        LEFT JOIN users UD on H.updated_by = UD.seq;


CREATE VIEW docket_users AS
    SELECT
        distinct usr.*
    FROM
        users usr,
        class_assignments ca,
        perm_types pt,
        perms p
        WHERE
        ca.user_seq = usr.seq AND
        p.class_seq = ca.class_seq AND
        p.perm_seq = pt.seq AND
        pt.perm_desc IN ('doc_edit', 'doc_add', 'doc_admin', 'doc_view')


CREATE VIEW developer_emails AS
    SELECT
        A.email
    FROM
        users A,
        class_assignments B
    WHERE
        A.seq = B.user_seq
      AND
        B.class_seq = 6;