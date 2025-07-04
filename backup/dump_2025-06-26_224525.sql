--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 17.5 (Debian 17.5-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    filename text NOT NULL,
    original_name text NOT NULL,
    size integer NOT NULL,
    upload_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    file_type text NOT NULL
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, filename, original_name, size, upload_time, file_type) FROM stdin;
1	3a3802350848430.jpeg	cat.jpeg	26	2025-06-26 15:38:39.98105	jpeg
2	d528828cfb2240d.jpg	quirrel.jpg	18	2025-06-26 15:38:42.72098	jpg
4	59cf655a4bb54f6.jpg	quirrel.jpg	18	2025-06-26 15:39:07.399306	jpg
5	9bb90ce8cc6741a.gif	hamster.gif	176	2025-06-26 15:39:18.150971	gif
6	b1de606028af4a7.png	dog.png	145	2025-06-26 15:39:20.139885	png
7	a9422700f736461.jpg	lion.jpg	13	2025-06-26 15:39:22.009695	jpg
9	1debfcb083264d3.jpeg	cat.jpeg	26	2025-06-26 15:39:26.209276	jpeg
10	05646a750a74454.png	dog.png	145	2025-06-26 15:39:28.219861	png
11	f7e75937810b49a.gif	hamster.gif	176	2025-06-26 15:39:32.558495	gif
12	a0a8199c57fc4af.jpg	quirrel.jpg	18	2025-06-26 15:39:34.988151	jpg
17	7fe06c43a61a480.gif	hamster.gif	176	2025-06-26 15:40:19.963819	gif
18	7e17e1381d7443b.png	dog.png	145	2025-06-26 15:40:22.017025	png
19	ae9f45930243495.gif	hamster.gif	176	2025-06-26 15:40:23.737786	gif
20	ea147d233f3c4be.jpg	lion.jpg	13	2025-06-26 15:40:25.399314	jpg
21	8999039d25b9413.png	dog.png	145	2025-06-26 15:40:27.227287	png
22	d6db59fefff54b2.gif	hamster.gif	176	2025-06-26 15:40:31.656064	gif
23	5651a8a9c1e54f9.png	dog.png	145	2025-06-26 15:40:33.305698	png
24	51157451b4934c0.jpeg	cat.jpeg	26	2025-06-26 15:40:44.005354	jpeg
25	db0d3a716ead467.jpg	quirrel.jpg	18	2025-06-26 15:40:46.155163	jpg
26	24b5c65bae33462.jpg	lion.jpg	13	2025-06-26 15:40:48.175147	jpg
\.


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 29, true);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

