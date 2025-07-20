/* DuckDB */
select version();


from read_avro('src/testing_avro/users.avro');
from read_avro('src/testing_avro/models-*.avro');
