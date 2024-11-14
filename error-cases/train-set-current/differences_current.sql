Line 43:
question:What are the names of all stations with a latitude smaller than 37.5?
error type: wrong key value error
golden truth: SELECT name FROM station WHERE lat  <  37.5	bike_1
prediction: SELECT name FROM station WHERE lat<5	bike_1


Line 44:
question: What are the names of stations that have latitude lower than 37.5?
error type: wrong key value error
golden truth: SELECT name FROM station WHERE lat  <  37.5	bike_1
prediction: SELECT name FROM station WHERE lat<5	bike_1


Line 63:
question: Which start station had the most trips starting from August? Give me the name and id of the station.
error type:
golden truth: SELECT start_station_name ,  start_station_id FROM trip WHERE start_date LIKE "8/%" GROUP BY start_station_name ORDER BY COUNT(*) DESC LIMIT 1	bike_1
prediction: station , trip	bike_1


Line 64:
question: What are the start stations name and id for the one that had the most start trips in August?
error type: miss LIKE clause
golden truth: SELECT start_station_name ,  start_station_id FROM trip WHERE start_date LIKE "8/%" GROUP BY start_station_name ORDER BY COUNT(*) DESC LIMIT 1	bike_1
prediction: SELECT start_station_name , start_station_id FROM trip WHERE start_date = (SELECT start_date FROM trip ORDER BY start_date ASC LIMIT 1) GROUP BY start_station_name ORDER BY COUNT( * ) DESC	bike_1


Line 79:
question: In zip code 94107, on which day neither Fog nor Rain was not observed?
error type: wrong column in WHERE
golden truth: SELECT date FROM weather WHERE zip_code  =  94107 AND EVENTS != "Fog" AND EVENTS != "Rain"	bike_1
prediction: SELECT date FROM weather WHERE zip_code = 94107 AND zip_code = 94107 AND events != 'fog'	bike_1


Line 80:
question: On which day has it neither been foggy nor rained in the zip code of 94107?
error type: what happened here...
golden truth: SELECT date FROM weather WHERE zip_code  =  94107 AND EVENTS != "Fog" AND EVENTS != "Rain"	bike_1
prediction: SELECT name FROM station WHERE city = 'San Jose' EXCEPT SELECT name FROM station WHERE city = 'San Jose'	bike_1


Line 103:
question: What are the dates in which the mean sea level pressure was between 30.3 and 31?
error type: fractional error
golden truth: SELECT date FROM weather WHERE mean_sea_level_pressure_inches BETWEEN 30.3 AND 31	bike_1
prediction: SELECT date FROM weather WHERE mean_sea_level_pressure_inches >= 3 AND mean_sea_level_pressure_inches <= 31	bike_1


Line 104:
question: What are the dates that have an average sea level pressure between 30.3 and 31?
error type: fractional error
golden truth: SELECT date FROM weather WHERE mean_sea_level_pressure_inches BETWEEN 30.3 AND 31	bike_1
prediction: SELECT date FROM weather WHERE mean_sea_level_pressure_inches >= 3 AND mean_sea_level_pressure_inches <= 31	bike_1


Line 105:
question: Find the day in which the difference between the max temperature and min temperature was the smallest. Also report the difference.
error type: calculation error(?)
golden truth: SELECT date ,  max_temperature_f - min_temperature_f FROM weather ORDER BY max_temperature_f - min_temperature_f LIMIT 1	bike_1
prediction: SELECT date , min_temperature_f FROM weather ORDER BY min_temperature_f ASC LIMIT 1	bike_1


Line 106:
question: What are the days that had the smallest temperature range, and what was that range?
error type:
golden truth: SELECT date ,  max_temperature_f - min_temperature_f FROM weather ORDER BY max_temperature_f - min_temperature_f LIMIT 1	bike_1
prediction: SELECT date , mean_temperature_f FROM weather ORDER BY mean_temperature_f ASC LIMIT 3	bike_1


Line 153:
question: Find the number of followers for each user.
error type: miss a GROUP BY clause
golden truth: SELECT count(*) FROM follows GROUP BY f1	twitter_1
prediction: SELECT COUNT( * ) FROM follows	twitter_1


Line 169:
question:A list of the top 10 countries by average invoice size. List country name and average invoice size.
error type: miss LIMIT clause
golden truth: SELECT billing_country ,  AVG(total) FROM invoices GROUP BY billing_country ORDER BY AVG(total) DESC LIMIT 10;	store_1
prediction: SELECT billing_country , AVG( total ) FROM invoices GROUP BY billing_country ORDER BY AVG( total ) DESC	store_1


