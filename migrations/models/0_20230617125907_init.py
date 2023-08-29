from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "partsfile" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid_field" UUID NOT NULL,
    "path" VARCHAR(200) NOT NULL,
    "size" BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS "filestatistic" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "files_count" INT NOT NULL,
    "downloads" INT NOT NULL,
    "date" DATE NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "paystatistic" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "year_count" INT NOT NULL,
    "month_count" INT NOT NULL,
    "week_count" INT NOT NULL,
    "date" DATE NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "storagestatistic" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "fill" INT NOT NULL,
    "date" DATE NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "userstatistic" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "users" INT NOT NULL,
    "new_subscribed" INT NOT NULL,
    "cancel_subscribed" INT NOT NULL,
    "date" DATE NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "tarif" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(160) NOT NULL,
    "price" INT NOT NULL,
    "period" VARCHAR(10) NOT NULL,
    "period_amount" INT NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "tarif"."period" IS 'month: Month\nweekend: Week\nyear: Year';
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(1024) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_verified" BOOL NOT NULL  DEFAULT False,
    "name" VARCHAR(80) NOT NULL,
    "phone" VARCHAR(20),
    "registered_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "expiration_date" TIMESTAMPTZ,
    "otp" INT,
    "auto_upload" BOOL NOT NULL  DEFAULT False,
    "date_of_send_otp" TIMESTAMPTZ,
    "downloads" INT NOT NULL  DEFAULT 0,
    "storage" BIGINT NOT NULL  DEFAULT 0,
    "last_upload" TIMESTAMPTZ,
    "status" VARCHAR(10),
    "tarif_id" INT  UNIQUE REFERENCES "tarif" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
COMMENT ON COLUMN "user"."status" IS 'premium: premium\nambassador: ambassador';
CREATE TABLE IF NOT EXISTS "changestatus" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "old_status" VARCHAR(10) NOT NULL,
    "new_status" VARCHAR(10) NOT NULL,
    "cause" TEXT NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "changestatus"."old_status" IS 'premium: premium\nambassador: ambassador';
COMMENT ON COLUMN "changestatus"."new_status" IS 'premium: premium\nambassador: ambassador';
CREATE TABLE IF NOT EXISTS "oauthaccount" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "oauth_name" VARCHAR(100) NOT NULL,
    "access_token" VARCHAR(1024) NOT NULL,
    "expires_at" INT,
    "refresh_token" VARCHAR(1024),
    "account_id" VARCHAR(255) NOT NULL,
    "account_email" VARCHAR(255) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_oauthaccoun_account_0f36a3" ON "oauthaccount" ("account_id");
CREATE TABLE IF NOT EXISTS "file" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "path" VARCHAR(200) NOT NULL,
    "description" TEXT NOT NULL,
    "upload_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_cart" BOOL NOT NULL  DEFAULT False,
    "cart_date" DATE,
    "size" BIGINT NOT NULL,
    "thumbnail" VARCHAR(100),
    "address" VARCHAR(200),
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "city" VARCHAR(100),
    "is_gallery" BOOL NOT NULL  DEFAULT False,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
