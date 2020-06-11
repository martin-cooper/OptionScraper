CREATE TABLE IF NOT EXISTS ticker (
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(10) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS contract (
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(20) PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    type VARCHAR(4) NOT NULL,
    strike MONEY NOT NULL,
    expiry DATE,
    FOREIGN KEY (ticker) REFERENCES ticker (name)
);

CREATE TABLE IF NOT EXISTS data_point (
    id INT GENERATED ALWAYS AS IDENTITY,
    contract_name VARCHAR(20),
    high MONEY NOT NULL,
    low MONEY NOT NULL,
    open_price MONEY NOT NULL,
    close_price MONEY NOT NULL,
    volume INT NOT NULL,
    time_value TIMESTAMP NOT NULL,
    FOREIGN KEY (contract_name) REFERENCES contract (name)
);