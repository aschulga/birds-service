# birds-service
### Задание 1
> Записать в таблицу bird_colors_info информацию о том, сколько в базе птиц каждого цвета:
```sql
DELETE FROM bird_colors_info;
INSERT INTO bird_colors_info SELECT color, COUNT(color) FROM birds GROUP BY color;
```

> Cредняя длина тела:
```sql
SELECT ROUND(AVG(body_length)) as body_length_mean FROM birds;
```

> Медиана длин тела:
```sql
SELECT  
  ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY body_length)::numeric, 2) AS body_length_median
FROM birds;
```

> Мода длин тел:
```sql
SELECT array_agg(body_length) AS body_length_mode
FROM
  (SELECT body_length
   FROM birds
   GROUP BY body_length
   HAVING count(body_length) =
     (SELECT count_body_length
      FROM
        (SELECT body_length,
                COUNT(body_length) AS count_body_length
         FROM birds
         GROUP BY body_length) AS t1
      ORDER BY count_body_length DESC
      LIMIT 1))AS t2
```

> Средняя длина размаха крыльев:
```sql
SELECT ROUND(AVG(wingspan)) as wingspan_mean FROM birds;
```

> Медиана длин размаха крыльев:
```sql
SELECT  
  ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY wingspan)::numeric, 2) AS wingspan_median
FROM birds;
```

> Мода длин размаха крыльев:
```sql
SELECT array_agg(wingspan) AS wingspan_mode
FROM
  (SELECT wingspan
   FROM birds
   GROUP BY wingspan
   HAVING count(wingspan) =
     (SELECT count_wingspan
      FROM
        (SELECT wingspan,
                COUNT(wingspan) AS count_wingspan
         FROM birds
         GROUP BY wingspan) AS t1
      ORDER BY count_wingspan DESC
      LIMIT 1))AS t2
```

> Записать статистические данные в таблицу birds_stat
```sql
DELETE FROM birds_stat;
INSERT INTO birds_stat
VALUES (
	(SELECT ROUND(AVG(body_length)) AS body_length_mean FROM birds),
	(SELECT ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY body_length)::numeric, 2) AS body_length_median FROM birds), 
	(SELECT array_agg(body_length) AS body_length_mode FROM (
		SELECT body_length FROM birds GROUP BY body_length HAVING count(body_length) = (
			SELECT count_body_length FROM (
				SELECT body_length, COUNT(body_length) AS count_body_length FROM birds GROUP BY body_length) AS t1 ORDER BY count_body_length DESC LIMIT 1))AS t2),
	(SELECT ROUND(AVG(wingspan)) AS wingspan_mean FROM birds),
	(SELECT ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY wingspan)::numeric, 2) AS wingspan_median FROM birds),
	(SELECT array_agg(wingspan) AS wingspan_mode FROM (
		SELECT wingspan FROM birds GROUP BY wingspan HAVING count(wingspan) = (
			SELECT count_wingspan FROM (
				SELECT wingspan, COUNT(wingspan) AS count_wingspan FROM birds GROUP BY wingspan) AS t1 ORDER BY count_wingspan DESC LIMIT 1))AS t2)
);
```

### Задание 2
> Представлено в файле main.py
