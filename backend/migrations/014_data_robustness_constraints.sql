ALTER TABLE records
DROP CONSTRAINT IF EXISTS records_concept_length_chk;

ALTER TABLE records
ADD CONSTRAINT records_concept_length_chk
    CHECK (char_length(concept) <= 40) NOT VALID;

ALTER TABLE records
DROP CONSTRAINT IF EXISTS records_comment_length_chk;

ALTER TABLE records
ADD CONSTRAINT records_comment_length_chk
    CHECK (comment IS NULL OR char_length(comment) <= 500) NOT VALID;

ALTER TABLE categories
DROP CONSTRAINT IF EXISTS categories_name_length_chk;

ALTER TABLE categories
ADD CONSTRAINT categories_name_length_chk
    CHECK (char_length(name) <= 40) NOT VALID;

ALTER TABLE categories
DROP CONSTRAINT IF EXISTS categories_description_length_chk;

ALTER TABLE categories
ADD CONSTRAINT categories_description_length_chk
    CHECK (description IS NULL OR char_length(description) <= 500) NOT VALID;

ALTER TABLE payment_methods
DROP CONSTRAINT IF EXISTS payment_methods_name_length_chk;

ALTER TABLE payment_methods
ADD CONSTRAINT payment_methods_name_length_chk
    CHECK (char_length(name) <= 40) NOT VALID;

ALTER TABLE banks
DROP CONSTRAINT IF EXISTS banks_name_length_chk;

ALTER TABLE banks
ADD CONSTRAINT banks_name_length_chk
    CHECK (char_length(name) <= 40) NOT VALID;

ALTER TABLE loans
DROP CONSTRAINT IF EXISTS loans_name_length_chk;

ALTER TABLE loans
ADD CONSTRAINT loans_name_length_chk
    CHECK (char_length(name) <= 40) NOT VALID;

ALTER TABLE loans
DROP CONSTRAINT IF EXISTS loans_description_length_chk;

ALTER TABLE loans
ADD CONSTRAINT loans_description_length_chk
    CHECK (description IS NULL OR char_length(description) <= 500) NOT VALID;

ALTER TABLE loan_usages
DROP CONSTRAINT IF EXISTS loan_usages_concept_length_chk;

ALTER TABLE loan_usages
ADD CONSTRAINT loan_usages_concept_length_chk
    CHECK (char_length(concept) <= 40) NOT VALID;

ALTER TABLE loan_usages
DROP CONSTRAINT IF EXISTS loan_usages_comment_length_chk;

ALTER TABLE loan_usages
ADD CONSTRAINT loan_usages_comment_length_chk
    CHECK (comment IS NULL OR char_length(comment) <= 500) NOT VALID;
