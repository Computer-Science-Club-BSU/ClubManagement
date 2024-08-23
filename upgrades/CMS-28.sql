CREATE TABLE links (
    seq int not null primary key auto_increment,
    link varchar(20) not null,
    eff_date timestamp default current_timestamp,
    redirect varchar(200) not null,
    visits int not null default 0,
    added_by int,
    added_dt datetime default current_timestamp,
    updated_by int,
    update_dt datetime default current_timestamp on update current_timestamp
);

ALTER TABLE links ADD UNIQUE (link, eff_date);
ALTER TABLE links ADD CONSTRAINT FOREIGN KEY (added_by) REFERENCES users(seq);
ALTER TABLE links ADD CONSTRAINT FOREIGN KEY (updated_by) REFERENCES users(seq);