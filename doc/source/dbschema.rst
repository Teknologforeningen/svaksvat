Database schema
===============

The schema is quite straightforward except for one thing. An objectId is used
for primary keys. It's a hexadecimal string which is generated from the
members_sequence table. I don't know the intention behind this, but it's quite
easy to abstract away using backend.orm.numberToString.

.. code-block:: sql

    CREATE TABLE "AwardReceptionTable" (
        award_fld character varying(36),
        member_fld character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        received_fld timestamp without time zone,
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "AwardTable" (
        "awardType_fld" character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(60),
        description_fld character varying(255),
        abbreviation_fld character varying(10),
        photo_fld text,
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "AwardTypeTable" (
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(30),
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "ContactInformationTable" (
        member_fld character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        location_fld character varying(20),
        "streetAddress_fld" character varying(60),
        "postalCode_fld" character varying(20),
        city_fld character varying(30),
        country_fld character varying(30),
        phone_fld character varying(30),
        "cellPhone_fld" character varying(30),
        fax_fld character varying(30),
        url_fld character varying(60),
        email_fld character varying(50),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "DepartmentMembershipTable" (
        member_fld character varying(36),
        department_fld character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        "studyType_fld" character varying(40),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "DepartmentTable" (
        "departmentType_fld" character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(60),
        abbreviation_fld character varying(10),
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "DepartmentTypeTable" (
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(30),
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "GroupMembershipTable" (
        member_fld character varying(36),
        post_fld character varying(36),
        group_fld character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "GroupTable" (
        "groupType_fld" character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(40),
        description_fld character varying(255),
        abbreviation_fld character varying(10),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "GroupTypeTable" (
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(40),
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "MemberTable" (
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "givenNames_fld" character varying(100),
        "preferredName_fld" character varying(30),
        "surName_fld" character varying(40),
        "maidenName_fld" character varying(40),
        "nickName_fld" character varying(20),
        "birthDate_fld" timestamp without time zone,
        "studentId_fld" character varying(10),
        gender_fld integer,
        graduated_fld integer,
        occupation_fld character varying(30),
        photo_fld text,
        title_fld character varying(30),
        nationality_fld character varying(3),
        "primaryContactId_fld" character varying(33),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL,
        dead_fld integer
    );

    CREATE TABLE "MembershipTable" (
        member_fld character varying(36),
        "membershipType_fld" character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "MembershipTypeTable" (
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(30),
        abbreviation_fld character varying(10),
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "PostMembershipTable" (
        post_fld character varying(36),
        member_fld character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "PostTable" (
        "postType_fld" character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(30),
        description_fld character varying(255),
        abbreviation_fld character varying(10),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "PostTypeTable" (
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        name_fld character varying(30),
        description_fld character varying(255),
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE "PresenceTable" (
        member_fld character varying(36),
        created_fld timestamp without time zone,
        "createdBy_fld" character varying(36),
        modified_fld timestamp without time zone,
        "modifiedBy_fld" character varying(36),
        "startTime_fld" timestamp without time zone,
        "endTime_fld" timestamp without time zone,
        "eventStatus_fld" integer,
        "eventType_fld" integer,
        "atTF_fld" integer,
        "atTKY_fld" integer,
        "atHUT_fld" integer,
        notes_fld character varying(255),
        "objectId" character varying(36) NOT NULL
    );

    CREATE TABLE members_sequence (
        "next" numeric(19,0) NOT NULL,
        objectname character varying(64) NOT NULL
    );

    ALTER TABLE ONLY "AwardReceptionTable"
        ADD CONSTRAINT "AwardReceptionTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "AwardTable"
        ADD CONSTRAINT "AwardTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "AwardTypeTable"
        ADD CONSTRAINT "AwardTypeTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "ContactInformationTable"
        ADD CONSTRAINT "ContactInformationTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "DepartmentMembershipTable"
        ADD CONSTRAINT "DepartmentMembershipTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "DepartmentTable"
        ADD CONSTRAINT "DepartmentTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "DepartmentTypeTable"
        ADD CONSTRAINT "DepartmentTypeTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "GroupMembershipTable"
        ADD CONSTRAINT "GroupMembershipTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "GroupTable"
        ADD CONSTRAINT "GroupTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "GroupTypeTable"
        ADD CONSTRAINT "GroupTypeTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "MemberTable"
        ADD CONSTRAINT "MemberTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "MembershipTable"
        ADD CONSTRAINT "MembershipTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "MembershipTypeTable"
        ADD CONSTRAINT "MembershipTypeTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "PostMembershipTable"
        ADD CONSTRAINT "PostMembershipTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "PostTable"
        ADD CONSTRAINT "PostTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "PostTypeTable"
        ADD CONSTRAINT "PostTypeTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY "PresenceTable"
        ADD CONSTRAINT "PresenceTable_pkey" PRIMARY KEY ("objectId");

    ALTER TABLE ONLY members_sequence
        ADD CONSTRAINT members_sequence_pkey PRIMARY KEY (objectname);

    ALTER TABLE ONLY "AwardReceptionTable"
        ADD CONSTRAINT "AwardReceptionTable_award_fld_fkey" FOREIGN KEY (award_fld) REFERENCES "AwardTable"("objectId");

    ALTER TABLE ONLY "AwardReceptionTable"
        ADD CONSTRAINT "AwardReceptionTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

    ALTER TABLE ONLY "AwardTable"
        ADD CONSTRAINT "AwardTable_awardType_fld_fkey" FOREIGN KEY ("awardType_fld") REFERENCES "AwardTypeTable"("objectId");

    ALTER TABLE ONLY "ContactInformationTable"
        ADD CONSTRAINT "ContactInformationTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

    ALTER TABLE ONLY "DepartmentMembershipTable"
        ADD CONSTRAINT "DepartmentMembershipTable_department_fld_fkey" FOREIGN KEY (department_fld) REFERENCES "DepartmentTable"("objectId");

    ALTER TABLE ONLY "DepartmentMembershipTable"
        ADD CONSTRAINT "DepartmentMembershipTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

    ALTER TABLE ONLY "DepartmentTable"
    --

    ALTER TABLE ONLY "GroupMembershipTable"
        ADD CONSTRAINT "GroupMembershipTable_group_fld_fkey" FOREIGN KEY (group_fld) REFERENCES "GroupTable"("objectId");

    ALTER TABLE ONLY "GroupMembershipTable"
        ADD CONSTRAINT "GroupMembershipTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

    ALTER TABLE ONLY "GroupMembershipTable"
        ADD CONSTRAINT "GroupMembershipTable_post_fld_fkey" FOREIGN KEY (post_fld) REFERENCES "PostTable"("objectId");

    ALTER TABLE ONLY "GroupTable"
        ADD CONSTRAINT "GroupTable_groupType_fld_fkey" FOREIGN KEY ("groupType_fld") REFERENCES "GroupTypeTable"("objectId");

    ALTER TABLE ONLY "MembershipTable"
        ADD CONSTRAINT "MembershipTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

    ALTER TABLE ONLY "MembershipTable"
        ADD CONSTRAINT "MembershipTable_membershipType_fld_fkey" FOREIGN KEY ("membershipType_fld") REFERENCES "MembershipTypeTable"("objectId");

    ALTER TABLE ONLY "PostMembershipTable"
        ADD CONSTRAINT "PostMembershipTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

    ALTER TABLE ONLY "PostMembershipTable"
        ADD CONSTRAINT "PostMembershipTable_post_fld_fkey" FOREIGN KEY (post_fld) REFERENCES "PostTable"("objectId");

    ALTER TABLE ONLY "PostTable"
        ADD CONSTRAINT "PostTable_postType_fld_fkey" FOREIGN KEY ("postType_fld") REFERENCES "PostTypeTable"("objectId");

    ALTER TABLE ONLY "PresenceTable"
        ADD CONSTRAINT "PresenceTable_member_fld_fkey" FOREIGN KEY (member_fld) REFERENCES "MemberTable"("objectId");

