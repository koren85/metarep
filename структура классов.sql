-- auto-generated definition
create table sxclass_source
(
    ouid              integer not null
        primary key,
    name              varchar(255),
    description       varchar(255),
    map               varchar(255),
    datastore         varchar(255),
    a_sxdsncache      varchar(255),
    icon              integer,
    isvirtual         integer,
    secinner          integer,
    precache          integer,
    pullable          integer,
    titletemplate     varchar(255),
    java_class        varchar(255),
    a_abstract        integer,
    a_version         integer,
    a_sql_view        varchar,
    java_handler      varchar(255),
    a_notduplobj      integer,
    a_notrepl         integer,
    a_info            varchar,
    a_isdataintegrity integer,
    systemclass       integer,
    sec_link          integer,
    guid              varchar(255),
    ts                timestamp,
    a_issystem        integer,
    cr_owner          integer,
    a_createdate      timestamp,
    a_editor          integer,
    parent_ouid       integer,
    a_link_target     integer,
    a_log             text,
    a_event           integer,
    a_status_variance integer
);

alter table sxclass_source
    owner to tomcat;

create index idx_sxclass_source_ouid_event
    on sxclass_source (ouid, a_event);

create index idx_sxclass_source_event_0
    on sxclass_source (a_event)
    where (a_event = 0);

create index idx_sxclass_source_event
    on sxclass_source (a_event, ouid);

-- auto-generated definition
create table sxattr_grp_source
(
    ouid              integer not null
        primary key,
    systemclass       integer,
    guid              varchar(255),
    ts                timestamp,
    a_issystem        integer,
    cr_owner          integer,
    a_createdate      timestamp,
    a_editor          integer,
    title             varchar(255),
    a_viewtype        varchar(255),
    name              varchar(255),
    cls               integer,
    num               integer,
    forservice        integer,
    icon              integer,
    a_parent          integer,
    a_width           varchar(255),
    a_height          varchar(255),
    a_link_target     integer,
    a_log             text,
    a_event           integer,
    a_status_variance integer
);

alter table sxattr_grp_source
    owner to tomcat;

create index idx_sxattr_grp_source_cls_event
    on sxattr_grp_source (cls, a_event);

create index idx_sxattr_grp_source_cls
    on sxattr_grp_source (cls);

create index idx_sxattr_grp_source_event_1
    on sxattr_grp_source (a_event)
    where (a_event = 1);

create index idx_sxattr_grp_source_name
    on sxattr_grp_source (name);

create index idx_sxattr_grp_source_title
    on sxattr_grp_source (title);

create index idx_sxattr_grp_source_issystem
    on sxattr_grp_source (a_issystem);

create index idx_sxattr_grp_source_guid
    on sxattr_grp_source (guid)
    where (guid IS NOT NULL);

create index idx_sxattr_grp_source_createdate
    on sxattr_grp_source (a_createdate);

create index idx_sxattr_grp_source_ts
    on sxattr_grp_source (ts);

create index idx_sxattr_grp_source_parent
    on sxattr_grp_source (a_parent)
    where (a_parent IS NOT NULL);

create index idx_sxattr_grp_source_owner
    on sxattr_grp_source (cr_owner);

create index idx_sxattr_grp_source_editor
    on sxattr_grp_source (a_editor);

create index idx_sxattr_grp_source_num
    on sxattr_grp_source (num);

create index idx_sxattr_grp_source_cls_num
    on sxattr_grp_source (cls, num);

create index idx_sxattr_grp_source_cls_system
    on sxattr_grp_source (cls, a_issystem);

create index idx_sxattr_grp_source_name_lower
    on sxattr_grp_source (lower(name::text));

create index idx_sxattr_grp_source_title_lower
    on sxattr_grp_source (lower(title::text));



