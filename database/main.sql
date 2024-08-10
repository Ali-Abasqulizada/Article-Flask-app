CREATE DATABASE IF NOT EXISTS article;
USE article;

CREATE TABLE IF NOT EXISTS article.users (
    id INTEGER auto_increment NOT NULL,
    name TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    surname TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    email VARCHAR(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    password TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    CONSTRAINT users_pk PRIMARY KEY (id),
    CONSTRAINT users_unique UNIQUE KEY (email)
);

CREATE TABLE IF NOT EXISTS article.articles (
	id INTEGER auto_increment NOT NULL,
	title TEXT NOT NULL,
	content TEXT NOT NULL,
	email VARCHAR(225) NOT NULL,
	creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT articles_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS article.comments (
	id INTEGER auto_increment NOT NULL,
	article_id INTEGER NOT NULL,
	email VARCHAR(225) NOT NULL,
	content TEXT NOT NULL,
	creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT comments_pk PRIMARY KEY (id)
);