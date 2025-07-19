/* DuckDB */
select version();


from read_avro('src/testing_avro/users.avro');
