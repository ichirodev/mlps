CREATE DATABASE drugdb;

CREATE TABLE drug(
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name varchar(128),
	url varchar(128),
	purpose longtext
);

