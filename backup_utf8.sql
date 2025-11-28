--
-- PostgreSQL database dump
--

\restrict hGOMGMKWBMofiMlgybVezRCLL1yKIFKGkNmmcfvcARqNkumuabUdeTkUctVIuAA

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


--
-- Name: set_brigade_status_on_section_change(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_brigade_status_on_section_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

  -- 1) ╨┐╨╛╨┐╨╡╤А╨╡╨┤╨╜╤П ╨▒╤А╨╕╨│╨░╨┤╨░ (╨┐╤А╨╕ UPDATE/DELETE)

  IF TG_OP IN ('UPDATE','DELETE') AND OLD.brigade_id IS NOT NULL THEN

    IF NOT EXISTS (

      SELECT 1 FROM sections

      WHERE brigade_id = OLD.brigade_id AND end_date IS NULL

    ) THEN

      UPDATE brigades SET status = '╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░' WHERE id = OLD.brigade_id;

    END IF;

  END IF;



  -- 2) ╨╜╨╛╨▓╨░ ╨▒╤А╨╕╨│╨░╨┤╨░ (╨┐╤А╨╕ INSERT/UPDATE)

  IF TG_OP IN ('INSERT','UPDATE') AND NEW.brigade_id IS NOT NULL THEN

    IF NEW.end_date IS NULL THEN

      UPDATE brigades SET status = '╨Р╨║╤В╨╕╨▓╨╜╨░' WHERE id = NEW.brigade_id;

    ELSE

      IF NOT EXISTS (

        SELECT 1 FROM sections

        WHERE brigade_id = NEW.brigade_id AND end_date IS NULL

      ) THEN

        UPDATE brigades SET status = '╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░' WHERE id = NEW.brigade_id;

      END IF;

    END IF;

  END IF;



  RETURN NEW;

END;

$$;


ALTER FUNCTION public.set_brigade_status_on_section_change() OWNER TO postgres;

--
-- Name: trg_decrease_stock_on_usage_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_decrease_stock_on_usage_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

DECLARE

    cur_price NUMERIC(10,2);

BEGIN

    -- ╨Я╨╡╤А╨╡╨▓╤Ц╤А╨║╨░ ╨╖╨░╨╗╨╕╤И╨║╤Г

    IF (SELECT count FROM materials WHERE id = NEW.material_id) < NEW.quantity THEN

        RAISE EXCEPTION '╨Э╨╡╨┤╨╛╤Б╤В╨░╤В╨╜╤Ц╨╣ ╨╖╨░╨╗╨╕╤И╨╛╨║ ╨╝╨░╤В╨╡╤А╤Ц╨░╨╗╤Г (id=%) ╨┤╨╗╤П ╤Б╨┐╨╕╤Б╨░╨╜╨╜╤П: ╨┐╨╛╤В╤А╤Ц╨▒╨╜╨╛ %, ╤Ф %',

            NEW.material_id, NEW.quantity, (SELECT count FROM materials WHERE id = NEW.material_id);

    END IF;



    SELECT price INTO cur_price FROM materials WHERE id = NEW.material_id;



    UPDATE materials

       SET count = count - NEW.quantity

     WHERE id = NEW.material_id;



    UPDATE material_usage_items

       SET total_price = NEW.quantity * cur_price

     WHERE id = NEW.id;



    RETURN NEW;

END;

$$;


ALTER FUNCTION public.trg_decrease_stock_on_usage_fn() OWNER TO postgres;

--
-- Name: trg_increase_stock_on_delivery_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_increase_stock_on_delivery_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    UPDATE materials

       SET count = count + NEW.quantity,

           price = NEW.price_per_unit     -- ╨╛╨╜╨╛╨▓╨╗╤О╤Ф╨╝╨╛ ╨┐╨╛╤В╨╛╤З╨╜╤Г ╤Б╨║╨╗╨░╨┤╤Б╤М╨║╤Г ╤Ж╤Ц╨╜╤Г ╨╛╤Б╤В╨░╨╜╨╜╤М╨╛╤О ╨╖╨░╨║╤Г╨┐╤Ц╨▓╨╡╨╗╤М╨╜╨╛╤О

     WHERE id = NEW.material_id;

    RETURN NEW;

END;

$$;


ALTER FUNCTION public.trg_increase_stock_on_delivery_fn() OWNER TO postgres;

--
-- Name: trg_log_brigade_status_change_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_log_brigade_status_change_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    IF NEW.status IS DISTINCT FROM OLD.status THEN

        INSERT INTO brigade_status_history (brigade_id, old_status, new_status, changed_by)

        VALUES (OLD.id, OLD.status, NEW.status, NULL);

    END IF;

    RETURN NEW;

END;

$$;


ALTER FUNCTION public.trg_log_brigade_status_change_fn() OWNER TO postgres;

--
-- Name: trg_update_delivery_total_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_update_delivery_total_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    UPDATE deliveries d

       SET total_amount = (

           SELECT COALESCE(SUM(total_price),0)

             FROM delivery_items di

            WHERE di.delivery_id = d.id

       )

     WHERE d.id = NEW.delivery_id;

    RETURN NEW;

END;

$$;


ALTER FUNCTION public.trg_update_delivery_total_fn() OWNER TO postgres;

