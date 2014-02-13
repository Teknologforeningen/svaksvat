name 'svaksvatdev'
description 'Setups postgresql and ldap for SvakSvat'
run_list(
         'recipe[apt]',
         'recipe[postgresql::server]',
         'recipe[svaksvat]',
         #'recipe[openldap::server]',
         )


default_attributes :postgresql => {
  :config => {
    :listen_addresses => '*'
  },
  :password => {
    :postgres => 'svaksvat'
    },
  :pg_hba => [
              {:type => 'local', :db => 'all', :user => 'all', :addr => nil, :method => 'trust'},
              {:type => 'host', :db => 'all', :user => 'all', :addr => '0.0.0.0/0', :method => 'reject'},
              {:type => 'host', :db => 'all', :user => 'all', :addr => '127.0.0.1/32', :method => 'trust'},
              {:type => 'host', :db => 'all', :user => 'all', :addr => '::1/128', :method => 'trust'}
              ]
},
:openldap => {
  :basedn => 'dc=teknologforeningen,dc=fi',
  :manage_ssl => false
}
