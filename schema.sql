--
-- PostgreSQL database dump
--

-- Dumped from database version 10.2
-- Dumped by pg_dump version 10.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: rprec_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA rprec_schema;


ALTER SCHEMA rprec_schema OWNER TO postgres;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE articles (
    slug character varying(200) NOT NULL,
    author character varying(50) NOT NULL,
    text text,
    id integer NOT NULL
);


ALTER TABLE articles OWNER TO postgres;

--
-- Name: articles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE articles_id_seq OWNER TO postgres;

--
-- Name: articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE articles_id_seq OWNED BY articles.id;


--
-- Name: similar_articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE similar_articles (
    slug character varying(200),
    similar_slug character varying(200),
    cosine_similarity real,
    id integer NOT NULL,
    doc2vec_similarity real
);


ALTER TABLE similar_articles OWNER TO postgres;

--
-- Name: similar_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE similar_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE similar_articles_id_seq OWNER TO postgres;

--
-- Name: similar_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE similar_articles_id_seq OWNED BY similar_articles.id;


--
-- Name: articles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY articles ALTER COLUMN id SET DEFAULT nextval('articles_id_seq'::regclass);


--
-- Name: similar_articles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY similar_articles ALTER COLUMN id SET DEFAULT nextval('similar_articles_id_seq'::regclass);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- Name: similar_articles similar_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY similar_articles
    ADD CONSTRAINT similar_articles_pkey PRIMARY KEY (id);


--
-- Name: articles unique_slug; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY articles
    ADD CONSTRAINT unique_slug UNIQUE (slug);


--
-- Name: similar_articles similar_articles_slug_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY similar_articles
    ADD CONSTRAINT similar_articles_slug_fkey FOREIGN KEY (slug) REFERENCES articles(slug);


--
-- Name: similar_articles similar_slug_constraint; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY similar_articles
    ADD CONSTRAINT similar_slug_constraint FOREIGN KEY (similar_slug) REFERENCES articles(slug);


--
-- PostgreSQL database dump complete
--