-- auto-generated definition
create table sxattr_source
(
    ouid               integer not null
        primary key,
    systemclass        integer,
    guid               varchar(255),
    ts                 timestamp,
    a_issystem         integer,
    cr_owner           integer,
    a_createdate       timestamp,
    a_editor           integer,
    name               varchar(255),
    description        text,
    ouiddatatype       integer,
    pkey               integer,
    defvalue           varchar(500),
    map                varchar(255),
    ouidsxclass        integer,
    visible            integer,
    inlist             integer,
    infiltr            integer,
    length             integer,
    istitle            integer,
    icon               integer,
    title              varchar(255),
    num                integer,
    informs            integer,
    agrp               integer,
    viewtype           integer,
    objquery           integer,
    read_only          integer,
    calculated         integer,
    ctrl_width         integer,
    near_label         integer,
    height             integer,
    ref_class          integer,
    ref_attr           integer,
    isordered          integer,
    select_sql         varchar(255),
    extendedfilter     integer,
    samerow            integer,
    isrepl             integer,
    iscrypt            integer,
    addlinksql         varchar(255),
    dellinksql         varchar(255),
    search_mode        integer,
    search_root        varchar(255),
    mandatory          integer,
    a_cascade          integer,
    a_isguid           integer,
    a_istimestamp      integer,
    isloading          integer,
    isservercrypt      integer,
    a_hierarchy        integer,
    a_autoinc          integer,
    a_class_descr      integer,
    a_aliases          varchar(255),
    a_indexed          integer,
    a_ext_list         integer,
    a_cascaderep       integer,
    a_viewlinkmn       integer,
    a_unique           integer,
    a_fornullval       varchar(255),
    a_isvirtual        integer,
    a_sort             varchar(255),
    a_sign             integer,
    a_hidegb           integer,
    a_hidecb           integer,
    a_hidedelb         integer,
    a_hideedtb         integer,
    isvaleuutitle      integer,
    a_history          varchar(255),
    a_symboliclinkview varchar(255),
    a_mask             varchar(255),
    a_isdiffbranch     integer,
    a_disabledublicate integer,
    a_isactualize      integer,
    columnfilter       integer,
    a_objcrit          text,
    a_link_target      integer,
    a_log              text,
    a_event            integer,
    a_status_variance  integer
);

alter table sxattr_source
    owner to tomcat;

create index idx_sxattr_source_class_event
    on sxattr_source (ouidsxclass, a_event);

create index idx_sxattr_source_class
    on sxattr_source (ouidsxclass);

create index idx_sxattr_source_event_1
    on sxattr_source (a_event)
    where (a_event = 1);

create index idx_sxattr_source_name
    on sxattr_source (name);

create index idx_sxattr_source_title
    on sxattr_source (title);

create index idx_sxattr_source_issystem
    on sxattr_source (a_issystem);

create index idx_sxattr_source_guid
    on sxattr_source (guid)
    where (guid IS NOT NULL);

create index idx_sxattr_source_createdate
    on sxattr_source (a_createdate);

create index idx_sxattr_source_ts
    on sxattr_source (ts);

create index idx_sxattr_source_ref_class
    on sxattr_source (ref_class)
    where (ref_class IS NOT NULL);

create index idx_sxattr_source_ref_attr
    on sxattr_source (ref_attr)
    where (ref_attr IS NOT NULL);

create index idx_sxattr_source_datatype
    on sxattr_source (ouiddatatype);

create index idx_sxattr_source_owner
    on sxattr_source (cr_owner);

create index idx_sxattr_source_editor
    on sxattr_source (a_editor);

create index idx_sxattr_source_visible
    on sxattr_source (visible);

create index idx_sxattr_source_inlist
    on sxattr_source (inlist);

create index idx_sxattr_source_num
    on sxattr_source (num);

create index idx_sxattr_source_istitle
    on sxattr_source (istitle)
    where (istitle = 1);

create index idx_sxattr_source_class_visible_num
    on sxattr_source (ouidsxclass, visible, num);

create index idx_sxattr_source_class_inlist_num
    on sxattr_source (ouidsxclass, inlist, num);

create index idx_sxattr_source_class_system
    on sxattr_source (ouidsxclass, a_issystem);

create index idx_sxattr_source_mandatory
    on sxattr_source (mandatory)
    where (mandatory = 1);

create index idx_sxattr_source_calculated
    on sxattr_source (calculated)
    where (calculated = 1);

create index idx_sxattr_source_readonly
    on sxattr_source (read_only)
    where (read_only = 1);

create index idx_sxattr_source_virtual
    on sxattr_source (a_isvirtual)
    where (a_isvirtual = 1);

create index idx_sxattr_source_name_pattern
    on sxattr_source using gin (name gin_trgm_ops);

create index idx_sxattr_source_title_pattern
    on sxattr_source using gin (title gin_trgm_ops);

create index idx_sxattr_source_name_lower
    on sxattr_source (lower(name::text));

create index idx_sxattr_source_title_lower
    on sxattr_source (lower(title::text));

