from cx_Freeze import setup, Executable

setup(
        name = "simpleregister",
        version = "0.5",
        description = "",
        executables = [Executable(
		script="simpleregisterwin.pyw",
		base="Win32GUI"
		#includes=["psycopg2"]
		#, "sqlalchemy.dialects.postgresql.pypostgresql"]
		)])