CREATE TABLE password_reset(
  seq int primary key auto_increment,
  user_seq int not null,
  password_token char(36),
  added_dt datetime default current_timestamp,
  added_by_user int,
  added_by_addr varchar(15),
  CONSTRAINT FOREIGN KEY (user_seq) REFERENCES users(seq)
);