-- Joomla Community Builder database alterations done.

drop table if exists newusers;
drop table if exists updatedusers;
create table newusers like jos_comprofiler;
create table updatedusers like jos_comprofiler;

-- Add new users to newusers table.
drop trigger if exists user_added;
create trigger user_added 
after insert on jos_comprofiler
    for each row
        replace into newusers 
        select new.*

-- Add updated users to updatedusers table.
drop trigger if exists user_updated;
create trigger user_updated
before update on jos_comprofiler
    for each row
        replace into updatedusers
        select new.*        
;


