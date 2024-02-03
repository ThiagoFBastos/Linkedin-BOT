#!/usr/bin/env python3

from jobs import write_jobs
from dependencies import write_dependencies
from variants import write_variants
from jobs_keywords import write_jobs_keywords
from keywords import write_keywords

template = \
"""
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS variants;
DROP TABLE IF EXISTS dependencies;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS jobs_keywords;

CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE variants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    keyword_id INT NOT NULL
);

CREATE TABLE dependencies (
    parent_keyword_id INT NOT NULL,
    child_keyword_id INT NOT NULL
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    weight SMALLINT NOT NULL
);

CREATE TABLE jobs_keywords (
    job_id INT NOT NULL,
    key_id INT NOT NULL
);

-- inserindo valores na tabela keywords
{}

-- inserindo valores na tabela variants
{}

-- inserindo as dependências entre as keywords
{}

-- inserindo as informações dos jobs posts
{}

-- inserindo as relações entre jobs e keywords
{}

ALTER TABLE variants
    ADD CONSTRAINT fk_keywords_variants FOREIGN KEY (keyword_id) REFERENCES keywords (id);

ALTER TABLE dependencies
    ADD CONSTRAINT fk_keywords_keywords_parent FOREIGN KEY (parent_keyword_id) REFERENCES keywords (id);

ALTER TABLE dependencies
    ADD CONSTRAINT fk_keywords_keywords_child FOREIGN KEY (child_keyword_id) REFERENCES keywords (id);

ALTER TABLE jobs_keywords
    ADD CONSTRAINT fk_jobs_keywords_job FOREIGN KEY (job_id) REFERENCES jobs (id);

ALTER TABLE jobs_keywords
    ADD CONSTRAINT fk_jobs_keywords_key FOREIGN KEY (key_id) REFERENCES keywords (id);
"""

with open('../models/linkedin.sql', 'w') as fp:
    keywords = write_keywords()
    jobs = write_jobs()
    variants = write_variants()
    dependencies = write_dependencies()
    jobs_keywords = write_jobs_keywords()
    template = template.format(keywords, variants, dependencies, jobs, jobs_keywords)
    fp.write(f'{template}\n')