Line 177:
question: List total amount of  invoice from Chicago, IL.
error type: wrong key value
golden truth: SELECT sum(total) FROM invoices WHERE billing_city  =  "Chicago" AND billing_state  =  "IL";	store_1
prediction: SELECT SUM( total ) FROM invoices WHERE billing_city = 'Chicago' AND billing_state = 'Chicago,'	store_1

Line 180:
question: List the number of invoices from the US, grouped by state.
error type: wrong key value
golden truth: SELECT billing_state ,  COUNT(*) FROM invoices WHERE billing_country  =  "USA" GROUP BY billing_state;	store_1
prediction: SELECT billing_state , COUNT( * ) FROM invoices WHERE billing_country = 'yes' GROUP BY billing_state	store_1


Line 181:
question: How many invoices were billed from each state?
error type: missing WHERE clause
golden truth: SELECT billing_state ,  COUNT(*) FROM invoices WHERE billing_country  =  "USA" GROUP BY billing_state;	store_1
prediction: SELECT billing_state , COUNT( * ) FROM invoices GROUP BY billing_state	store_1


Line 182:
question: List the state in the US with the most invoices.
error type: missing COUNT operation + wrong key value
golden truth: SELECT billing_state ,  COUNT(*) FROM invoices WHERE billing_country  =  "USA" GROUP BY billing_state ORDER BY COUNT(*) DESC LIMIT 1;	store_1
prediction: SELECT billing_state FROM invoices WHERE billing_country = 'billing_state' GROUP BY billing_state ORDER BY COUNT( * ) DESC LIMIT 1	store_1


Line 183:
question: What are the states with the most invoices?
error type: missing WHERE clause
golden truth: SELECT billing_state ,  COUNT(*) FROM invoices WHERE billing_country  =  "USA" GROUP BY billing_state ORDER BY COUNT(*) DESC LIMIT 1;	store_1
prediction: SELECT billing_state , COUNT( * ) FROM invoices GROUP BY billing_state ORDER BY COUNT( * ) DESC LIMIT 1	store_1


Line 184:
question: List the number of invoices and the invoice total from California.
error type: missing WHERE clause
golden truth: SELECT billing_state ,  COUNT(*) ,  SUM(total) FROM invoices WHERE billing_state  =  "CA";	store_1
prediction: SELECT billing_state , COUNT( * ) , SUM( total ) FROM invoices GROUP BY billing_state	store_1


Line 193:
question: How many customers in state of CA?
error type: wrong key value
golden truth: SELECT count(*) FROM customers WHERE state = "CA";	store_1
prediction: SELECT COUNT( * ) FROM customers WHERE state = 'California'	store_1


Line 222:
question: How much is the track Fast As a Shark?
error type: wrong column in SELECT 
golden truth: SELECT unit_price FROM tracks WHERE name = "Fast As a Shark";	store_1
prediction: SELECT bytes FROM tracks WHERE name = 'Fast As a Shark'	store_1


Line 382:
question: List each birth place along with the number of people from there.
error type: wrong column in SELECT + missing COUNT + missing GROUP BY clause 
golden truth: SELECT Birth_Place ,  COUNT(*) FROM people GROUP BY Birth_Place	body_builder
prediction: SELECT birth_date FROM people ORDER BY height ASC	body_builder


Line 477:
question: Find the minimum salary for the departments whose average salary is above the average payment of all instructors.
error type: 
golden truth: SELECT min(salary) ,  dept_name FROM instructor GROUP BY dept_name HAVING avg(salary)  >  (SELECT avg(salary) FROM instructor)	college_2
prediction: SELECT MIN( salary ) , dept_name FROM instructor WHERE salary<(SELECT AVG( salary ) FROM instructor) UNION SELECT MIN( salary ) , dept_name FROM instructor WHERE salary<(SELECT AVG( salary ) FROM instructor)	college_2


Line 478:
question: What is the lowest salary in departments with average salary greater than the overall average.
error type: wrong column in SELECT + missing avg operation
golden truth: SELECT min(salary) ,  dept_name FROM instructor GROUP BY dept_name HAVING avg(salary)  >  (SELECT avg(salary) FROM instructor)	college_2
prediction: SELECT MIN( salary ) , dept_name FROM instructor GROUP BY dept_name HAVING AVG( salary ) > (SELECT dept_name FROM instructor)	college_2


Line 487:
question: Find the names of all instructors in computer science department
error type: wrong key value
golden truth: SELECT name FROM instructor WHERE dept_name  =  'Comp. Sci.'	college_2
prediction: SELECT name FROM instructor WHERE dept_name = 'computer science'	college_2


Line 524:
question: List all church names in descending order of opening date.
error: 
golden truth: SELECT name FROM church ORDER BY open_date DESC	wedding
prediction: SELECT COUNT( * ) FROM church WHERE open_date<1850	wedding


