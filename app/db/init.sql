DROP TABLE IF EXISTS test_table;

CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL
);

INSERT INTO test_table (name, address) VALUES ('John Doe', '123 Main St, Springfield');
commit;
