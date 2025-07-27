SELECT
  *
FROM table_2
WHERE
  1 = 1
  AND 30 > DATEDIFF(DATE, created_at, GETDATE())
  AND status = '{{ status }}'
