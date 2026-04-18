-- migrate:up
CREATE DATABASE IF NOT EXISTS fengqun_fms 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- migrate:down
DROP DATABASE IF EXISTS fengqun_fms;