Line 648:
question: Find the number of schools that have more than one donator whose donation amount is less than 8.5.
error:
golden truth: SELECT count(*) FROM (SELECT * FROM endowment WHERE amount  >  8.5 GROUP BY school_id HAVING count(*)  >  1)	school_finance
prediction: SELECT * FROM endowment WHERE amount > 5 GROUP BY school_id HAVING COUNT( * ) > 1	school_finance


Line 693:
golden truth: SELECT company ,  main_industry FROM company WHERE headquarters != 'USA'	gas_company
prediction: SELECT company , main_industry FROM company WHERE headquarters != 'United States'	gas_company

Line 756:
golden truth: SELECT DISTINCT name FROM races WHERE YEAR BETWEEN 2014 AND 2017	formula_1
prediction: SELECT DISTINCT date FROM races WHERE round BETWEEN 2014 and 2017	formula_1


Line 757:
golden truth: SELECT DISTINCT name FROM races WHERE YEAR BETWEEN 2014 AND 2017	formula_1
prediction: SELECT DISTINCT date FROM races WHERE round BETWEEN 2014 and 2017	formula_1


Line 764:
golden truth: SELECT DISTINCT name FROM races ORDER BY name DESC	formula_1
prediction: SELECT DISTINCT date FROM races ORDER BY date DESC	formula_1


Line 765:
golden truth: SELECT DISTINCT name FROM races ORDER BY name DESC	formula_1
prediction: SELECT DISTINCT date FROM races ORDER BY date DESC	formula_1


Line 766:
golden truth: SELECT name FROM races WHERE YEAR BETWEEN 2009 AND 2011	formula_1
prediction: SELECT date FROM races WHERE round BETWEEN 2009 and 2011	formula_1


Line 767:
golden truth: SELECT name FROM races WHERE YEAR BETWEEN 2009 AND 2011	formula_1
prediction: SELECT date FROM races WHERE round BETWEEN 2009 and 2011	formula_1


Line 768:
golden truth: SELECT name FROM races WHERE TIME > "12:00:00" OR TIME < "09:00:00"	formula_1
prediction: SELECT date FROM races WHERE date > '12:00:00' OR date<'09:00:00'	formula_1


Line 769:
golden truth: SELECT name FROM races WHERE TIME > "12:00:00" OR TIME < "09:00:00"	formula_1
prediction: SELECT date FROM races WHERE date > '12:00:00' OR date<'09:00:00'	formula_1

Line 844:
golden truth: SELECT count(*) FROM campuses WHERE county  =  "Los Angeles"	csu_1
prediction: SELECT COUNT( * ) FROM campuses WHERE county = 'LA'	csu_1

Line 893:
golden truth: SELECT Adults FROM Reservations WHERE CheckIn  =  "2010-10-23" AND FirstName  =  "CONRAD" AND LastName  =  "SELBIG";	inn_1
prediction: SELECT adults FROM reservations WHERE firstname = 'CONRAD' AND lastname = 'SELBIG' AND lastname = 'SELBIG'	inn_1


Line 894:
golden truth: SELECT Adults FROM Reservations WHERE CheckIn  =  "2010-10-23" AND FirstName  =  "CONRAD" AND LastName  =  "SELBIG";	inn_1
prediction: SELECT adults FROM reservations WHERE firstname = 'CONRAD' AND lastname = 'SELBIG' AND lastname = 'SELBIG'	inn_1


Line 895:
golden truth: SELECT Kids FROM Reservations WHERE CheckIn  =  "2010-09-21" AND FirstName  =  "DAMIEN" AND LastName  =  "TRACHSEL";	inn_1
prediction: SELECT kids FROM reservations WHERE firstname = 'DAMIEN' AND lastname = 'TRACHSEL' AND lastname = 'TRACHSEL'	inn_1


Line 896:
golden truth: SELECT Kids FROM Reservations WHERE CheckIn  =  "2010-09-21" AND FirstName  =  "DAMIEN" AND LastName  =  "TRACHSEL";	inn_1
prediction: SELECT kids FROM reservations WHERE firstname = 'DAMIEN' AND lastname = 'TRACHSEL' AND lastname = 'TRACHSEL'	inn_1

Line 961:
golden truth: SELECT count(*) FROM storm WHERE Number_Deaths  >  0	storm_record
prediction: SELECT COUNT( * ) FROM storm WHERE number_deaths = 1	storm_record


Line 962:
golden truth: SELECT count(*) FROM storm WHERE Number_Deaths  >  0	storm_record
prediction: SELECT COUNT( * ) FROM storm WHERE number_deaths > 1	storm_record


--number of differences: 44