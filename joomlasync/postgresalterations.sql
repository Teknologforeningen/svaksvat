-- Members registry alterations done.

-- True if member wants the membershipmagazine Modulen.
alter table "MemberTable" add column subscribedToModulen_fld integer DEFAULT 1;

-- Last sync with Joomla Community Builder.
alter table "MemberTable" add column lastsync_fld timestamp without time zone DEFAULT 'January 1, 0001';

-- The LDAP username used as key when syncing with Joomla.
alter table "MemberTable" add column username_fld character varying(150) UNIQUE;