--
-- Name: update_total_cost(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_total_cost() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    -- ╨Я╤Ц╨┤╤А╨░╤Е╤Г╨╜╨╛╨║ ╨▓╨░╤А╤В╨╛╤Б╤В╤Ц

    SELECT price INTO STRICT NEW.total_cost

    FROM materials

    WHERE id = NEW.material_id;



    NEW.total_cost := NEW.total_cost * NEW.quantity;

    RETURN NEW;

END;

$$;


ALTER FUNCTION public.update_total_cost() OWNER TO postgres;

--
-- Name: update_work_total_cost(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_work_total_cost() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    SELECT cost_per_unit INTO STRICT NEW.total_cost

    FROM work_types

    WHERE id = NEW.work_type_id;



    NEW.total_cost := NEW.total_cost * NEW.volume;

    RETURN NEW;

END;

$$;


ALTER FUNCTION public.update_work_total_cost() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts_keys (
    id bigint CONSTRAINT accounts_customuser_id_not_null NOT NULL,
    username character varying(150) CONSTRAINT accounts_customuser_username_not_null NOT NULL,
    password_hash character varying(255) CONSTRAINT accounts_customuser_password_hash_not_null NOT NULL,
    role character varying(20) CONSTRAINT accounts_customuser_role_not_null NOT NULL,
    created_at timestamp with time zone CONSTRAINT accounts_customuser_created_at_not_null NOT NULL,
    reset_code character varying(10)
);


ALTER TABLE public.accounts_keys OWNER TO postgres;

--
-- Name: accounts_customuser_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.accounts_keys ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_guestrequest; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts_guestrequest (
    id bigint NOT NULL,
    message text NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    user_id bigint NOT NULL
);


ALTER TABLE public.accounts_guestrequest OWNER TO postgres;

--
-- Name: accounts_guestrequest_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.accounts_guestrequest ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_guestrequest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: brigade_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brigade_assignments (
    id integer NOT NULL,
    brigade_id integer NOT NULL,
    section_id integer NOT NULL,
    assigned_at date DEFAULT CURRENT_DATE,
    unassigned_at date,
    notes text
);


ALTER TABLE public.brigade_assignments OWNER TO postgres;

--
-- Name: brigade_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.brigade_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.brigade_assignments_id_seq OWNER TO postgres;

--
-- Name: brigade_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.brigade_assignments_id_seq OWNED BY public.brigade_assignments.id;


--
-- Name: brigade_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brigade_members (
    brigade_id integer NOT NULL,
    employee_id integer NOT NULL,
    role character varying(100),
    start_date date DEFAULT CURRENT_DATE,
    end_date date
);


ALTER TABLE public.brigade_members OWNER TO postgres;

--
-- Name: brigade_status_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brigade_status_history (
    id integer NOT NULL,
    brigade_id integer NOT NULL,
    old_status character varying(50),
    new_status character varying(50) NOT NULL,
    changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    changed_by integer,
    CONSTRAINT brigade_status_history_new_status_check CHECK (((new_status)::text = ANY ((ARRAY['╨Р╨║╤В╨╕╨▓╨╜╨░'::character varying, '╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░'::character varying])::text[])))
);


ALTER TABLE public.brigade_status_history OWNER TO postgres;

--
-- Name: brigade_status_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.brigade_status_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.brigade_status_history_id_seq OWNER TO postgres;

--
-- Name: brigade_status_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.brigade_status_history_id_seq OWNED BY public.brigade_status_history.id;


--
-- Name: brigade_work_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brigade_work_history (
    id integer NOT NULL,
    brigade_id integer NOT NULL,
    section_work_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date
);


ALTER TABLE public.brigade_work_history OWNER TO postgres;

--
-- Name: brigade_work_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.brigade_work_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.brigade_work_history_id_seq OWNER TO postgres;

--
-- Name: brigade_work_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.brigade_work_history_id_seq OWNED BY public.brigade_work_history.id;


--
-- Name: brigades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brigades (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    leader_id integer,
    notes text,
    status character varying(50) DEFAULT '╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░'::character varying,
    CONSTRAINT brigades_status_check CHECK (((status)::text = ANY ((ARRAY['╨Р╨║╤В╨╕╨▓╨╜╨░'::character varying, '╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░'::character varying])::text[])))
);


ALTER TABLE public.brigades OWNER TO postgres;

--
-- Name: brigades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.brigades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.brigades_id_seq OWNER TO postgres;

--
-- Name: brigades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.brigades_id_seq OWNED BY public.brigades.id;


--
-- Name: construction_sites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.construction_sites (
    id integer NOT NULL,
    management_id integer,
    name character varying(255) NOT NULL,
    address text NOT NULL,
    start_date date NOT NULL,
    end_date date,
    responsible_engineer_id integer,
    status character varying(50) DEFAULT '╨Т ╨┐╤А╨╛╤Ж╨╡╤Б╤Ц'::character varying,
    notes text,
    deadline date,
    CONSTRAINT construction_sites_status_check CHECK (((status)::text = ANY ((ARRAY['╨Я╨╗╨░╨╜╤Г╤Ф╤В╤М╤Б╤П'::character varying, '╨Т ╨┐╤А╨╛╤Ж╨╡╤Б╤Ц'::character varying, '╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛'::character varying, '╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛ ╤Ц╨╖ ╨╖╨░╨┐╤Ц╨╖╨╜╨╡╨╜╨╜╤П╨╝'::character varying])::text[])))
);


ALTER TABLE public.construction_sites OWNER TO postgres;

--
-- Name: construction_sites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.construction_sites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.construction_sites_id_seq OWNER TO postgres;

--
-- Name: construction_sites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.construction_sites_id_seq OWNED BY public.construction_sites.id;


--
-- Name: deliveries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deliveries (
    id integer NOT NULL,
    supplier_id integer,
    delivery_date date DEFAULT CURRENT_DATE NOT NULL,
    total_amount numeric(12,2),
    notes text,
    section_id integer,
    CONSTRAINT deliveries_total_amount_check CHECK ((total_amount >= (0)::numeric))
);


ALTER TABLE public.deliveries OWNER TO postgres;

--
-- Name: deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deliveries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deliveries_id_seq OWNER TO postgres;

--
-- Name: deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deliveries_id_seq OWNED BY public.deliveries.id;


--
-- Name: delivery_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.delivery_items (
    id integer NOT NULL,
    delivery_id integer NOT NULL,
    material_id integer NOT NULL,
    quantity numeric(10,2) NOT NULL,
    price_per_unit numeric(10,2) NOT NULL,
    total_price numeric(12,2) GENERATED ALWAYS AS ((quantity * price_per_unit)) STORED,
    CONSTRAINT delivery_items_price_per_unit_check CHECK ((price_per_unit > (0)::numeric)),
    CONSTRAINT delivery_items_quantity_check CHECK ((quantity > (0)::numeric))
);


ALTER TABLE public.delivery_items OWNER TO postgres;

--
-- Name: delivery_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.delivery_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.delivery_items_id_seq OWNER TO postgres;

--
-- Name: delivery_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.delivery_items_id_seq OWNED BY public.delivery_items.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    father_name character varying(255),
    birthday date NOT NULL,
    start_date date NOT NULL,
    end_date date,
    salary numeric(10,2) NOT NULL,
    position_id integer NOT NULL,
    category character varying(50) NOT NULL,
    CONSTRAINT employees_category_check CHECK (((category)::text = ANY ((ARRAY['╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕'::character varying, '╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗'::character varying])::text[]))),
    CONSTRAINT employees_salary_check CHECK ((salary > (0)::numeric))
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    status character varying(20) DEFAULT '╨Т╤Ц╨╗╤М╨╜╨░'::character varying,
    notes text,
    assigned_site_id integer,
    type_id integer,
    CONSTRAINT equipment_status_check CHECK (((status)::text = ANY ((ARRAY['╨Т╤Ц╨╗╤М╨╜╨░'::character varying, '╨Т ╤А╨╛╨▒╨╛╤В╤Ц'::character varying, '╨Т ╤А╨╡╨╝╨╛╨╜╤В╤Ц'::character varying])::text[])))
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_id_seq OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- Name: equipment_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_types (
    id integer NOT NULL,
    title character varying(255) NOT NULL
);


ALTER TABLE public.equipment_types OWNER TO postgres;

--
-- Name: equipment_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_types_id_seq OWNER TO postgres;

--
-- Name: equipment_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_types_id_seq OWNED BY public.equipment_types.id;


--
-- Name: equipment_work_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_work_history (
    id integer NOT NULL,
    equipment_id integer NOT NULL,
    site_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date,
    notes text
);


ALTER TABLE public.equipment_work_history OWNER TO postgres;

--
-- Name: equipment_work_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_work_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_work_history_id_seq OWNER TO postgres;

--
-- Name: equipment_work_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_work_history_id_seq OWNED BY public.equipment_work_history.id;


--
-- Name: managements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.managements (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    head_employee_id integer,
    notes text
);


ALTER TABLE public.managements OWNER TO postgres;

--
-- Name: managements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.managements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.managements_id_seq OWNER TO postgres;

--
-- Name: managements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.managements_id_seq OWNED BY public.managements.id;


--
-- Name: material_plan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material_plan (
    id integer NOT NULL,
    section_id integer NOT NULL,
    material_id integer NOT NULL,
    planned_qty numeric(10,2) NOT NULL,
    CONSTRAINT material_plan_planned_qty_check CHECK ((planned_qty >= (0)::numeric))
);


ALTER TABLE public.material_plan OWNER TO postgres;

--
-- Name: material_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.material_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_plan_id_seq OWNER TO postgres;

--
-- Name: material_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.material_plan_id_seq OWNED BY public.material_plan.id;


--
-- Name: material_usage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material_usage (
    id integer NOT NULL,
    section_id integer NOT NULL,
    material_id integer NOT NULL,
    used_qty numeric(10,2) NOT NULL,
    CONSTRAINT material_usage_used_qty_check CHECK ((used_qty >= (0)::numeric))
);


ALTER TABLE public.material_usage OWNER TO postgres;

--
-- Name: material_usage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.material_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_usage_id_seq OWNER TO postgres;

--
-- Name: material_usage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.material_usage_id_seq OWNED BY public.material_usage.id;


--
-- Name: material_usage_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material_usage_items (
    id integer NOT NULL,
    usage_id integer NOT NULL,
    material_id integer NOT NULL,
    quantity numeric(10,2) NOT NULL,
    total_price numeric(12,2),
    CONSTRAINT material_usage_items_quantity_check CHECK ((quantity > (0)::numeric))
);


ALTER TABLE public.material_usage_items OWNER TO postgres;

--
-- Name: material_usage_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.material_usage_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_usage_items_id_seq OWNER TO postgres;

--
-- Name: material_usage_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.material_usage_items_id_seq OWNED BY public.material_usage_items.id;


--
-- Name: material_usages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material_usages (
    id integer NOT NULL,
    usage_date date DEFAULT CURRENT_DATE NOT NULL,
    section_id integer NOT NULL,
    responsible_employee_id integer,
    notes text
);


ALTER TABLE public.material_usages OWNER TO postgres;

--
-- Name: material_usages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.material_usages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_usages_id_seq OWNER TO postgres;

--
-- Name: material_usages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.material_usages_id_seq OWNED BY public.material_usages.id;


--
-- Name: materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.materials (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    supplier_id integer NOT NULL,
    price numeric(10,2) NOT NULL,
    count numeric(10,2) NOT NULL,
    unit_id integer NOT NULL,
    CONSTRAINT materials_count_check CHECK ((count >= (0)::numeric)),
    CONSTRAINT materials_price_check CHECK ((price > (0)::numeric))
);


ALTER TABLE public.materials OWNER TO postgres;

--
-- Name: materials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materials_id_seq OWNER TO postgres;

--
-- Name: materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.materials_id_seq OWNED BY public.materials.id;


--
-- Name: plan_materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_materials (
    id integer NOT NULL,
    plan_id integer NOT NULL,
    material_id integer NOT NULL,
    required_qty numeric(12,2) NOT NULL,
    CONSTRAINT plan_materials_required_qty_check CHECK ((required_qty >= (0)::numeric))
);


ALTER TABLE public.plan_materials OWNER TO postgres;

--
-- Name: plan_materials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.plan_materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plan_materials_id_seq OWNER TO postgres;

--
-- Name: plan_materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.plan_materials_id_seq OWNED BY public.plan_materials.id;


--
-- Name: positions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.positions (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    description text,
    category character varying(50) NOT NULL,
    CONSTRAINT chk_positions_category CHECK (((category)::text = ANY ((ARRAY['╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕'::character varying, '╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗'::character varying])::text[])))
);


ALTER TABLE public.positions OWNER TO postgres;

--
-- Name: positions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.positions_id_seq OWNER TO postgres;

--
-- Name: positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.positions_id_seq OWNED BY public.positions.id;


--
-- Name: saved_queries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saved_queries (
    id integer NOT NULL,
    user_id integer NOT NULL,
    query_text text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    result_text text
);


ALTER TABLE public.saved_queries OWNER TO postgres;

--
-- Name: saved_queries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.saved_queries ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.saved_queries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: section_materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.section_materials (
    id integer NOT NULL,
    section_id integer NOT NULL,
    material_id integer NOT NULL,
    quantity numeric(10,2) NOT NULL,
    total_cost numeric(10,2)
);


ALTER TABLE public.section_materials OWNER TO postgres;

--
-- Name: section_materials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.section_materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.section_materials_id_seq OWNER TO postgres;

--
-- Name: section_materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.section_materials_id_seq OWNED BY public.section_materials.id;


--
-- Name: section_work_plan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.section_work_plan (
    id integer NOT NULL,
    section_id integer NOT NULL,
    work_type_id integer NOT NULL,
    planned_start date NOT NULL,
    planned_end date NOT NULL,
    planned_quantity numeric(12,2) NOT NULL,
    unit_id integer NOT NULL,
    order_index integer,
    notes text,
    CONSTRAINT section_work_plan_planned_quantity_check CHECK ((planned_quantity > (0)::numeric))
);


ALTER TABLE public.section_work_plan OWNER TO postgres;

--
-- Name: section_work_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.section_work_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.section_work_plan_id_seq OWNER TO postgres;

--
-- Name: section_work_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.section_work_plan_id_seq OWNED BY public.section_work_plan.id;


--
-- Name: section_works; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.section_works (
    id integer NOT NULL,
    section_id integer NOT NULL,
    work_type_id integer NOT NULL,
    volume numeric(10,2) NOT NULL,
    total_cost numeric(12,2),
    planned_start date,
    planned_end date,
    actual_start date,
    actual_end date
);


ALTER TABLE public.section_works OWNER TO postgres;

--
-- Name: section_works_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.section_works_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.section_works_id_seq OWNER TO postgres;

--
-- Name: section_works_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.section_works_id_seq OWNED BY public.section_works.id;


--
-- Name: sections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sections (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    site_id integer NOT NULL,
    chief_id integer,
    brigade_id integer,
    start_date date NOT NULL,
    end_date date,
    notes text
);


ALTER TABLE public.sections OWNER TO postgres;

--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sections_id_seq OWNER TO postgres;

--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sections_id_seq OWNED BY public.sections.id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suppliers (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    contact_name character varying(255),
    phone character varying(50),
    email character varying(100),
    address text
);


ALTER TABLE public.suppliers OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suppliers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suppliers_id_seq OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suppliers_id_seq OWNED BY public.suppliers.id;


--
-- Name: units; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.units (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    short_name character varying(10) NOT NULL
);


ALTER TABLE public.units OWNER TO postgres;

--
-- Name: units_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.units_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.units_id_seq OWNER TO postgres;

--
-- Name: units_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.units_id_seq OWNED BY public.units.id;


--
-- Name: work_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_logs (
    id integer NOT NULL,
    section_id integer NOT NULL,
    brigade_id integer,
    work_type_id integer NOT NULL,
    actual_date date DEFAULT CURRENT_DATE NOT NULL,
    quantity numeric(12,2) NOT NULL,
    unit_id integer NOT NULL,
    notes text,
    CONSTRAINT work_logs_quantity_check CHECK ((quantity >= (0)::numeric))
);


ALTER TABLE public.work_logs OWNER TO postgres;

--
-- Name: work_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_logs_id_seq OWNER TO postgres;

--
-- Name: work_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_logs_id_seq OWNED BY public.work_logs.id;


--
-- Name: work_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_plans (
    id integer NOT NULL,
    site_id integer,
    brigade_id integer,
    work_type_id integer,
    planned_start date,
    planned_end date,
    planned_quantity numeric(10,2),
    status character varying(30) DEFAULT '╨Ч╨░╨┐╨╗╨░╨╜╨╛╨▓╨░╨╜╨╛'::character varying,
    notes text,
    CONSTRAINT work_plans_status_check CHECK (((status)::text = ANY ((ARRAY['╨Ч╨░╨┐╨╗╨░╨╜╨╛╨▓╨░╨╜╨╛'::character varying, '╨Т╨╕╨║╨╛╨╜╤Г╤Ф╤В╤М╤Б╤П'::character varying, '╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛'::character varying])::text[])))
);


ALTER TABLE public.work_plans OWNER TO postgres;

--
-- Name: work_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_plans_id_seq OWNER TO postgres;

--
-- Name: work_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_plans_id_seq OWNED BY public.work_plans.id;


--
-- Name: work_report_materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_report_materials (
    id integer NOT NULL,
    report_id integer NOT NULL,
    material_id integer NOT NULL,
    quantity numeric(12,2) NOT NULL
);


ALTER TABLE public.work_report_materials OWNER TO postgres;

--
-- Name: work_report_materials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_report_materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_report_materials_id_seq OWNER TO postgres;

--
-- Name: work_report_materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_report_materials_id_seq OWNED BY public.work_report_materials.id;


--
-- Name: work_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_reports (
    id integer NOT NULL,
    work_plan_id integer,
    actual_start date,
    actual_end date,
    actual_quantity numeric(10,2),
    comment text
);


ALTER TABLE public.work_reports OWNER TO postgres;

--
-- Name: work_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_reports_id_seq OWNER TO postgres;

--
-- Name: work_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_reports_id_seq OWNED BY public.work_reports.id;


--
-- Name: work_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_types (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    cost_per_unit numeric(10,2),
    unit_id integer
);


ALTER TABLE public.work_types OWNER TO postgres;

--
-- Name: work_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_types_id_seq OWNER TO postgres;

--
-- Name: work_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_types_id_seq OWNED BY public.work_types.id;


--
-- Name: brigade_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_assignments ALTER COLUMN id SET DEFAULT nextval('public.brigade_assignments_id_seq'::regclass);


--
-- Name: brigade_status_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_status_history ALTER COLUMN id SET DEFAULT nextval('public.brigade_status_history_id_seq'::regclass);


--
-- Name: brigade_work_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_work_history ALTER COLUMN id SET DEFAULT nextval('public.brigade_work_history_id_seq'::regclass);


--
-- Name: brigades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigades ALTER COLUMN id SET DEFAULT nextval('public.brigades_id_seq'::regclass);


--
-- Name: construction_sites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.construction_sites ALTER COLUMN id SET DEFAULT nextval('public.construction_sites_id_seq'::regclass);


--
-- Name: deliveries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries ALTER COLUMN id SET DEFAULT nextval('public.deliveries_id_seq'::regclass);


--
-- Name: delivery_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_items ALTER COLUMN id SET DEFAULT nextval('public.delivery_items_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- Name: equipment_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_types ALTER COLUMN id SET DEFAULT nextval('public.equipment_types_id_seq'::regclass);


--
-- Name: equipment_work_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_work_history ALTER COLUMN id SET DEFAULT nextval('public.equipment_work_history_id_seq'::regclass);


--
-- Name: managements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.managements ALTER COLUMN id SET DEFAULT nextval('public.managements_id_seq'::regclass);


--
-- Name: material_plan id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_plan ALTER COLUMN id SET DEFAULT nextval('public.material_plan_id_seq'::regclass);


--
-- Name: material_usage id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage ALTER COLUMN id SET DEFAULT nextval('public.material_usage_id_seq'::regclass);


--
-- Name: material_usage_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage_items ALTER COLUMN id SET DEFAULT nextval('public.material_usage_items_id_seq'::regclass);


--
-- Name: material_usages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usages ALTER COLUMN id SET DEFAULT nextval('public.material_usages_id_seq'::regclass);


--
-- Name: materials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials ALTER COLUMN id SET DEFAULT nextval('public.materials_id_seq'::regclass);


--
-- Name: plan_materials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_materials ALTER COLUMN id SET DEFAULT nextval('public.plan_materials_id_seq'::regclass);


--
-- Name: positions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positions ALTER COLUMN id SET DEFAULT nextval('public.positions_id_seq'::regclass);


--
-- Name: section_materials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_materials ALTER COLUMN id SET DEFAULT nextval('public.section_materials_id_seq'::regclass);


--
-- Name: section_work_plan id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_work_plan ALTER COLUMN id SET DEFAULT nextval('public.section_work_plan_id_seq'::regclass);


--
-- Name: section_works id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_works ALTER COLUMN id SET DEFAULT nextval('public.section_works_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections ALTER COLUMN id SET DEFAULT nextval('public.sections_id_seq'::regclass);


--
-- Name: suppliers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN id SET DEFAULT nextval('public.suppliers_id_seq'::regclass);


--
-- Name: units id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units ALTER COLUMN id SET DEFAULT nextval('public.units_id_seq'::regclass);


--
-- Name: work_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs ALTER COLUMN id SET DEFAULT nextval('public.work_logs_id_seq'::regclass);


--
-- Name: work_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_plans ALTER COLUMN id SET DEFAULT nextval('public.work_plans_id_seq'::regclass);


--
-- Name: work_report_materials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_report_materials ALTER COLUMN id SET DEFAULT nextval('public.work_report_materials_id_seq'::regclass);


--
-- Name: work_reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_reports ALTER COLUMN id SET DEFAULT nextval('public.work_reports_id_seq'::regclass);


--
-- Name: work_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_types ALTER COLUMN id SET DEFAULT nextval('public.work_types_id_seq'::regclass);


--
-- Data for Name: accounts_guestrequest; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_guestrequest (id, message, status, created_at, user_id) FROM stdin;
2	╨е╨╛╤З╤Г, ╤Й╨╛╨▒ ╨▓╨╕ ╨╝╨╡╨╜╤Ц ╨╜╨░╨┤╨░╨╗╨╕ ╨┤╨╛╤Б╤В╤Г╨┐ ╤П╨║ ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╨╜╨╛╨╝╤Г ╨║╨╛╤А╨╕╤Б╤В╤Г╨▓╨░╤З╤Г	rejected	2025-11-15 15:08:39.388766+02	3
1	╨е╨╛╤З╤Г, ╤Й╨╛╨▒ ╨▓╨╕ ╨╝╨╡╨╜╤Ц ╨╜╨░╨┤╨░╨╗╨╕ ╨┤╨╛╤Б╤В╤Г╨┐ ╤П╨║ ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╨╜╨╛╨╝╤Г ╨║╨╛╤А╨╕╤Б╤В╤Г╨▓╨░╤З╤Г	approved	2025-11-15 15:07:39.322756+02	3
5	╨Я╤А╨╛╤И╤Г ╨▓╨░╤Б ╨╜╨░╨┤╨░╤В╨╕ ╨╝╨╡╨╜╤Ц ╨┤╨╛╤Б╤В╤Г╨┐ ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╨╜╨╛╨│╨╛ ╨║╨╛╤А╨╕╤Б╤В╤Г╨▓╨░╤З╨░	approved	2025-11-15 15:12:37.144481+02	3
6	╨Я╤А╨╛╤И╤Г ╨▓╨░╤Б ╨╜╨░╨┤╨░╤В╨╕ ╨╝╨╡╨╜╤Ц ╨┤╨╛╤Б╤В╤Г╨┐ ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╨╜╨╛╨│╨╛ ╨║╨╛╤А╨╕╤Б╤В╤Г╨▓╨░╤З╨░	rejected	2025-11-15 15:25:18.605842+02	3
7	╨Я╤А╨╛╤И╤Г, ╨╜╨░╨┤╨░╨╣╤В╨╡ ╨╝╨╡╨╜╤Ц ╤Б╤В╨░╤В╤Г╤Б ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╨╜╨╛╨│╨╛ ╨║╨╛╤А╨╕╤Б╤В╤Г╨▓╨░╤З╨░	approved	2025-11-15 22:31:30.264365+02	3
8	╨┐╤А╨╛╤И╤Г ╨▓╨░╤Б ╨╜╨░╨┤╨░╤В╨╕ ╨╝╨╡╨╜╤Ц ╨┤╨╛╤Б╤В╤Г╨┐ ╤П╨║ ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╨╜╨╛╨│╨╛ ╨║╨╛╤А╨╕╤Б╤В╤Г╨▓╨░╤З╨░	approved	2025-11-16 17:52:08.485846+02	3
\.


--
-- Data for Name: accounts_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_keys (id, username, password_hash, role, created_at, reset_code) FROM stdin;
1	admin	240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9	admin	2025-11-15 01:54:55.104582+02	\N
3	mark	36fdc53642d31d9b24cf3439ad9b3982893f2c0c5777f5f9a5d4ee58a5463ebf	operator	2025-11-15 14:56:12.047536+02	\N
2	kirill	9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0	authorized	2025-11-15 02:04:14.219257+02	\N
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add user	6	add_customuser
22	Can change user	6	change_customuser
23	Can delete user	6	delete_customuser
24	Can view user	6	view_customuser
25	Can add custom user	7	add_customuser
26	Can change custom user	7	change_customuser
27	Can delete custom user	7	delete_customuser
28	Can view custom user	7	view_customuser
29	Can add guest request	8	add_guestrequest
30	Can change guest request	8	change_guestrequest
31	Can delete guest request	8	delete_guestrequest
32	Can view guest request	8	view_guestrequest
33	Can add user	9	add_user
34	Can change user	9	change_user
35	Can delete user	9	delete_user
36	Can view user	9	view_user
\.


--
-- Data for Name: brigade_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brigade_assignments (id, brigade_id, section_id, assigned_at, unassigned_at, notes) FROM stdin;
\.


--
-- Data for Name: brigade_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brigade_members (brigade_id, employee_id, role, start_date, end_date) FROM stdin;
14	8	╨С╤А╨╕╨│╨░╨┤╨╕╤А	2025-11-10	\N
14	27	╨Х╨╗╨╡╨║╤В╤А╨╕╨║	2025-11-10	\N
15	41	╨С╤А╨╕╨│╨░╨┤╨╕╤А	2025-11-11	\N
15	40	╨Я╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╨╕╨║	2025-11-11	\N
15	39	╨Я╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╨╕╨║	2025-11-11	\N
18	1	╨С╤А╨╕╨│╨░╨┤╨╕╤А	2025-11-18	\N
18	26	╨С╨╡╤В╨╛╨╜╤П╤А	2025-11-18	\N
18	37	╨С╨╡╤В╨╛╨╜╤П╤А	2025-11-18	\N
18	35	╨в╤А╤Г╨▒╨╛╤З╨╕╤Б╤В	2025-11-18	\N
\.


--
-- Data for Name: brigade_status_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brigade_status_history (id, brigade_id, old_status, new_status, changed_at, changed_by) FROM stdin;
5	15	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-17 15:29:35.563219	\N
6	15	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-17 16:02:29.321851	\N
7	15	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-18 15:38:04.223646	\N
8	15	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-18 15:43:58.872738	\N
9	18	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-18 16:12:57.72219	\N
10	18	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-18 16:20:25.690606	\N
11	15	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-18 16:53:13.856559	\N
12	15	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-18 16:55:40.098702	\N
13	18	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-18 17:14:17.802789	\N
14	15	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-18 17:16:39.353401	\N
15	18	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-18 17:17:39.577886	\N
16	15	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-18 17:17:47.728018	\N
17	18	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-18 17:33:06.194809	\N
18	18	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-18 17:38:42.998176	\N
19	15	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	╨Р╨║╤В╨╕╨▓╨╜╨░	2025-11-20 11:43:09.901252	\N
20	15	╨Р╨║╤В╨╕╨▓╨╜╨░	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░	2025-11-20 11:45:41.747441	\N
\.


--
-- Data for Name: brigade_work_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brigade_work_history (id, brigade_id, section_work_id, start_date, end_date) FROM stdin;
1	18	18	2025-02-05	2025-05-05
2	15	19	2025-02-05	2025-04-05
\.


--
-- Data for Name: brigades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brigades (id, name, leader_id, notes, status) FROM stdin;
14	╨С╤А╨╕╨│╨░╨┤╨░ ╨╡╨╗╨╡╨║╤В╤А╨╕╨║╤Ц╨▓	8	╨Ч╨░╨╣╨╝╨░╤Ф╤В╤М╤Б╤П ╨╡╨╗╨╡╨║╤В╤А╨╕╨║╨╛╤О	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░
18	╨С╤А╨╕╨│╨░╨┤╨░ ╨║╨╛╨╝╤Г╨╜╨░╨╗╤М╨╜╨╕╨║╤Ц╨▓	1	╨Ч╨░╨╣╨╝╨░╤О╤В╤М╤Б╤П ╨┐╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П╨╝ ╨║╨╛╨╝╤Г╨╜╤Ц╨║╨░╤Ж╤Ц╨╣	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░
15	╨С╤А╨╕╨│╨░╨┤╨░ ╨┐╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╨╕╨║╤Ц╨▓	41	╨Ч╨░╨╣╨╝╨░╤Ф╤В╤М╤Б╤П ╨┐╨╛╨▓╨╜╨╕╨╝ ╨║╨╛╨╝╨┐╨╗╨╡╨║╤Б╨╛╨╝ ╨┐╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╨╕╤Е ╤А╨╛╨▒╤Ц╤В	╨Э╨╡╨░╨║╤В╨╕╨▓╨╜╨░
\.


--
-- Data for Name: construction_sites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.construction_sites (id, management_id, name, address, start_date, end_date, responsible_engineer_id, status, notes, deadline) FROM stdin;
16	2	╤В╨╡╤Б╤В ╨╛╨▒'╤Ф╨║╤В 9	╨░╨┤╤А╨╡╤Б╨░ ╤В╨╡╤Б╤В╨╛╨▓╨╛╨│╨╛ ╨╛╨▒'╤Ф╨║╤В╨░ 9	2025-02-05	2027-01-05	22	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛	╤В╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 9	2027-02-05
17	1	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 10	╨░╨┤╤А╨╡╤Б╨░ ╤В╨╡╤Б╤В╨╛╨▓╨╛╨│╨╛ ╨╛╨▒'╤Ф╨║╤В╨░ 10	2025-02-05	\N	2	╨Т ╨┐╤А╨╛╤Ж╨╡╤Б╤Ц	\N	2030-02-05
5	1	9-╤В╨╕ ╨┐╨╛╨▓╨╡╤А╤Е╤Ц╨▓╨║╨░	╨╝. ╨з╨╡╤А╨╜╤Ц╨▓╤Ж╤Ц, ╨▓╤Г╨╗ ╨а╤Ц╨▓╨╜╨╡╨╜╤Б╤М╨║╨░ 6╨░	2025-11-12	2025-12-12	2	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛		2026-11-12
8	2	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В	╨╝. ╨з╨╡╤А╨╜╤Ц╨▓╤Ж╤Ц, ╨▓╤Г╨╗. ╨а╤Г╤Б╤М╨║╨░ 241	2025-02-05	2026-02-05	2	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛	╨ж╨╡ ╤В╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В	2027-02-05
9	3	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 2	╨╝. ╨Ъ╤А╨╛╨┐╨╕╨▓╨╜╨╕╤Ж╤М╨║╨╕╨╣, ╨▓╤Г╨╗. ╨б╤В╨╛╤А╨╛╨╢╨╕╨╜╨╡╤Ж╤М╨║╨░, 65	2025-02-05	2029-02-05	2	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛ ╤Ц╨╖ ╨╖╨░╨┐╤Ц╨╖╨╜╨╡╨╜╨╜╤П╨╝	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 2	2028-02-05
11	1	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 4	╤В╨╡╤Б╤В╨╛╨▓╨░ ╨░╨┤╤А╨╡╤Б╨░ 43	2025-02-05	0007-02-04	2	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛	\N	2027-02-05
12	2	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 5	╨░╨┤╤А╨╡╤Б╨░ ╤В╨╡╤Б╤В╨╛╨▓╨╛╨│╨╛ ╨╛╨▒'╤Ф╨║╤В╨░	2025-02-05	2030-03-05	22	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛ ╤Ц╨╖ ╨╖╨░╨┐╤Ц╨╖╨╜╨╡╨╜╨╜╤П╨╝	╨Т╨╡╨╗╨╕╨║╨╕╨╣ ╤В╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В	2030-02-05
13	1	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 6	╨░╨┤╤А╨╡╤Б╨░ ╤В╨╡╤Б╤В╨╛╨▓╨╛╨│╨╛ ╨╛╨▒'╤Ф╨║╤В╨░ 6	2025-03-05	2027-03-05	2	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛	╤В╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В ╨┤╨╗╤П ╨╛╨▒'╤Ф╨║╤В╨░ 6	2027-03-05
14	3	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 7	╤В╨╡╤Б╤В╨╛╨▓╨░ ╨░╨┤╤А╨╡╤Б╨░ 7	2025-02-05	2030-02-06	20	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛ ╤Ц╨╖ ╨╖╨░╨┐╤Ц╨╖╨╜╨╡╨╜╨╜╤П╨╝	╤В╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 7\r\n	2030-02-05
15	1	╤В╨╡╤Б╤В ╨╛╨▒'╤Ф╨║╤В 8	╨░╨┤╤А╨╡╤Б╨░ ╤В╨╡╤Б╤В╨╛╨▓╨╛╨│╨╛ ╨╛╨▒'╤Ф╨║╤В╨░ 8	2025-02-05	2027-02-05	38	╨Ч╨░╨▓╨╡╤А╤И╨╡╨╜╨╛	╨в╨╡╤Б╤В╨╛╨▓╨╕╨╣ ╨╛╨▒'╤Ф╨║╤В 8	2027-02-05
\.


--
-- Data for Name: deliveries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deliveries (id, supplier_id, delivery_date, total_amount, notes, section_id) FROM stdin;
13	1	2025-05-06	15600.00		\N
14	1	2025-05-06	1560.00		\N
5	2	2025-06-05	21000.00		\N
6	2	2025-06-05	21000.00		\N
12	1	2025-11-11	126000.00		\N
16	1	2025-06-05	504.00		\N
15	1	2025-02-05	70000.00		\N
17	1	2025-02-05	5166.00		5
18	1	2025-02-05	0.00		7
19	1	2025-11-15	0.00		7
20	1	2025-11-15	0.00		7
21	1	2025-11-15	0.00		7
22	1	2025-11-15	0.00		7
23	1	2025-11-15	0.00		7
24	1	2025-11-15	0.00		7
25	1	2025-02-05	140000.00		9
\.


--
-- Data for Name: delivery_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.delivery_items (id, delivery_id, material_id, quantity, price_per_unit) FROM stdin;
5	5	3	500.00	42.00
6	6	3	500.00	42.00
7	12	4	60.00	2100.00
8	13	7	1300.00	12.00
9	14	7	130.00	12.00
10	15	8	150.00	200.00
11	15	6	200.00	200.00
12	16	3	12.00	42.00
13	17	3	123.00	42.00
14	25	9	200.00	250.00
15	25	8	250.00	200.00
16	25	6	200.00	200.00
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-11-20 23:39:13.18049+02
2	auth	0001_initial	2025-11-20 23:39:21.282803+02
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
0ph1ennhriidkq2n3rdp2wjosjigsqgy	eyJ1c2VyX2lkIjoxLCJyb2xlIjoiYWRtaW4ifQ:1vMCZb:oJHbyRgOWSGmtocNPrHDLp3pw67hsn7RnEMqwCeW4cs	2025-12-04 23:52:15.230314+02
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, first_name, last_name, father_name, birthday, start_date, end_date, salary, position_id, category) FROM stdin;
2	╨б╨▓╤Ц╤В╨╗╨░╨╜╨░	╨Ж╨▓╨░╨╜╨╡╨╜╨║╨╛	╨Ь╨╕╤Е╨░╨╣╨╗╤Ц╨▓╨╜╨░	1990-02-20	2018-06-10	\N	22000.00	6	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
3	╨Р╨╜╨┤╤А╤Ц╨╣	╨Ъ╨╛╨▓╨░╨╗╤М	╨Ю╨╗╨╡╨║╤Б╨░╨╜╨┤╤А╨╛╨▓╨╕╤З	1995-09-15	2019-05-01	\N	18000.00	1	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
4	╨б╨╡╤А╨│╤Ц╨╣	╨С╨╛╨╜╨┤╨░╤А	╨Ж╨▓╨░╨╜╨╛╨▓╨╕╤З	1992-07-08	2017-04-15	\N	19000.00	2	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
6	╨Ж╤А╨╕╨╜╨░	╨в╨╕╨╝╨╛╤И╨╡╨╜╨║╨╛	╨о╤А╤Ц╤Ч╨▓╨╜╨░	1993-11-03	2021-03-01	\N	21000.00	5	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
8	╨Ь╨░╤А╤Ц╤П	╨б╨╛╨║╨╛╨╗╨╛╨▓╨░	╨Т╤Ц╤В╨░╨╗╤Ц╤Ч╨▓╨╜╨░	1991-01-25	2019-09-01	\N	18500.00	7	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
40	╨Р╨╜╨┤╤А╤Ц╨╣	╨Ч╤Г╨▒╨╡╨╜╨║╨╛	╨Ь╨╕╨║╨╛╨╗╨░╨╣╨╛╨▓╨╕╤З	2000-07-20	2025-11-11	\N	18000.00	1	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
1	╨Ю╨╗╨╡╨│	╨Я╨╡╤В╤А╨╡╨╜╨║╨╛	╨Т╤Ц╨║╤В╨╛╤А╨╛╨▓╨╕╤З	1987-05-12	2015-03-01	\N	25000.00	4	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
20	╨Ж╨▓╨░╨╜	╨Ж╨▓╨░╨╜╨╛╨▓	╨Ж╨▓╨░╨╜╨╛╨▓╨╕╤З	2000-03-20	2025-11-01	\N	798465.00	14	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
42	╨а╨╛╤Б╤В╨╕╤Б╨╗╨░╨▓	╨Ь╨╕╤А╤И╤З╨╡╨╜╨║╨╛	╨С╨╛╨│╨┤╨░╨╜╨╛╨▓╨╕╤З	2000-05-02	2025-11-12	\N	16000.00	3	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
26	╨Т╨░╤Б╨╕╨╗╤М	╨Ж╨▓╨░╨╜╨╛╨▓	╨Ю╨╗╨╡╨║╤Б╨░╨╜╨┤╤А╨╛╨▓╨╕╤З	2025-11-07	2025-11-07	\N	15000.00	3	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
27	╨Т╨░╤Б╨╕╨╗╤М	╨Я╨╡╤В╤А╨╡╨╜╨║╨╛	╨С╨░╤В╤М╨║╨╛╨▓╨╕╤З	1999-11-05	2025-11-07	\N	30000.00	7	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
5	╨Я╨░╨▓╨╗╨╛	╨Ф╨╡╨╝╤З╨╡╨╜╨║╨╛	╨Р╨╜╨┤╤А╤Ц╨╣╨╛╨▓╨╕╤З	1988-12-01	2020-02-01	2025-05-02	20000.00	3	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
41	╨в╨░╤А╨░╤Б	╨Р╨╜╨┤╤А╤Г╤Й╨╡╨╜╨║╨╛	╨Ю╨╗╨╡╨│╨╛╨▓╨╕╤З	1999-12-02	2025-11-11	2025-05-02	20000.00	3	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
22	╨Ъ╨╕╤А╨╕╨╗╨╛	╨С╨╡╤А╨╡╨│╨╛╨▓╨╕╨╣ 	╨Ю╨╗╨╡╨║╤Б╨░╨╜╨┤╤А╨╛╨▓╨╕╤З	2005-07-20	2025-11-05	2026-02-05	17500.00	6	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
38	╨Ю╨╗╨╡╨║╤Б╨░╨╜╨┤╤А	╨Т╨░╨╗╤М	╨Ф╨░╨╜╨╕╨╗╨╛╨▓╨╕╤З	1965-08-09	2025-11-11	\N	60000.00	5	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
35	╨Р╨╜╨┤╤А╤Ц╨╣	╨Ь╤Г╤А╨░╨╜╤З╨╡╨╜╨║╨╛	╨Ь╨╕╨║╨╛╨╗╨░╨╣╨╛╨▓╨╕╤З	1975-12-09	2025-11-10	\N	25000.00	3	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
36	╨Ю╨╗╨╡╨╜╨░	╨Ь╨╡╨╗╤М╨╜╨╕╨║	╨б╨╡╤А╨│╤Ц╤Ч╨▓╨╜╨░	1987-10-09	2015-04-13	\N	34500.00	1	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
37	╨Ф╨╝╨╕╤В╤А╨╛	╨и╨╡╨▓╤З╨╡╨╜╨║╨╛	╨Ю╨╗╨╡╨║╤Б╨░╨╜╨┤╤А╨╛╨▓╨╕╤З	1995-01-22	2020-09-01	\N	29800.00	3	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
39	╨Ь╨╕╤Е╨░╨╣╨╗╨╛	╨Ъ╤А╨╕╨▓╨╛╨╜╨╛╨╢╨║╨╛	╨Ж╨▓╨░╨╜╨╛╨▓╨╕╤З	1987-04-19	2025-11-11	\N	15000.00	1	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
\.


--
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (id, name, status, notes, assigned_site_id, type_id) FROM stdin;
6	╨У╤А╤Г╨╖╨╛╨▓╨╕╨║ ╨▒╤Ц╨╗╨╕╨╣	╨Т╤Ц╨╗╤М╨╜╨░	╨Ф╤Г╨╢╨╡ ╨▓╨╡╨╗╨╕╨║╨╕╨╣ ╨│╤А╤Г╨╖╨╛╨▓╨╕╨║	\N	3
7	╨С╤Г╨╗╤М╨┤╨╛╨╖╨╡╤А ╤Б╨╕╨╜╤Ц╨╣	╨Т╤Ц╨╗╤М╨╜╨░	╨Т╨╡╨╗╨╕╨║╨╕╨╣ ╤Б╨╕╨╜╤Ц╨╣ ╨▒╤Г╨╗╤М╨┤╨╛╨╖╨╡╤А	\N	2
8	╨Х╨║╤Б╨║╨░╨▓╨░╤В╨╛╤А ╨╢╨╛╨▓╤В╨╕╨╣	╨Т╤Ц╨╗╤М╨╜╨░	╨Ц╨╛╨▓╤В╨╕╨╣ ╨╡╨║╤Б╨║╨░╨▓╨░╤В╨╛╤А\r\n	\N	4
\.


--
-- Data for Name: equipment_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_types (id, title) FROM stdin;
1	╨Ъ╤А╨░╨╜
2	╨С╤Г╨╗╤М╨┤╨╛╨╖╨╡╤А
3	╨У╤А╤Г╨╖╨╛╨▓╨╕╨║
4	╨Х╨║╤Б╨║╨░╨▓╨░╤В╨╛╤А
\.


--
-- Data for Name: equipment_work_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_work_history (id, equipment_id, site_id, start_date, end_date, notes) FROM stdin;
1	6	14	2025-11-18	\N	╨Ф╤Г╨╢╨╡ ╨▓╨╡╨╗╨╕╨║╨╕╨╣ ╨│╤А╤Г╨╖╨╛╨▓╨╕╨║
2	7	14	2025-11-18	\N	╨Т╨╡╨╗╨╕╨║╨╕╨╣ ╤Б╨╕╨╜╤Ц╨╣ ╨▒╤Г╨╗╤М╨┤╨╛╨╖╨╡╤А
3	6	15	2025-11-18	\N	╨Ф╤Г╨╢╨╡ ╨▓╨╡╨╗╨╕╨║╨╕╨╣ ╨│╤А╤Г╨╖╨╛╨▓╨╕╨║
4	7	15	2025-11-18	\N	╨Т╨╡╨╗╨╕╨║╨╕╨╣ ╤Б╨╕╨╜╤Ц╨╣ ╨▒╤Г╨╗╤М╨┤╨╛╨╖╨╡╤А
5	8	15	2025-11-18	\N	╨Ц╨╛╨▓╤В╨╕╨╣ ╨╡╨║╤Б╨║╨░╨▓╨░╤В╨╛╤А\r\n
6	6	16	2025-11-18	\N	╨Ф╤Г╨╢╨╡ ╨▓╨╡╨╗╨╕╨║╨╕╨╣ ╨│╤А╤Г╨╖╨╛╨▓╨╕╨║
7	7	16	2025-11-18	\N	╨Т╨╡╨╗╨╕╨║╨╕╨╣ ╤Б╨╕╨╜╤Ц╨╣ ╨▒╤Г╨╗╤М╨┤╨╛╨╖╨╡╤А
8	8	16	2025-11-18	\N	╨Ц╨╛╨▓╤В╨╕╨╣ ╨╡╨║╤Б╨║╨░╨▓╨░╤В╨╛╤А\r\n
\.


--
-- Data for Name: managements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.managements (id, name, head_employee_id, notes) FROM stdin;
1	╨С╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╡ ╤Г╨┐╤А╨░╨▓╨╗╤Ц╨╜╨╜╤П тДЦ1	1	╨Т╤Ц╨┤╨┐╨╛╨▓╤Ц╨┤╨░╤Ф ╨╖╨░ ╨┐╤Ц╨▓╨╜╤Ц╤З╨╜╨╕╨╣ ╤А╨╡╨│╤Ц╨╛╨╜
2	╨С╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╡ ╤Г╨┐╤А╨░╨▓╨╗╤Ц╨╜╨╜╤П тДЦ2	2	╨Т╤Ц╨┤╨┐╨╛╨▓╤Ц╨┤╨░╤Ф ╨╖╨░ ╤Ж╨╡╨╜╤В╤А╨░╨╗╤М╨╜╨╕╨╣ ╤А╨╡╨│╤Ц╨╛╨╜
3	╨С╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╡ ╤Г╨┐╤А╨░╨▓╨╗╤Ц╨╜╨╜╤П тДЦ3	22	╨Т╤Ц╨┤╨┐╨╛╨▓╤Ц╨┤╨░╤Ф ╨╖╨░ ╨┐╤Ц╨▓╨┤╨╡╨╜╨╜╨╕╨╣ ╤А╨╡╨│╤Ц╨╛╨╜
\.


--
-- Data for Name: material_plan; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.material_plan (id, section_id, material_id, planned_qty) FROM stdin;
141	5	3	1.00
142	5	4	1.00
143	5	9	1.00
144	5	8	1.00
145	5	6	1.00
146	5	7	1.00
147	5	5	1.00
148	5	2	1.00
149	5	1	1.00
150	14	3	1.00
151	14	4	1.00
152	14	9	1.00
153	14	8	1.00
154	14	6	1.00
155	14	7	1.00
156	14	5	1.00
157	14	2	1.00
158	14	1	1.00
\.


--
-- Data for Name: material_usage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.material_usage (id, section_id, material_id, used_qty) FROM stdin;
2	5	3	123.00
3	9	9	200.00
4	9	8	250.00
5	9	6	200.00
\.


--
-- Data for Name: material_usage_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.material_usage_items (id, usage_id, material_id, quantity, total_price) FROM stdin;
\.


--
-- Data for Name: material_usages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.material_usages (id, usage_date, section_id, responsible_employee_id, notes) FROM stdin;
\.


--
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.materials (id, name, description, supplier_id, price, count, unit_id) FROM stdin;
5	╨д╨░╤А╨▒╨░ ╤Д╨░╤Б╨░╨┤╨╜╨░	╨С╤Ц╨╗╨░ ╨░╨║╤А╨╕╨╗╨╛╨▓╨░ ╤Д╨░╤А╨▒╨░	1	800.00	100.00	5
2	╨ж╨╡╨│╨╗╨░ ╨║╨╡╤А╨░╨╝╤Ц╤З╨╜╨░	╨Я╨╛╨▓╨╜╨╛╤В╤Ц╨╗╨░, ╤Б╤В╨░╨╜╨┤╨░╤А╤В╨╜╨░	1	12.50	9500.00	3
1	╨ж╨╡╨╝╨╡╨╜╤В ╨Ь50	╨Ф╨╗╤П ╨▒╨╡╤В╨╛╨╜╨╜╨╕╤Е ╤А╨╛╨▒╤Ц╤В	1	150.00	1400.00	4
7	╨Я╤А╨╛╨▓╨╛╨┤╨░ ╨┤╨╗╤П ╨┐╤А╨╛╨▓╨╛╨┤╨║╨╕	╨Ф╨╗╤П ╨┐╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П ╨╡╨╗╨╡╨║╤В╤А╨╕╨║╨╕	4	12.00	13000.00	7
4	╨С╨╡╤В╨╛╨╜ ╨Т25	╨У╨╛╤В╨╛╨▓╨░ ╨▒╨╡╤В╨╛╨╜╨╜╨░ ╤Б╤Г╨╝╤Ц╤И	2	21.00	60.00	2
3	╨Р╤А╨╝╨░╤В╤Г╤А╨░ ├Ш12	╨б╤В╨░╨╗╨╡╨▓╨╕╨╣ ╨┐╤А╤Г╤В ╨┤╨╗╤П ╨║╨░╤А╨║╨░╤Б╤Ц╨▓	2	42.00	550.00	1
9	╨С╤Ц╤В╤Г╨╝╨╜╨░ ╨║╤А╨╕╤И╨░	╨а╨╡╨╖╨╕╨╜╨╛╨▓╨╡ ╨┐╨╛╨║╤А╨╕╤В╤В╤П	5	250.00	1300.00	1
8	╨Ь╨╡╤В╨░╨╗╨╛╤З╨╡╤А╨╡╨┐╨╕╤Ж╤П ╤З╨╡╤А╨▓╨╛╨╜╨░	╨Ь╨╡╤В╨░╨╗╨╛╤З╨╡╤А╨╡╨┐╨╕╤Ж╤П ╨╖ ╨╛╤Б╨╛╨▒╨╗╨╕╨▓╨╕╨╝ ╨┐╨╛╨║╤А╨╕╤В╤В╤П╨╝	5	200.00	2300.00	1
6	╨Ь╤Г╤А╨╗╨░╤В╨╕	╨Ф╨╗╤П ╨┐╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╨╕╤Е ╤А╨╛╨▒╤Ц╤В	3	200.00	250.00	1
\.


--
-- Data for Name: plan_materials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_materials (id, plan_id, material_id, required_qty) FROM stdin;
\.


--
-- Data for Name: positions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.positions (id, title, description, category) FROM stdin;
2	╨Ь╤Г╤А╨░╨▓╨╜╨╕╨║	╨Ч╨┤╤Ц╨╣╤Б╨╜╤О╤Ф ╨║╨╗╨░╨┤╨║╤Г ╤Ж╨╡╨│╨╗╨╕ ╤В╨░ ╨▒╨╗╨╛╨║╤Ц╨▓	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
4	╨Ж╨╜╨╢╨╡╨╜╨╡╤А	╨Ъ╨╡╤А╤Г╤Ф ╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╝╨╕ ╨┐╤А╨╛╤Ж╨╡╤Б╨░╨╝╨╕ ╨╜╨░ ╨╛╨▒тАЩ╤Ф╨║╤В╤Ц	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
7	╨Х╨╗╨╡╨║╤В╤А╨╕╨║	╨Т╤Б╤В╨░╨╜╨╛╨▓╨╗╤О╤Ф ╨╡╨╗╨╡╨║╤В╤А╨╕╤З╨╜╤Ц ╤Б╨╕╤Б╤В╨╡╨╝╨╕	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
13	╨Я╤А╨╛╤А╨░╨▒	╨Ъ╨╛╨╜╤В╤А╨╛╨╗╤О╤Ф ╤Е╤Ц╨┤ ╨▒╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╕╤Е ╤А╨╛╨▒╤Ц╤В, ╨║╨╛╨╛╤А╨┤╨╕╨╜╤Г╤Ф ╨▒╤А╨╕╨│╨░╨┤╨╕	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
14	╨Ж╨╜╨╢╨╡╨╜╨╡╤А ╨╖ ╨╛╤Е╨╛╤А╨╛╨╜╨╕ ╨┐╤А╨░╤Ж╤Ц	╨Ъ╨╛╨╜╤В╤А╨╛╨╗╤О╤Ф ╨┤╨╛╤В╤А╨╕╨╝╨░╨╜╨╜╤П ╤В╨╡╤Е╨╜╤Ц╨║╨╕ ╨▒╨╡╨╖╨┐╨╡╨║╨╕ ╨╜╨░ ╨╛╨▒тАЩ╤Ф╨║╤В╨░╤Е	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
15	╨Ж╨╜╨╢╨╡╨╜╨╡╤А-╨║╨╛╤И╤В╨╛╤А╨╕╤Б╨╜╨╕╨║	╨У╨╛╤В╤Г╤Ф ╤В╨░ ╨░╨╜╨░╨╗╤Ц╨╖╤Г╤Ф ╨║╨╛╤И╤В╨╛╤А╨╕╤Б╨╜╤Г ╨┤╨╛╨║╤Г╨╝╨╡╨╜╤В╨░╤Ж╤Ц╤О	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
16	╨Ж╨╜╨╢╨╡╨╜╨╡╤А-╨▒╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╕╨║	╨Я╤А╨╛╨╡╨║╤В╤Г╤Ф ╤Ц ╨┐╨╗╨░╨╜╤Г╤Ф ╨║╨╛╨╜╤Б╤В╤А╤Г╨║╤В╨╕╨▓╨╜╤Ц ╨╡╨╗╨╡╨╝╨╡╨╜╤В╨╕ ╨▒╤Г╨┤╤Ц╨▓╨╡╨╗╤М	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
17	╨Ь╨░╨╣╤Б╤В╨╡╤А ╨▓╨╕╤А╨╛╨▒╨╜╨╕╤З╨╛╤Ч ╨┤╤Ц╨╗╤М╨╜╨╕╤Ж╤Ц	╨С╨╡╨╖╨┐╨╛╤Б╨╡╤А╨╡╨┤╨╜╤М╨╛ ╨║╨╡╤А╤Г╤Ф ╨▒╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╕╨╝╨╕ ╤А╨╛╨▒╨╛╤В╨░╨╝╨╕ ╨╜╨░ ╨╝╤Ц╤Б╤Ж╤Ц	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
1	╨С╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╕╨║	╨Т╨╕╨║╨╛╨╜╤Г╤Ф ╨╖╨░╨│╨░╨╗╤М╨╜╨╛╨▒╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╤Ц ╤А╨╛╨▒╨╛╤В╨╕	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
3	╨С╨╡╤В╨╛╨╜╤П╤А	╨У╨╛╤В╤Г╤Ф ╤В╨░ ╨╖╨░╨╗╨╕╨▓╨░╤Ф ╨▒╨╡╤В╨╛╨╜	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
8	╨Ь╨░╨╗╤П╤А	╨Т╨╕╨║╨╛╨╜╤Г╤Ф ╨╛╨╖╨┤╨╛╨▒╨╗╤О╨▓╨░╨╗╤М╨╜╤Ц ╤А╨╛╨▒╨╛╤В╨╕	╨а╨╛╨▒╤Ц╤В╨╜╨╕╨║╨╕
5	╨Э╨░╤З╨░╨╗╤М╨╜╨╕╨║ ╨┤╤Ц╨╗╤М╨╜╨╕╤Ж╤Ц	╨Ю╤А╨│╨░╨╜╤Ц╨╖╨╛╨▓╤Г╤Ф ╤А╨╛╨▒╨╛╤В╤Г ╨▒╤А╨╕╨│╨░╨┤ ╨╜╨░ ╨┤╤Ц╨╗╤П╨╜╤Ж╤Ц	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
6	╨У╨╛╨╗╨╛╨▓╨╜╨╕╨╣ ╤Ц╨╜╨╢╨╡╨╜╨╡╤А	╨Ъ╨╛╨╜╤В╤А╨╛╨╗╤О╤Ф ╨▓╨╕╨║╨╛╨╜╨░╨╜╨╜╤П ╨▒╤Г╨┤╤Ц╨▓╨╡╨╗╤М╨╜╨╕╤Е ╨┐╤А╨╛╤Ж╨╡╤Б╤Ц╨▓	╨Ж╨╜╨╢╨╡╨╜╨╡╤А╨╜╨╛-╤В╨╡╤Е╨╜╤Ц╤З╨╜╨╕╨╣ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗
\.


--
-- Data for Name: saved_queries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saved_queries (id, user_id, query_text, created_at, result_text) FROM stdin;
\.


--
-- Data for Name: section_materials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.section_materials (id, section_id, material_id, quantity, total_cost) FROM stdin;
\.


--
-- Data for Name: section_work_plan; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.section_work_plan (id, section_id, work_type_id, planned_start, planned_end, planned_quantity, unit_id, order_index, notes) FROM stdin;
\.


--
-- Data for Name: section_works; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.section_works (id, section_id, work_type_id, volume, total_cost, planned_start, planned_end, actual_start, actual_end) FROM stdin;
8	5	5	135.00	27000.00	2025-03-20	2025-04-20	2025-03-20	2026-04-22
9	9	5	200.00	40000.00	2025-02-05	2025-04-05	2025-02-05	2025-04-06
10	9	2	200.00	50000.00	2025-04-05	2025-06-05	2025-04-05	2025-07-05
11	9	4	200.00	30000.00	2025-07-05	2025-09-05	2025-07-05	2025-09-05
12	10	6	200.00	20000.00	2025-11-05	2026-02-05	2025-11-05	2026-02-09
13	10	1	200.00	30000.00	2026-02-09	2026-04-09	2026-02-09	2026-04-11
14	11	2	250.00	62500.00	2025-02-05	2025-03-05	2025-02-05	2025-03-06
15	11	5	250.00	50000.00	2025-03-07	2025-05-07	2025-03-07	2025-05-07
16	12	6	150.00	15000.00	2025-03-07	2025-05-07	2025-03-07	2025-05-08
17	13	5	150.00	30000.00	2025-09-05	2025-10-05	2025-09-05	2025-10-06
18	14	6	150.00	15000.00	2025-02-05	2025-05-05	2025-02-05	2025-05-05
19	15	5	200.00	40000.00	2025-02-05	2025-04-05	2025-02-05	2025-04-05
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sections (id, name, site_id, chief_id, brigade_id, start_date, end_date, notes) FROM stdin;
7	╨Я╨╛╨║╤А╤Ц╨▓╨╗╤П	5	6	\N	2025-02-05	\N	\N
5	╨С╤Г╨┤╤Ц╨▓╨╜╨╕╤Ж╤В╨▓╨╛	5	6	\N	2025-02-05	\N	None
9	╨Я╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╤Ц ╤А╨╛╨▒╨╛╤В╨╕	11	38	\N	2025-02-05	2025-09-05	╨Ч╨░╨╣╨╝╨░╤О╤В╤М╤Б╤П ╨┐╨╛╨▓╨╜╨╛╤О ╨┐╨╛╨▒╤Г╨┤╨╛╨▓╨╛╤О ╨║╤А╨╕╤И╤Ц
10	╨Я╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П ╤В╤А╤Г╨▒	11	38	\N	2025-11-05	2026-04-11	╨а╨╛╨▒╨╛╤В╨╕ ╨╖ ╨┐╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П╨╝ ╨║╨╛╨╝╤Г╨╜╤Ц╨║╨░╤Ж╤Ц╨╣ ╨┤╨╛ ╨╛╨▒'╤Ф╨║╤В╤Г
11	╨а╨╛╨▒╨╛╤В╨░ ╨╖ ╨║╤А╨╕╤И╨╛╤О	12	38	\N	2025-02-05	\N	╨а╨╛╨▒╨╛╤В╨╕ ╨╖ ╨┐╨╛╨║╤А╤Ц╨▓╨╗╨╡╤О
12	╨Я╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П ╤В╤А╤Г╨▒	13	6	\N	2025-03-07	2025-06-07	\N
13	╨Я╨╛╨║╤А╤Ц╨▓╨╡╨╗╤М╨╜╤Ц ╤А╨╛╨▒╨╛╤В╨╕ 1	13	38	\N	2025-09-05	2025-11-05	\N
14	╨в╤А╤Г╨▒╨╕	14	38	\N	2025-02-05	2025-07-05	\N
15	╨Я╨╛╨║╤А╤Ц╨▓╨╗╤П 10	17	6	15	2025-02-05	2025-04-05	\N
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suppliers (id, name, contact_name, phone, email, address) FROM stdin;
1	╨в╨Ю╨Т "╨С╤Г╨┤╨Ь╨░╤А╨║╨╡╤В"	╨Ж╨▓╨░╨╜ ╨У╨╜╨░╤В╤О╨║	+380931234567	info@budmarket.ua	╨╝. ╨Ъ╨╕╤Ч╨▓, ╨▓╤Г╨╗. ╨Я╤А╨╛╨╝╨╕╤Б╨╗╨╛╨▓╨░, 12
2	╨в╨Ю╨Т "╨б╤В╨░╨╗╤М╨Я╤А╨╛╨╝"	╨Ю╨╗╨╡╨╜╨░ ╨а╨╛╨╝╨░╨╜╤О╨║	+380671112233	sales@stalprom.ua	╨╝. ╨Ф╨╜╤Ц╨┐╤А╨╛, ╨▓╤Г╨╗. ╨б╤Ц╤З╨╛╨▓╨╕╤Е ╨б╤В╤А╤Ц╨╗╤М╤Ж╤Ц╨▓, 24
3	╨в╨Ю╨Т "╨Ы╤Ц╤Б╨С╤Г╨┤1"	╨Я╨╡╤В╤А╨╡╨╜╨║╨╛ ╨Ж╨▓╨░╨╜	+380992645789	forestbuild@gmail.com	╨╝. ╨з╨╡╤А╨╜╤Ц╨▓╤Ж╤Ц, ╨▓╤Г╨╗. ╨и╨╡╨▓╤З╨╡╨╜╨║╨░, 53
4	╨в╨Ю╨Т "╨з╨╡╤А╨╜╤Ц╨▓╤Ж╤Ц╨Ь╤Ц╨┤╤М"	╨б╨╗╤О╤Б╨░╤А ╨Ь╨╕╨║╨╛╨╗╨░	+380963051456	example@gmailcom	╨╝. ╨з╨╡╤А╨╜╤Ц╨▓╤Ж╤Ц, ╨▓╤Г╨╗. ╨а╤Г╤Б╤М╨║╨░ 105
5	╨в╨Ю╨Т "╨Я╨╛╨║╤А╤Ц╨▓╨╗╤П"	╨Ж╨▓╨░╨╜╨╛╨▓ ╨Ь╨╕╤Е╨░╨╣╨╗╨╛	+3801234567	example@gmail.com	╨╝. ╨з╨╡╤А╨╜╤Ц╨▓╤Ж╤Ц, ╨▓╤Г╨╗. ╨а╤Г╤Б╤М╨║╨░ 241
\.


--
-- Data for Name: units; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.units (id, name, short_name) FROM stdin;
1	╨╝╨╡╤В╤А ╨║╨▓╨░╨┤╤А╨░╤В╨╜╨╕╨╣	╨╝┬▓
2	╨╝╨╡╤В╤А ╨║╤Г╨▒╤Ц╤З╨╜╨╕╨╣	╨╝┬│
3	╤И╤В╤Г╨║╨░	╤И╤В
4	╨║╤Ц╨╗╨╛╨│╤А╨░╨╝	╨║╨│
5	╨╗╤Ц╤В╤А	╨╗
7	╨╝╨╡╤В╤А	╨╝
\.


--
-- Data for Name: work_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_logs (id, section_id, brigade_id, work_type_id, actual_date, quantity, unit_id, notes) FROM stdin;
\.


--
-- Data for Name: work_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_plans (id, site_id, brigade_id, work_type_id, planned_start, planned_end, planned_quantity, status, notes) FROM stdin;
\.


--
-- Data for Name: work_report_materials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_report_materials (id, report_id, material_id, quantity) FROM stdin;
\.


--
-- Data for Name: work_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_reports (id, work_plan_id, actual_start, actual_end, actual_quantity, comment) FROM stdin;
\.


--
-- Data for Name: work_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_types (id, name, cost_per_unit, unit_id) FROM stdin;
2	╨Ю╨▒╤А╨╕╤И╨╛╤В╨║╨░ ╨┤╨╗╤П ╨║╤А╨╕╤И╤Ц	250.00	1
1	╨Ч╨░╨╗╨╕╨▓╨║╨░ ╤Д╤Г╨╜╨┤╨░╨╝╨╡╨╜╤В╤Г	150.00	1
4	╨Я╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П ╨┐╤А╨╛╨▓╨╛╨┤╨║╨╕	150.00	1
5	╨Я╨╛╨║╤А╨╕╤В╤В╤П ╨┐╨╛╨║╤А╤Ц╨▓╨╗╤Ц	200.00	1
6	╨Я╤А╨╛╨▓╨╡╨┤╨╡╨╜╨╜╤П ╤В╤А╤Г╨▒	100.00	1
\.


--
-- Name: accounts_customuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_customuser_id_seq', 3, true);


--
-- Name: accounts_guestrequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_guestrequest_id_seq', 8, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 36, true);


--
-- Name: brigade_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brigade_assignments_id_seq', 1, false);


--
-- Name: brigade_status_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brigade_status_history_id_seq', 20, true);


--
-- Name: brigade_work_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brigade_work_history_id_seq', 2, true);


--
-- Name: brigades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brigades_id_seq', 18, true);


--
-- Name: construction_sites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.construction_sites_id_seq', 17, true);


--
-- Name: deliveries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deliveries_id_seq', 25, true);


--
-- Name: delivery_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.delivery_items_id_seq', 16, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 1, false);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 2, true);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 42, true);


--
-- Name: equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_id_seq', 8, true);


--
-- Name: equipment_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_types_id_seq', 4, true);


--
-- Name: equipment_work_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_work_history_id_seq', 8, true);


--
-- Name: managements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.managements_id_seq', 3, true);


--
-- Name: material_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_plan_id_seq', 158, true);


--
-- Name: material_usage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_usage_id_seq', 5, true);


--
-- Name: material_usage_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_usage_items_id_seq', 4, true);


--
-- Name: material_usages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_usages_id_seq', 2, true);


--
-- Name: materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.materials_id_seq', 10, true);


--
-- Name: plan_materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.plan_materials_id_seq', 1, false);


--
-- Name: positions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.positions_id_seq', 17, true);


--
-- Name: saved_queries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.saved_queries_id_seq', 1, false);


--
-- Name: section_materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.section_materials_id_seq', 1, false);


--
-- Name: section_work_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.section_work_plan_id_seq', 1, false);


--
-- Name: section_works_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.section_works_id_seq', 19, true);


--
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sections_id_seq', 15, true);


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suppliers_id_seq', 5, true);


--
-- Name: units_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.units_id_seq', 7, true);


--
-- Name: work_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_logs_id_seq', 1, false);


--
-- Name: work_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_plans_id_seq', 1, false);


--
-- Name: work_report_materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_report_materials_id_seq', 1, false);


--
-- Name: work_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_reports_id_seq', 1, false);


--
-- Name: work_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_types_id_seq', 6, true);


--
-- Name: accounts_keys accounts_customuser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts_keys
    ADD CONSTRAINT accounts_customuser_pkey PRIMARY KEY (id);


--
-- Name: accounts_keys accounts_customuser_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts_keys
    ADD CONSTRAINT accounts_customuser_username_key UNIQUE (username);


--
-- Name: accounts_guestrequest accounts_guestrequest_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts_guestrequest
    ADD CONSTRAINT accounts_guestrequest_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: brigade_assignments brigade_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_assignments
    ADD CONSTRAINT brigade_assignments_pkey PRIMARY KEY (id);


--
-- Name: brigade_members brigade_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_members
    ADD CONSTRAINT brigade_members_pkey PRIMARY KEY (brigade_id, employee_id);


--
-- Name: brigade_status_history brigade_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_status_history
    ADD CONSTRAINT brigade_status_history_pkey PRIMARY KEY (id);


--
-- Name: brigade_work_history brigade_work_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_work_history
    ADD CONSTRAINT brigade_work_history_pkey PRIMARY KEY (id);


--
-- Name: brigades brigades_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigades
    ADD CONSTRAINT brigades_name_key UNIQUE (name);


--
-- Name: brigades brigades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigades
    ADD CONSTRAINT brigades_pkey PRIMARY KEY (id);


--
-- Name: construction_sites construction_sites_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.construction_sites
    ADD CONSTRAINT construction_sites_name_key UNIQUE (name);


--
-- Name: construction_sites construction_sites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.construction_sites
    ADD CONSTRAINT construction_sites_pkey PRIMARY KEY (id);


--
-- Name: deliveries deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT deliveries_pkey PRIMARY KEY (id);


--
-- Name: delivery_items delivery_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_items
    ADD CONSTRAINT delivery_items_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- Name: equipment_types equipment_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_types
    ADD CONSTRAINT equipment_types_pkey PRIMARY KEY (id);


--
-- Name: equipment_work_history equipment_work_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_work_history
    ADD CONSTRAINT equipment_work_history_pkey PRIMARY KEY (id);


--
-- Name: managements managements_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.managements
    ADD CONSTRAINT managements_name_key UNIQUE (name);


--
-- Name: managements managements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.managements
    ADD CONSTRAINT managements_pkey PRIMARY KEY (id);


--
-- Name: material_plan material_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_plan
    ADD CONSTRAINT material_plan_pkey PRIMARY KEY (id);


--
-- Name: material_usage_items material_usage_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage_items
    ADD CONSTRAINT material_usage_items_pkey PRIMARY KEY (id);


--
-- Name: material_usage material_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage
    ADD CONSTRAINT material_usage_pkey PRIMARY KEY (id);


--
-- Name: material_usages material_usages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usages
    ADD CONSTRAINT material_usages_pkey PRIMARY KEY (id);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- Name: plan_materials plan_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_materials
    ADD CONSTRAINT plan_materials_pkey PRIMARY KEY (id);


--
-- Name: positions positions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positions
    ADD CONSTRAINT positions_pkey PRIMARY KEY (id);


--
-- Name: positions positions_title_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positions
    ADD CONSTRAINT positions_title_key UNIQUE (title);


--
-- Name: saved_queries saved_queries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_queries
    ADD CONSTRAINT saved_queries_pkey PRIMARY KEY (id);


--
-- Name: section_materials section_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_materials
    ADD CONSTRAINT section_materials_pkey PRIMARY KEY (id);


--
-- Name: section_work_plan section_work_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_work_plan
    ADD CONSTRAINT section_work_plan_pkey PRIMARY KEY (id);


--
-- Name: section_works section_works_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_works
    ADD CONSTRAINT section_works_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_name_key UNIQUE (name);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: units units_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_name_key UNIQUE (name);


--
-- Name: units units_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- Name: units units_short_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_short_name_key UNIQUE (short_name);


--
-- Name: brigade_assignments uq_active_assignment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_assignments
    ADD CONSTRAINT uq_active_assignment UNIQUE (brigade_id, section_id, assigned_at);


--
-- Name: material_usage uq_material_usage_section_material; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage
    ADD CONSTRAINT uq_material_usage_section_material UNIQUE (section_id, material_id);


--
-- Name: work_logs work_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs
    ADD CONSTRAINT work_logs_pkey PRIMARY KEY (id);


--
-- Name: work_plans work_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_plans
    ADD CONSTRAINT work_plans_pkey PRIMARY KEY (id);


--
-- Name: work_report_materials work_report_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_report_materials
    ADD CONSTRAINT work_report_materials_pkey PRIMARY KEY (id);


--
-- Name: work_reports work_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_reports
    ADD CONSTRAINT work_reports_pkey PRIMARY KEY (id);


--
-- Name: work_types work_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_types
    ADD CONSTRAINT work_types_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser_username_722f3555_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX accounts_customuser_username_722f3555_like ON public.accounts_keys USING btree (username varchar_pattern_ops);


--
-- Name: accounts_guestrequest_user_id_9b57bc70; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX accounts_guestrequest_user_id_9b57bc70 ON public.accounts_guestrequest USING btree (user_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: idx_assignments_brigade_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignments_brigade_active ON public.brigade_assignments USING btree (brigade_id, assigned_at, unassigned_at);


--
-- Name: idx_assignments_section; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignments_section ON public.brigade_assignments USING btree (section_id);


--
-- Name: idx_employees_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_category ON public.employees USING btree (category);


--
-- Name: idx_plan_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_dates ON public.section_work_plan USING btree (planned_start, planned_end);


--
-- Name: idx_plan_section_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_section_order ON public.section_work_plan USING btree (section_id, order_index);


--
-- Name: idx_sites_management; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sites_management ON public.construction_sites USING btree (management_id);


--
-- Name: idx_usage_section_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usage_section_date ON public.material_usages USING btree (section_id, usage_date);


--
-- Name: idx_work_logs_section_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_logs_section_date ON public.work_logs USING btree (section_id, actual_date);


--
-- Name: uq_active_brigade_once; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_active_brigade_once ON public.sections USING btree (brigade_id) WHERE ((brigade_id IS NOT NULL) AND (end_date IS NULL));


--
-- Name: material_usage_items trg_decrease_stock_on_usage; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_decrease_stock_on_usage AFTER INSERT ON public.material_usage_items FOR EACH ROW EXECUTE FUNCTION public.trg_decrease_stock_on_usage_fn();


--
-- Name: delivery_items trg_increase_stock_on_delivery; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_increase_stock_on_delivery AFTER INSERT ON public.delivery_items FOR EACH ROW EXECUTE FUNCTION public.trg_increase_stock_on_delivery_fn();


--
-- Name: brigades trg_log_brigade_status_change; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_log_brigade_status_change AFTER UPDATE ON public.brigades FOR EACH ROW EXECUTE FUNCTION public.trg_log_brigade_status_change_fn();


--
-- Name: sections trg_sections_status_aiud; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_sections_status_aiud AFTER INSERT OR DELETE OR UPDATE OF brigade_id, end_date ON public.sections FOR EACH ROW EXECUTE FUNCTION public.set_brigade_status_on_section_change();


--
-- Name: delivery_items trg_update_delivery_total; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_delivery_total AFTER INSERT OR UPDATE ON public.delivery_items FOR EACH ROW EXECUTE FUNCTION public.trg_update_delivery_total_fn();


--
-- Name: section_materials trg_update_total_cost; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_total_cost BEFORE INSERT OR UPDATE ON public.section_materials FOR EACH ROW EXECUTE FUNCTION public.update_total_cost();


--
-- Name: section_works trg_update_work_total_cost; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_work_total_cost BEFORE INSERT OR UPDATE ON public.section_works FOR EACH ROW EXECUTE FUNCTION public.update_work_total_cost();


--
-- Name: accounts_guestrequest accounts_guestreques_user_id_9b57bc70_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts_guestrequest
    ADD CONSTRAINT accounts_guestreques_user_id_9b57bc70_fk_accounts_ FOREIGN KEY (user_id) REFERENCES public.accounts_keys(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: brigade_assignments brigade_assignments_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_assignments
    ADD CONSTRAINT brigade_assignments_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE CASCADE;


--
-- Name: brigade_members brigade_members_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_members
    ADD CONSTRAINT brigade_members_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE CASCADE;


--
-- Name: brigade_members brigade_members_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_members
    ADD CONSTRAINT brigade_members_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: brigade_status_history brigade_status_history_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_status_history
    ADD CONSTRAINT brigade_status_history_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE CASCADE;


--
-- Name: brigade_status_history brigade_status_history_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_status_history
    ADD CONSTRAINT brigade_status_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: brigade_work_history brigade_work_history_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_work_history
    ADD CONSTRAINT brigade_work_history_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE CASCADE;


--
-- Name: brigade_work_history brigade_work_history_section_work_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigade_work_history
    ADD CONSTRAINT brigade_work_history_section_work_id_fkey FOREIGN KEY (section_work_id) REFERENCES public.section_works(id) ON DELETE CASCADE;


--
-- Name: brigades brigades_leader_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brigades
    ADD CONSTRAINT brigades_leader_id_fkey FOREIGN KEY (leader_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: construction_sites construction_sites_management_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.construction_sites
    ADD CONSTRAINT construction_sites_management_id_fkey FOREIGN KEY (management_id) REFERENCES public.managements(id) ON DELETE SET NULL;


--
-- Name: construction_sites construction_sites_responsible_engineer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.construction_sites
    ADD CONSTRAINT construction_sites_responsible_engineer_id_fkey FOREIGN KEY (responsible_engineer_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: deliveries deliveries_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT deliveries_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE SET NULL;


--
-- Name: deliveries deliveries_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT deliveries_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE RESTRICT;


--
-- Name: delivery_items delivery_items_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_items
    ADD CONSTRAINT delivery_items_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES public.deliveries(id) ON DELETE CASCADE;


--
-- Name: delivery_items delivery_items_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_items
    ADD CONSTRAINT delivery_items_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE RESTRICT;


--
-- Name: django_admin_log django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id);


--
-- Name: employees employees_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_position_id_fkey FOREIGN KEY (position_id) REFERENCES public.positions(id) ON DELETE RESTRICT;


--
-- Name: equipment equipment_assigned_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_assigned_site_id_fkey FOREIGN KEY (assigned_site_id) REFERENCES public.construction_sites(id) ON DELETE SET NULL;


--
-- Name: equipment_work_history equipment_work_history_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_work_history
    ADD CONSTRAINT equipment_work_history_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id) ON DELETE CASCADE;


--
-- Name: equipment_work_history equipment_work_history_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_work_history
    ADD CONSTRAINT equipment_work_history_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.construction_sites(id) ON DELETE CASCADE;


--
-- Name: employees fk_employees_position; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT fk_employees_position FOREIGN KEY (position_id) REFERENCES public.positions(id) ON DELETE RESTRICT;


--
-- Name: work_types fk_work_types_unit; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_types
    ADD CONSTRAINT fk_work_types_unit FOREIGN KEY (unit_id) REFERENCES public.units(id) ON DELETE SET NULL;


--
-- Name: managements managements_head_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.managements
    ADD CONSTRAINT managements_head_employee_id_fkey FOREIGN KEY (head_employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: material_plan material_plan_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_plan
    ADD CONSTRAINT material_plan_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: material_plan material_plan_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_plan
    ADD CONSTRAINT material_plan_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE CASCADE;


--
-- Name: material_usage_items material_usage_items_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage_items
    ADD CONSTRAINT material_usage_items_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE RESTRICT;


--
-- Name: material_usage_items material_usage_items_usage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage_items
    ADD CONSTRAINT material_usage_items_usage_id_fkey FOREIGN KEY (usage_id) REFERENCES public.material_usages(id) ON DELETE CASCADE;


--
-- Name: material_usage material_usage_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage
    ADD CONSTRAINT material_usage_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: material_usage material_usage_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usage
    ADD CONSTRAINT material_usage_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE CASCADE;


--
-- Name: material_usages material_usages_responsible_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_usages
    ADD CONSTRAINT material_usages_responsible_employee_id_fkey FOREIGN KEY (responsible_employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: materials materials_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE RESTRICT;


--
-- Name: materials materials_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.units(id) ON DELETE RESTRICT;


--
-- Name: plan_materials plan_materials_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_materials
    ADD CONSTRAINT plan_materials_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE RESTRICT;


--
-- Name: plan_materials plan_materials_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_materials
    ADD CONSTRAINT plan_materials_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.section_work_plan(id) ON DELETE CASCADE;


--
-- Name: section_materials section_materials_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_materials
    ADD CONSTRAINT section_materials_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: section_materials section_materials_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_materials
    ADD CONSTRAINT section_materials_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE CASCADE;


--
-- Name: section_work_plan section_work_plan_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_work_plan
    ADD CONSTRAINT section_work_plan_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.units(id) ON DELETE RESTRICT;


--
-- Name: section_work_plan section_work_plan_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_work_plan
    ADD CONSTRAINT section_work_plan_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id) ON DELETE RESTRICT;


--
-- Name: section_works section_works_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_works
    ADD CONSTRAINT section_works_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE CASCADE;


--
-- Name: section_works section_works_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_works
    ADD CONSTRAINT section_works_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id) ON DELETE CASCADE;


--
-- Name: sections sections_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE SET NULL;


--
-- Name: sections sections_chief_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_chief_id_fkey FOREIGN KEY (chief_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: sections sections_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.construction_sites(id) ON DELETE CASCADE;


--
-- Name: work_logs work_logs_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs
    ADD CONSTRAINT work_logs_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE SET NULL;


--
-- Name: work_logs work_logs_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs
    ADD CONSTRAINT work_logs_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.units(id) ON DELETE RESTRICT;


--
-- Name: work_logs work_logs_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs
    ADD CONSTRAINT work_logs_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id) ON DELETE RESTRICT;


--
-- Name: work_plans work_plans_brigade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_plans
    ADD CONSTRAINT work_plans_brigade_id_fkey FOREIGN KEY (brigade_id) REFERENCES public.brigades(id) ON DELETE SET NULL;


--
-- Name: work_plans work_plans_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_plans
    ADD CONSTRAINT work_plans_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.construction_sites(id) ON DELETE CASCADE;


--
-- Name: work_plans work_plans_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_plans
    ADD CONSTRAINT work_plans_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id) ON DELETE SET NULL;


--
-- Name: work_report_materials work_report_materials_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_report_materials
    ADD CONSTRAINT work_report_materials_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id);


--
-- Name: work_report_materials work_report_materials_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_report_materials
    ADD CONSTRAINT work_report_materials_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.work_reports(id) ON DELETE CASCADE;


--
-- Name: work_reports work_reports_work_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_reports
    ADD CONSTRAINT work_reports_work_plan_id_fkey FOREIGN KEY (work_plan_id) REFERENCES public.work_plans(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict hGOMGMKWBMofiMlgybVezRCLL1yKIFKGkNmmcfvcARqNkumuabUdeTkUctVIuAA

