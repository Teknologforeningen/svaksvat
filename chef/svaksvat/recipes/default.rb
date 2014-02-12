# -*- coding: utf-8 -*-
#
# Cookbook Name:: svaksvat
# Recipe:: default
#

include_recipe "database::postgresql"
postgresql_connection_info = {
  :host     => '127.0.0.1',
  :port     => node['postgresql']['config']['port'],
  :username => 'postgres',
  :password => node['postgresql']['password']['postgres']
}

# create a postgresql database
postgresql_database 'members' do
  connection    postgresql_connection_info
  action :create
end

memberspassword = "members"

user "members" do
  supports :manage_home => true
  gid "users"
  home "/home/members"
  shell "/bin/bash"
  password '$1$3uFrxahb$n3tYteXaoso3F4QPPIm11/' # members
end

# create members user
postgresql_database_user 'members' do
  connection    postgresql_connection_info
  password      memberspassword
  action        :create
end

# Grant all privileges on all tables in members db
postgresql_database_user 'members' do
  connection    postgresql_connection_info
  database_name 'members'
  privileges    [:all]
  action        :grant
end
