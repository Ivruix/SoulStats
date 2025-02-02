CREATE TABLE user_data (
    user_id SERIAL PRIMARY KEY,
    username text UNIQUE,
    email text UNIQUE,
    password_hash text NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat (
  chat_id serial PRIMARY KEY,
  user_id integer,
  created_at date
);

CREATE TABLE message (
  message_id serial PRIMARY KEY,
  chat_id integer,
  created_at timestamp default current_timestamp,
  by_user boolean,
  content text
);

CREATE TABLE happiness_level (
  chat_id integer PRIMARY KEY,
  val integer
);

CREATE TABLE main_emotion (
  chat_id integer PRIMARY KEY,
  val text
);

CREATE TABLE fact (
  fact_id serial PRIMARY KEY,
  user_id integer,
  content text
);

CREATE TABLE event (
  event_id serial PRIMARY KEY,
  user_id integer,
  happens_at date,
  content text
);

ALTER TABLE event ADD FOREIGN KEY (user_id) REFERENCES user_data (user_id);

ALTER TABLE fact ADD FOREIGN KEY (user_id) REFERENCES user_data (user_id);

ALTER TABLE chat ADD FOREIGN KEY (user_id) REFERENCES user_data (user_id);

ALTER TABLE message ADD FOREIGN KEY (chat_id) REFERENCES chat (chat_id);

ALTER TABLE happiness_level ADD FOREIGN KEY (chat_id) REFERENCES chat (chat_id);

ALTER TABLE main_emotion ADD FOREIGN KEY (chat_id) REFERENCES chat (chat_id);
