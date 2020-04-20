--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1
-- Dumped by pg_dump version 12.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: rprec_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA rprec_schema;


ALTER SCHEMA rprec_schema OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.articles (
    slug character varying(200) NOT NULL,
    author character varying(50) NOT NULL,
    text text,
    id integer NOT NULL
);


ALTER TABLE public.articles OWNER TO postgres;

--
-- Name: articles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.articles_id_seq OWNER TO postgres;

--
-- Name: articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.articles_id_seq OWNED BY public.articles.id;


--
-- Name: similar_articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.similar_articles (
    slug character varying(200),
    similar_slug character varying(200),
    cosine_similarity real,
    id integer NOT NULL
);


ALTER TABLE public.similar_articles OWNER TO postgres;

--
-- Name: similar_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.similar_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.similar_articles_id_seq OWNER TO postgres;

--
-- Name: similar_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.similar_articles_id_seq OWNED BY public.similar_articles.id;


--
-- Name: articles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.articles ALTER COLUMN id SET DEFAULT nextval('public.articles_id_seq'::regclass);


--
-- Name: similar_articles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.similar_articles ALTER COLUMN id SET DEFAULT nextval('public.similar_articles_id_seq'::regclass);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- Name: similar_articles similar_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.similar_articles
    ADD CONSTRAINT similar_articles_pkey PRIMARY KEY (id);


--
-- Name: articles unique_slug; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT unique_slug UNIQUE (slug);


--
-- Name: similar_articles similar_articles_slug_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.similar_articles
    ADD CONSTRAINT similar_articles_slug_fkey FOREIGN KEY (slug) REFERENCES public.articles(slug);


--
-- Name: similar_articles similar_slug_constraint; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.similar_articles
    ADD CONSTRAINT similar_slug_constraint FOREIGN KEY (similar_slug) REFERENCES public.articles(slug);


--
-- PostgreSQL database dump complete
--

