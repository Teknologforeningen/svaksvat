The Backend
===========

.. toctree::
   :maxdepth: 2

   orm
   dbschema
   ldaplogin

The project uses SQLAlchemy for ORM (Object-Relational Mapping). The mapper
classes reside in the backend.orm module. The member __tablename__ gives the
name of the table in the database and "sequence_name" the name of the row in
the members_sequence table.

